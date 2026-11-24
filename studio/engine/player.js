import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const GradeShader = {
  uniforms: {
    tDiffuse: { value: null }, sat: { value: 1 }, flash: { value: 0 }, ca: { value: 0.0012 }, time: { value: 0 },
    grain: { value: 0.035 }, tint: { value: new THREE.Color(1, 1, 1) }, glitch: { value: 0 }, vig: { value: 0.35 },
  },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
  fragmentShader: `
    uniform sampler2D tDiffuse; uniform float sat, flash, ca, time, grain, glitch, vig; uniform vec3 tint; varying vec2 vUv;
    float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
    void main(){
      vec2 uv = vUv;
      if (glitch > 0.0) {
        float band = floor(uv.y * 28.0);
        float r = h(vec2(band, floor(time * 24.0)));
        if (r > 0.55) uv.x += (r - 0.75) * 0.12 * glitch;
      }
      vec2 d = (uv - 0.5) * (ca + glitch * 0.02);
      vec3 c = vec3(texture2D(tDiffuse, uv + d).r, texture2D(tDiffuse, uv).g, texture2D(tDiffuse, uv - d).b);
      float l = dot(c, vec3(0.299, 0.587, 0.114));
      c = mix(vec3(l), c, sat) * tint;
      float v = smoothstep(0.85, 0.25, length(vUv - 0.5));
      c *= mix(1.0 - vig, 1.0, v);
      c = mix(c, vec3(1.0), flash);
      c += (h(vUv * vec2(1931.0, 1087.0) + fract(time * 7.13)) - 0.5) * grain;
      gl_FragColor = vec4(max(c, 0.0), 1.0);
    }`,
};

function chunk(words) {
  const chunks = [];
  let cur = [];
  for (const w of words) {
    cur.push(w);
    if (cur.length === 3 || /[.,?!:]$/.test(w.raw)) { chunks.push(cur); cur = []; }
  }
  if (cur.length) chunks.push(cur);
  return chunks.map((ws, i, all) => ({ words: ws, start: ws[0].start, end: Math.min(ws.at(-1).end + 0.3, all[i + 1]?.start ?? Infinity) }));
}

function drawCaptions(ctx, t, chunks, W, H) {
  const ch = chunks.find((c) => t >= c.start && t < c.end);
  if (!ch) return;
  const size = Math.round(Math.min(W, H) * (W > H ? 0.092 : 0.08));
  ctx.font = `900 ${size}px Inter`;
  ctx.textBaseline = 'middle';
  ctx.lineJoin = 'round';
  const gap = size * 0.26;
  const shown = ch.words.filter((w) => t >= w.start);
  const widths = shown.map((w) => ctx.measureText(w.text).width);
  let x = W / 2 - (widths.reduce((a, b) => a + b, 0) + gap * (widths.length - 1)) / 2;
  const y = H * (W > H ? 0.83 : 0.68);
  shown.forEach((w, i) => {
    const k = Math.min(1, (t - w.start) / 0.1);
    const s = 1 + 0.28 * (1 - k) ** 2;
    const active = i === shown.length - 1 && t < w.end + 0.15;
    ctx.save();
    ctx.translate(x + widths[i] / 2, y);
    ctx.scale(s, s);
    ctx.rotate(w.color ? -0.035 : 0);
    ctx.textAlign = 'center';
    ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowOffsetY = size * 0.08;
    ctx.lineWidth = size * 0.24; ctx.strokeStyle = '#0c0c0c';
    ctx.strokeText(w.text, 0, 0);
    ctx.shadowColor = 'transparent';
    ctx.fillStyle = w.color ?? (active ? '#ffd400' : '#ffffff');
    ctx.fillText(w.text, 0, 0);
    ctx.restore();
    x += widths[i] + gap;
  });
}

export async function createPlayer(episode, { width: W, height: H, words: rawWords, env = [], envRate = 60 }) {
  const gl = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  gl.setPixelRatio(1);
  gl.setSize(W, H, false);
  gl.outputColorSpace = THREE.SRGBColorSpace;

  const composer = new EffectComposer(gl, new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 4 }));
  composer.setPixelRatio(1);
  composer.setSize(W, H);
  const renderPass = new RenderPass(new THREE.Scene(), new THREE.PerspectiveCamera());
  const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), 0.85, 0.55, 1.08);
  const grade = new ShaderPass(GradeShader);
  composer.addPass(renderPass);
  composer.addPass(bloom);
  composer.addPass(grade);
  composer.addPass(new OutputPass());

  const out = document.getElementById('out');
  out.width = W; out.height = H;
  const ctx = out.getContext('2d');

  const words = rawWords.map((w, i) => {
    const color = episode.emph?.[i];
    const clean = w.w.replace(/[.,]$/, '');
    return { raw: w.w, text: color ? clean.toUpperCase() : clean, start: w.s, end: w.e, color };
  });
  const chunks = chunk(words);
  const duration = words.at(-1).end + (episode.tail ?? 1.2);
  const at = (i) => words[Math.min(i, words.length - 1)].start;

  const sets = episode.setup({ W, H });
  const shots = episode.shots.map((s, i) => ({ ...s, start: i === 0 ? 0 : Math.max(0, at(s.at) - 0.06) }));
  shots.forEach((s, i) => { s.end = shots[i + 1]?.start ?? duration; });

  const talkAt = (t) => {
    const v = env[Math.floor(t * envRate)] ?? 0;
    return v < 0.12 ? 0 : Math.min(1, Math.sqrt(v));
  };

  function renderAt(t) {
    const shot = shots.find((s) => t >= s.start && t < s.end) ?? shots.at(-1);
    const lt = t - shot.start;
    const set = sets[shot.set];
    const fx = { sat: 1, flash: 0, glitch: 0, tint: [1, 1, 1], shake: 0, bloom: 0.85, vig: 0.35 };
    const api = {
      t, lt, dur: shot.end - shot.start, fx, set, sets, duration,
      talk: talkAt(t),
      at, cue: (i) => at(i) - shot.start, since: (i) => t - at(i),
    };
    shot.update?.(lt, api);
    if (shot.start > 0) fx.flash = Math.max(fx.flash, 0.35 * Math.max(0, 1 - lt / 0.09));

    const cam = set.camera;
    const saved = cam.position.clone();
    if (fx.shake > 0) {
      const n = (a) => Math.sin(t * 61.3 + a) * 0.6 + Math.sin(t * 37.7 + a * 2.1) * 0.4;
      cam.position.x += n(0) * fx.shake * 0.12;
      cam.position.y += n(5) * fx.shake * 0.12;
    }
    renderPass.scene = set.scene;
    renderPass.camera = cam;
    bloom.strength = fx.bloom;
    const u = grade.uniforms;
    u.sat.value = fx.sat; u.flash.value = fx.flash; u.glitch.value = fx.glitch; u.time.value = t; u.vig.value = fx.vig;
    u.tint.value.setRGB(...fx.tint);
    composer.render();
    cam.position.copy(saved);

    ctx.drawImage(gl.domElement, 0, 0);
    episode.hud?.(ctx, t, { ...api, W, H, shot });
    drawCaptions(ctx, t, chunks, W, H);
  }

  const mix = episode.mix?.({ at, duration, shots });
  return { duration, renderAt, mix, shots: shots.map((s) => ({ set: s.set, start: s.start, end: s.end })) };
}
