const ease = (x) => { x = Math.min(1, Math.max(0, x)); return 1 - (1 - x) ** 3; };

function panel(ctx, x, y, w, h, r, border) {
  ctx.beginPath(); ctx.roundRect(x, y, w, h, r);
  ctx.fillStyle = 'rgba(12,12,18,0.82)'; ctx.fill();
  ctx.lineWidth = Math.max(3, h * 0.04); ctx.strokeStyle = border; ctx.stroke();
}

export function wallet(ctx, W, H, { value, label = 'WALLET', color = '#5dff7a', delta = '', deltaColor = '#5dff7a', deltaAge = 99, appear = 1, pulse = 0 }) {
  const s = H / 1080, k = ease(appear);
  if (k <= 0) return;
  ctx.save();
  ctx.translate(-380 * s * (1 - k), 0);
  const x = 40 * s, y = 36 * s, w = 340 * s, h = 128 * s;
  const sc = 1 + 0.08 * pulse;
  ctx.translate(x + w / 2, y + h / 2); ctx.scale(sc, sc); ctx.translate(-(x + w / 2), -(y + h / 2));
  panel(ctx, x, y, w, h, 22 * s, color);
  ctx.fillStyle = '#bfc3cc'; ctx.font = `800 ${24 * s}px Inter`; ctx.textBaseline = 'top'; ctx.textAlign = 'left';
  ctx.fillText(label, x + 24 * s, y + 18 * s);
  ctx.fillStyle = color; ctx.font = `900 ${60 * s}px Inter`;
  ctx.fillText(value, x + 22 * s, y + 48 * s);
  ctx.restore();
  if (delta && deltaAge < 1.4) {
    const a = 1 - Math.max(0, deltaAge - 0.9) / 0.5;
    ctx.save(); ctx.globalAlpha = a;
    ctx.font = `900 ${54 * s}px Inter`; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
    ctx.lineWidth = 12 * s; ctx.strokeStyle = '#0c0c0c'; ctx.lineJoin = 'round';
    const yy = y + h / 2 + 14 * s - 30 * s * ease(deltaAge / 0.4);
    ctx.strokeText(delta, x + w + 22 * s, yy); ctx.fillStyle = deltaColor; ctx.fillText(delta, x + w + 22 * s, yy);
    ctx.restore();
  }
}

export function gauge(ctx, cx, cy, r, v, { label = '', appear = 1 } = {}) {
  const k = ease(appear);
  if (k <= 0) return;
  ctx.save(); ctx.translate(cx, cy); ctx.scale(k, k);
  ctx.beginPath(); ctx.roundRect(-r * 1.25, -r * 1.2, r * 2.5, r * 1.75, r * 0.2);
  ctx.fillStyle = 'rgba(12,12,18,0.82)'; ctx.fill();
  const segs = ['#5dff7a', '#c6ff4d', '#ffd400', '#ff8a2a', '#ff2a2a'];
  segs.forEach((col, i) => {
    ctx.beginPath(); ctx.arc(0, 0, r, Math.PI + (i / 5) * Math.PI + 0.02, Math.PI + ((i + 1) / 5) * Math.PI - 0.02);
    ctx.lineWidth = r * 0.22; ctx.strokeStyle = col; ctx.stroke();
  });
  const a = Math.PI + Math.max(0, Math.min(1, v)) * Math.PI;
  ctx.lineWidth = r * 0.08; ctx.strokeStyle = '#fff'; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(Math.cos(a) * r * 0.85, Math.sin(a) * r * 0.85); ctx.stroke();
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(0, 0, r * 0.09, 0, Math.PI * 2); ctx.fill();
  ctx.font = `900 ${r * 0.22}px Inter`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(label, 0, r * 0.32);
  ctx.restore();
}

const spike = (x) => -0.15 * Math.exp(-(((x + 0.05) / 0.015) ** 2)) + Math.exp(-((x / 0.012) ** 2)) - 0.35 * Math.exp(-(((x - 0.04) / 0.015) ** 2)) + 0.18 * Math.exp(-(((x - 0.22) / 0.05) ** 2));

export function ecg(ctx, x, y, w, h, t, { bpm = (tt) => 70, gain = (tt) => 0.5, appear = 1, label = 'HEART RATE' } = {}) {
  const k = ease(appear);
  if (k <= 0) return;
  ctx.save(); ctx.globalAlpha = k;
  panel(ctx, x, y, w, h, h * 0.12, '#ff3b5c');
  ctx.save(); ctx.beginPath(); ctx.rect(x + 6, y + 6, w - 12, h - 12); ctx.clip();
  ctx.strokeStyle = 'rgba(255,59,92,0.15)'; ctx.lineWidth = 1;
  for (let gx = x; gx < x + w; gx += h / 6) { ctx.beginPath(); ctx.moveTo(gx, y); ctx.lineTo(gx, y + h); ctx.stroke(); }
  const win = 3, base = y + h * 0.62;
  ctx.beginPath();
  for (let px = 0; px <= w; px += 2) {
    const tt = t - (1 - px / w) * win;
    const period = 60 / bpm(tt);
    const ph = ((tt % period) + period) % period;
    const v = spike(ph - period * 0.3) * gain(tt);
    const py = base - v * h * 0.55;
    px ? ctx.lineTo(x + px, py) : ctx.moveTo(x + px, py);
  }
  ctx.strokeStyle = '#ff3b5c'; ctx.lineWidth = h * 0.035; ctx.shadowColor = '#ff3b5c'; ctx.shadowBlur = h * 0.08; ctx.stroke();
  ctx.restore();
  ctx.fillStyle = '#ffb3c0'; ctx.font = `800 ${h * 0.13}px Inter`; ctx.textAlign = 'left'; ctx.textBaseline = 'top';
  ctx.fillText(label, x + h * 0.12, y + h * 0.08);
  ctx.textAlign = 'right'; ctx.font = `900 ${h * 0.2}px Inter`; ctx.fillStyle = '#fff';
  ctx.fillText(`${Math.round(bpm(t))} BPM`, x + w - h * 0.12, y + h * 0.06);
  ctx.restore();
}

export function popText(ctx, W, H, text, age, { color = '#ff2a2a', size = 0.16, y = 0.4 } = {}) {
  if (age < 0) return;
  const k = Math.min(1, age / 0.18);
  const s = 1 + 0.6 * (1 - k) ** 2;
  ctx.save();
  ctx.translate(W / 2, H * y); ctx.scale(s, s); ctx.rotate(-0.05);
  ctx.font = `900 ${H * size}px Inter`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.lineJoin = 'round'; ctx.lineWidth = H * size * 0.22; ctx.strokeStyle = '#0c0c0c';
  ctx.strokeText(text, 0, 0); ctx.fillStyle = color; ctx.fillText(text, 0, 0);
  ctx.restore();
}

export function cite(ctx, W, H, text, appear = 1) {
  const k = ease(appear);
  if (k <= 0) return;
  const s = H / 1080;
  ctx.save(); ctx.globalAlpha = 0.9 * k;
  ctx.font = `700 ${24 * s}px Inter`; ctx.textAlign = 'left'; ctx.textBaseline = 'bottom';
  const w = ctx.measureText(text).width;
  ctx.fillStyle = 'rgba(12,12,18,0.75)';
  ctx.beginPath(); ctx.roundRect(36 * s, H - 84 * s, w + 36 * s, 46 * s, 10 * s); ctx.fill();
  ctx.fillStyle = '#e8e8ee'; ctx.fillText(text, 54 * s, H - 48 * s);
  ctx.restore();
}
