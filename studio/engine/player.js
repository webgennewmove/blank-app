import * as THREE from 'three';

export function timeWords(line, start) {
  const words = [];
  let t = start;
  for (const raw of line.split(/\s+/).filter(Boolean)) {
    const emph = raw.includes('*');
    const text = raw.replace(/\*/g, '');
    const digits = text.replace(/\D/g, '').length;
    const chars = digits ? digits * 4 + (text.includes('$') ? 7 : 0) : text.replace(/[^\w$]/g, '').length;
    const dur = 0.13 + 0.052 * chars;
    words.push({ text, emph, start: t, end: t + dur });
    t += dur + (/[.,?!:]$/.test(text) ? 0.28 : 0.02);
  }
  return words;
}

function chunk(words) {
  const chunks = [];
  let cur = [];
  for (const w of words) {
    cur.push(w);
    if (cur.length === 3 || /[.,?!:]$/.test(w.text)) { chunks.push(cur); cur = []; }
  }
  if (cur.length) chunks.push(cur);
  return chunks.map((ws, i, all) => ({
    words: ws,
    start: ws[0].start,
    end: Math.min(ws.at(-1).end + 0.35, all[i + 1]?.start ?? Infinity),
  }));
}

function drawCaptions(ctx, t, chunks, W, H) {
  const ch = chunks.find((c) => t >= c.start && t < c.end);
  if (!ch) return;
  const size = Math.round(Math.min(W, H) * (W > H ? 0.085 : 0.075));
  ctx.font = `900 ${size}px Inter`;
  ctx.textBaseline = 'middle';
  ctx.lineJoin = 'round';
  const gap = size * 0.28;
  const widths = ch.words.map((w) => ctx.measureText(w.text).width);
  const shown = widths.filter((_, i) => t >= ch.words[i].start);
  let x = W / 2 - (shown.reduce((a, b) => a + b, 0) + gap * (shown.length - 1)) / 2;
  const y = H * (W > H ? 0.84 : 0.7);
  ch.words.forEach((w, i) => {
    const visible = t >= w.start;
    if (visible) {
      const k = Math.min(1, (t - w.start) / 0.12);
      const s = 1 + 0.18 * (1 - k) ** 2;
      const active = t < (ch.words[i + 1]?.start ?? ch.end);
      ctx.save();
      ctx.translate(x + widths[i] / 2, y);
      ctx.scale(s, s);
      ctx.textAlign = 'center';
      ctx.lineWidth = size * 0.24;
      ctx.strokeStyle = '#0c0c0c';
      ctx.strokeText(w.text, 0, 0);
      ctx.fillStyle = w.emph ? '#5dff7a' : active ? '#ffd400' : '#ffffff';
      ctx.fillText(w.text, 0, 0);
      ctx.restore();
    }
    x += widths[i] + gap;
  });
}

function vignette(ctx, W, H) {
  const g = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.45, W / 2, H / 2, Math.max(W, H) * 0.75);
  g.addColorStop(0, 'rgba(0,0,0,0)');
  g.addColorStop(1, 'rgba(0,0,0,0.35)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
}

export async function createPlayer(episode, { width: W, height: H, audio = null }) {
  const gl = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  gl.setPixelRatio(1);
  gl.setSize(W, H, false);
  gl.outputColorSpace = THREE.SRGBColorSpace;

  const out = document.getElementById('out');
  out.width = W; out.height = H;
  const ctx = out.getContext('2d');

  const shots = [];
  let t0 = 0;
  episode.shots.forEach((s, i) => {
    const a0 = t0 + (s.lead ?? 0.3);
    const words = timeWords(s.line, a0);
    const clip = audio?.[i];
    if (clip) {
      const k = clip.speech / (words.at(-1).end - a0);
      for (const w of words) { w.start = a0 + (w.start - a0) * k; w.end = a0 + (w.end - a0) * k; }
    }
    const end = Math.max(words.at(-1).end, clip ? a0 + clip.dur : 0) + (s.tail ?? 0.5);
    shots.push({ ...s, start: t0, end, audioStart: a0, words, built: s.build({ W, H }) });
    t0 = end;
  });
  const allWords = shots.flatMap((s) => s.words);
  const chunks = chunk(allWords);

  function renderAt(t) {
    const shot = shots.find((s) => t >= s.start && t < s.end) ?? shots.at(-1);
    const lt = t - shot.start;
    const speaking = shot.words.some((w) => t >= w.start && t < w.end - 0.03);
    const { scene, camera, update } = shot.built;
    const cue = (i) => shot.words[Math.min(i, shot.words.length - 1)].start - shot.start;
    update(lt, { speaking, dur: shot.end - shot.start, t, cue });
    gl.render(scene, camera);
    ctx.drawImage(gl.domElement, 0, 0);
    vignette(ctx, W, H);
    drawCaptions(ctx, t, chunks, W, H);
    const flash = Math.max(0, 1 - lt / 0.12);
    if (shot.start > 0 && flash > 0) { ctx.fillStyle = `rgba(255,255,255,${flash * 0.5})`; ctx.fillRect(0, 0, W, H); }
  }

  return {
    duration: t0,
    renderAt,
    script: shots.map((s) => ({ start: s.start, end: s.end, audioStart: s.audioStart, line: s.line.replace(/\*/g, '') })),
    words: allWords,
  };
}
