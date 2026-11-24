import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

export const clamp01 = (x) => Math.min(1, Math.max(0, x));
export const ease = (x) => { x = clamp01(x); return x < 0.5 ? 2 * x * x : 1 - (-2 * x + 2) ** 2 / 2; };
export const lerp = (a, b, k) => a + (b - a) * k;
export const popIn = (x) => { x = clamp01(x); const s = 1.7; return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2; };

export function rng(seed) {
  return () => {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const gradientMap = (() => {
  const t = new THREE.DataTexture(new Uint8Array([110, 190, 255]), 3, 1, THREE.RedFormat);
  t.minFilter = t.magFilter = THREE.NearestFilter;
  t.needsUpdate = true;
  return t;
})();

const outlineMat = new THREE.ShaderMaterial({
  uniforms: { w: { value: 0.035 } },
  vertexShader: `uniform float w;
    void main() {
      vec4 mv = modelViewMatrix * vec4(position, 1.0);
      vec3 n = normalize(normalMatrix * normal);
      mv.xyz += n * w * clamp(-mv.z * 0.12, 0.6, 3.0);
      gl_Position = projectionMatrix * mv;
    }`,
  fragmentShader: `void main() { gl_FragColor = vec4(0.07, 0.07, 0.07, 1.0); }`,
  side: THREE.BackSide,
});

export function toon(geometry, color, { outline = true, map = null, emissive = 0x000000 } = {}) {
  const g = new THREE.Group();
  g.add(new THREE.Mesh(geometry, new THREE.MeshToonMaterial({ color, gradientMap, map, emissive })));
  if (outline) g.add(new THREE.Mesh(geometry, outlineMat));
  return g;
}

export const rbox = (w, h, d, r = 0.08) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2));

export function canvasTexture(w, h, draw) {
  const cv = document.createElement('canvas');
  cv.width = w; cv.height = h;
  const c = cv.getContext('2d');
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  tex.redraw = (...args) => { c.clearRect(0, 0, w, h); draw(c, w, h, ...args); tex.needsUpdate = true; };
  tex.redraw();
  return tex;
}

export function textPanel(w, h, draw, { pxPerUnit = 256 } = {}) {
  const tex = canvasTexture(Math.round(w * pxPerUnit), Math.round(h * pxPerUnit), draw);
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tex, transparent: true, toneMapped: false }));
  m.userData.tex = tex;
  return m;
}

export function makeStage({ W, H, sky = ['#7fd3ff', '#fff4d6'], ground = '#7ac06b', fog = null, fov = 35 }) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(fov, W / H, 0.1, 500);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8888aa, 1.4));
  const sun = new THREE.DirectionalLight(0xffffff, 2.0);
  sun.position.set(4, 10, 8);
  scene.add(sun);

  const skyMat = new THREE.ShaderMaterial({
    uniforms: { top: { value: new THREE.Color(sky[0]) }, bottom: { value: new THREE.Color(sky[1]) } },
    vertexShader: `varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
    fragmentShader: `uniform vec3 top; uniform vec3 bottom; varying vec3 vP;
      void main(){ float k = smoothstep(-0.05, 0.55, vP.y); gl_FragColor = vec4(mix(bottom, top, k), 1.0);
      #include <colorspace_fragment>
      }`,
    side: THREE.BackSide, depthWrite: false,
  });
  scene.add(new THREE.Mesh(new THREE.SphereGeometry(300, 32, 16), skyMat));

  const g = new THREE.Mesh(new THREE.CircleGeometry(250, 64), new THREE.MeshToonMaterial({ color: ground, gradientMap }));
  g.rotation.x = -Math.PI / 2;
  scene.add(g);
  if (fog) scene.fog = new THREE.Fog(fog[0], fog[1], fog[2]);
  return { scene, camera };
}

export function moveCamera(camera, { from, to, lookFrom, lookTo = lookFrom, k }) {
  const e = ease(k);
  camera.position.set(lerp(from[0], to[0], e), lerp(from[1], to[1], e), lerp(from[2], to[2], e));
  camera.lookAt(lerp(lookFrom[0], lookTo[0], e), lerp(lookFrom[1], lookTo[1], e), lerp(lookFrom[2], lookTo[2], e));
}

const coinGeo = new THREE.CylinderGeometry(0.28, 0.28, 0.07, 32);
export function coin() {
  const c = toon(coinGeo, '#ffc93c', { emissive: 0x332200 });
  return c;
}

export function coinStack(n, { jitter = 0.03, seed = 1 } = {}) {
  const r = rng(seed);
  const g = new THREE.Group();
  for (let i = 0; i < n; i++) {
    const c = coin();
    c.position.set((r() - 0.5) * jitter, 0.035 + i * 0.075, (r() - 0.5) * jitter);
    g.add(c);
  }
  return g;
}

export function palm(height = 3.2, seed = 1) {
  const r = rng(seed);
  const g = new THREE.Group();
  const lean = (r() - 0.5) * 0.3;
  const trunk = toon(new THREE.CylinderGeometry(0.09, 0.16, height, 10), '#a0703c');
  trunk.position.y = height / 2;
  trunk.rotation.z = lean;
  g.add(trunk);
  const top = new THREE.Vector3(-Math.sin(lean) * height, Math.cos(lean) * height, 0);
  for (let i = 0; i < 6; i++) {
    const leaf = toon(new THREE.SphereGeometry(0.5, 12, 8), '#2fae5a');
    leaf.scale.set(1.6, 0.18, 0.5);
    const a = (i / 6) * Math.PI * 2;
    leaf.position.set(top.x + Math.cos(a) * 0.7, top.y - 0.1, top.z + Math.sin(a) * 0.7);
    leaf.rotation.y = -a;
    leaf.rotation.z = -0.35;
    g.add(leaf);
  }
  return g;
}

export function sign(text, { w = 2.6, h = 1.1, color = '#ffffff', ink = '#151515', sub = '' } = {}) {
  const g = new THREE.Group();
  for (const x of [-w * 0.35, w * 0.35]) {
    const post = toon(new THREE.CylinderGeometry(0.06, 0.06, 1.4, 8), '#7a5230');
    post.position.set(x, 0.7, -0.05);
    g.add(post);
  }
  const board = toon(rbox(w, h, 0.12, 0.05), color);
  board.position.y = 1.4 + h / 2;
  g.add(board);
  const label = textPanel(w * 0.92, h * 0.85, (c, W, H) => {
    c.fillStyle = ink; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.font = `900 ${H * (sub ? 0.48 : 0.62)}px Inter`;
    c.fillText(text, W / 2, sub ? H * 0.38 : H / 2, W * 0.95);
    if (sub) { c.font = `800 ${H * 0.2}px Inter`; c.fillText(sub, W / 2, H * 0.8, W * 0.95); }
  });
  label.position.set(0, 1.4 + h / 2, 0.065);
  g.add(label);
  return g;
}

export function stamp(text = 'BANKRUPT', { w = 1.8 } = {}) {
  return textPanel(w, w * 0.32, (c, W, H) => {
    c.save(); c.translate(W / 2, H / 2); c.rotate(-0.12);
    c.strokeStyle = '#e0242b'; c.lineWidth = H * 0.08;
    c.strokeRect(-W * 0.45, -H * 0.36, W * 0.9, H * 0.72);
    c.fillStyle = '#e0242b'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.font = `900 ${H * 0.45}px Inter`;
    c.fillText(text, 0, H * 0.03, W * 0.82);
    c.restore();
  });
}
