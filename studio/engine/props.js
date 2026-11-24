import * as THREE from 'three';
import {
  toon, rbox, textPanel, canvasTexture, gradientMap, outlineMat, glowMat, neonText, bulbRow, rectPoints, coin, rng,
} from './world.js';

const K = '#151515';

function sym(c, name, x, y, s) {
  c.save(); c.translate(x, y); c.lineJoin = 'round'; c.lineWidth = s * 0.06; c.strokeStyle = K;
  if (name === '7') {
    c.font = `900 ${s * 0.9}px Inter`; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillStyle = '#e0242b'; c.strokeText('7', 0, s * 0.04); c.fillText('7', 0, s * 0.04);
  } else if (name === 'bar') {
    c.fillStyle = '#151515'; c.fillRect(-s * 0.38, -s * 0.18, s * 0.76, s * 0.36);
    c.font = `900 ${s * 0.28}px Inter`; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillStyle = '#fff'; c.fillText('BAR', 0, s * 0.02);
  } else if (name === 'cherry') {
    c.strokeStyle = '#2f8f3a'; c.lineWidth = s * 0.05;
    c.beginPath(); c.moveTo(-s * 0.18, s * 0.1); c.quadraticCurveTo(-s * 0.05, -s * 0.3, s * 0.12, -s * 0.36); c.stroke();
    c.beginPath(); c.moveTo(s * 0.2, s * 0.1); c.quadraticCurveTo(s * 0.15, -s * 0.2, s * 0.12, -s * 0.36); c.stroke();
    c.strokeStyle = K; c.lineWidth = s * 0.05;
    for (const cx of [-s * 0.18, s * 0.2]) { c.fillStyle = '#e0242b'; c.beginPath(); c.arc(cx, s * 0.18, s * 0.17, 0, Math.PI * 2); c.fill(); c.stroke(); }
  } else if (name === 'lemon') {
    c.fillStyle = '#ffd400'; c.beginPath(); c.ellipse(0, 0, s * 0.34, s * 0.24, 0, 0, Math.PI * 2); c.fill(); c.stroke();
  } else if (name === 'eye') {
    c.fillStyle = '#fff'; c.beginPath(); c.ellipse(0, 0, s * 0.38, s * 0.22, 0, 0, Math.PI * 2); c.fill(); c.stroke();
    c.fillStyle = '#e0242b'; c.beginPath(); c.arc(0, 0, s * 0.14, 0, Math.PI * 2); c.fill();
    c.fillStyle = K; c.beginPath(); c.ellipse(0, 0, s * 0.04, s * 0.12, 0, 0, Math.PI * 2); c.fill();
  }
  c.restore();
}

const REEL = ['7', 'cherry', 'bar', 'lemon', '7', 'lemon', 'cherry', 'bar'];

export function slotMachine({ body = '#c81e3a', trim = '#ffcc33', screen = true } = {}) {
  const g = new THREE.Group();
  const cab = toon(rbox(1.6, 2.6, 1.0, 0.12), body); cab.position.y = 1.3; g.add(cab);
  const top = toon(rbox(1.75, 0.55, 1.08, 0.12), trim); top.position.y = 2.8; g.add(top);
  const sign = neonText('777', { h: 0.42, color: '#ffe066', k: 2.2 }); sign.position.set(0, 2.8, 0.56); g.add(sign);
  const bezel = toon(rbox(1.42, 0.98, 0.06, 0.04), '#1b1b1b'); bezel.position.set(0, 1.75, 0.5); g.add(bezel);
  const tray = toon(rbox(1.2, 0.22, 0.45, 0.05), '#9aa0a8'); tray.position.set(0, 0.6, 0.48); g.add(tray);
  const arm = toon(new THREE.CylinderGeometry(0.04, 0.04, 0.9, 10), '#c9ccd1'); arm.position.set(0.95, 2.05, 0.1); g.add(arm);
  const knob = toon(new THREE.SphereGeometry(0.13, 16, 12), '#e0242b'); knob.position.set(0.95, 2.55, 0.1); g.add(knob);
  const bulbs = bulbRow(rectPoints(1.5, 1.06, 0.15), { size: 0.04, k: 2.0 }); bulbs.position.set(0, 1.75, 0.54); g.add(bulbs);

  let key = '';
  const state = { reels: [0, 2, 4], bet: '', win: '', eyes: false };
  const tex = canvasTexture(512, 330, (c, W, H) => {
    c.fillStyle = '#fffaf0'; c.fillRect(0, 0, W, H);
    const rh = H * 0.72, cw = W / 3;
    for (let r = 0; r < 3; r++) {
      c.save(); c.beginPath(); c.rect(r * cw + 6, 6, cw - 12, rh - 12); c.clip();
      const o = state.reels[r];
      const i0 = Math.floor(o), f = o - i0;
      for (let k = -1; k <= 1; k++) {
        const name = state.eyes ? 'eye' : REEL[(((i0 + k) % REEL.length) + REEL.length) % REEL.length];
        sym(c, name, r * cw + cw / 2, rh / 2 + (k - f) * rh * 0.8, rh * 0.62);
      }
      c.restore();
      c.strokeStyle = K; c.lineWidth = 6; c.strokeRect(r * cw + 6, 6, cw - 12, rh - 12);
    }
    c.fillStyle = '#151515'; c.fillRect(0, rh, W, H - rh);
    c.font = `900 ${H * 0.13}px Inter`; c.textBaseline = 'middle';
    c.textAlign = 'left'; c.fillStyle = '#ff5a5a'; c.fillText(state.bet && `BET ${state.bet}`, 18, rh + (H - rh) / 2);
    c.textAlign = 'right'; c.fillStyle = '#5dff7a'; c.fillText(state.win && `WIN ${state.win}`, W - 18, rh + (H - rh) / 2);
  });
  if (screen) {
    const scr = new THREE.Mesh(new THREE.PlaneGeometry(1.3, 0.84), new THREE.MeshBasicMaterial({ map: tex, color: new THREE.Color(0.92, 0.92, 0.92), toneMapped: false }));
    scr.position.set(0, 1.75, 0.535);
    g.add(scr);
  }
  g.userData = {
    bulbs, sign, knob, arm,
    set(next) {
      Object.assign(state, next);
      const k = JSON.stringify(state.reels.map((v) => v.toFixed(2))) + state.bet + state.win + state.eyes;
      if (k !== key) { key = k; tex.redraw(); }
    },
  };
  return g;
}

export function iconPanel(size, draw) {
  return textPanel(size, size, draw, { pxPerUnit: 300 });
}

export const drawClover = (c, W, H) => {
  c.lineWidth = W * 0.03; c.strokeStyle = K; c.fillStyle = '#2fbf5a';
  c.beginPath(); c.moveTo(W * 0.5, H * 0.52); c.quadraticCurveTo(W * 0.56, H * 0.8, W * 0.66, H * 0.92); c.stroke();
  for (let i = 0; i < 4; i++) {
    c.save(); c.translate(W / 2, H * 0.45); c.rotate(i * Math.PI / 2 + Math.PI / 4);
    c.beginPath(); c.moveTo(0, 0);
    c.bezierCurveTo(-W * 0.22, -H * 0.12, -W * 0.16, -H * 0.36, 0, -H * 0.24);
    c.bezierCurveTo(W * 0.16, -H * 0.36, W * 0.22, -H * 0.12, 0, 0);
    c.fill(); c.stroke(); c.restore();
  }
};

export const drawX = (c, W, H) => {
  for (const [col, w] of [[K, W * 0.2], ['#ff2a2a', W * 0.13]]) {
    c.strokeStyle = col; c.lineWidth = w; c.lineCap = 'round';
    c.beginPath(); c.moveTo(W * 0.18, H * 0.18); c.lineTo(W * 0.82, H * 0.82); c.moveTo(W * 0.82, H * 0.18); c.lineTo(W * 0.18, H * 0.82); c.stroke();
  }
};

export function brainPanel() {
  const r = rng(9);
  const lobes = Array.from({ length: 14 }, () => [0.25 + r() * 0.5, 0.25 + r() * 0.35, 0.09 + r() * 0.06]);
  return textPanel(2.4, 2.4, (c, W, H, hacked = false) => {
    c.lineWidth = W * 0.022; c.strokeStyle = K;
    c.fillStyle = '#ff8fb1';
    for (const [x, y, rr] of lobes) { c.beginPath(); c.arc(x * W, y * H, rr * W, 0, Math.PI * 2); c.fill(); }
    c.strokeStyle = '#c2557a'; for (const [x, y, rr] of lobes) { c.beginPath(); c.arc(x * W, y * H, rr * W * 0.7, Math.PI * 1.15, Math.PI * 1.85); c.stroke(); }
    c.strokeStyle = K;
    c.beginPath(); c.moveTo(W * 0.5, H * 0.2); c.bezierCurveTo(W * 0.45, H * 0.35, W * 0.55, H * 0.45, W * 0.5, H * 0.62); c.stroke();
    c.fillStyle = '#e0242b'; c.beginPath(); c.arc(W * 0.72, H * 0.24, W * 0.09, 0, Math.PI * 2); c.fill(); c.stroke();
    c.fillStyle = '#fff'; for (let i = 0; i < 6; i++) { c.save(); c.translate(W * 0.72, H * 0.24); c.rotate(i * Math.PI / 3); c.fillRect(-W * 0.012, -W * 0.088, W * 0.024, W * 0.03); c.restore(); }
    if (hacked) {
      c.save(); c.translate(W / 2, H * 0.83); c.rotate(-0.08);
      c.font = `900 ${H * 0.17}px Inter`; c.textAlign = 'center'; c.textBaseline = 'middle';
      c.lineWidth = H * 0.03; c.strokeText('HACKED', 0, 0); c.fillStyle = '#ff2a2a'; c.fillText('HACKED', 0, 0);
      c.restore();
    }
  });
}

export function clockPanel(size = 2.6) {
  return textPanel(size, size * 1.35, (c, W, H, hour = 0, minute = 0, melt = 0) => {
    const cx = W / 2, cy = W / 2, R = W * 0.42;
    const pt = (a, rr) => {
      const x = Math.cos(a) * rr, y = Math.sin(a) * rr;
      const s = Math.max(0, Math.sin(a));
      return [cx + x, cy + y + melt * R * 1.1 * s * s * (1 + 0.35 * Math.sin(a * 7)) * (rr / R)];
    };
    c.lineJoin = 'round';
    for (const [rr, fill, lw] of [[R, '#fffaf0', W * 0.04]]) {
      c.beginPath();
      for (let i = 0; i <= 120; i++) { const [x, y] = pt((i / 120) * Math.PI * 2, rr); i ? c.lineTo(x, y) : c.moveTo(x, y); }
      c.closePath(); c.fillStyle = fill; c.fill(); c.lineWidth = lw; c.strokeStyle = K; c.stroke();
    }
    c.lineWidth = W * 0.02;
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * Math.PI * 2;
      const [x1, y1] = pt(a, R * 0.82), [x2, y2] = pt(a, R * 0.94);
      c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2, y2); c.stroke();
    }
    const hand = (ang, len, w, col) => {
      const a = ang - Math.PI / 2;
      c.strokeStyle = col; c.lineWidth = w; c.lineCap = 'round';
      c.beginPath(); c.moveTo(cx, cy);
      for (let i = 1; i <= 10; i++) { const [x, y] = pt(a, (len * i) / 10); c.lineTo(x, y); }
      c.stroke();
    };
    hand(hour, R * 0.5, W * 0.045, K);
    hand(minute, R * 0.78, W * 0.03, '#e0242b');
    c.fillStyle = K; c.beginPath(); c.arc(cx, cy, W * 0.04, 0, Math.PI * 2); c.fill();
  });
}

export function windowPanel() {
  return textPanel(2.2, 1.8, (c, W, H) => {
    c.fillStyle = '#1b2a4a'; c.fillRect(W * 0.05, H * 0.05, W * 0.9, H * 0.9);
    c.lineWidth = W * 0.03; c.strokeStyle = K; c.strokeRect(W * 0.05, H * 0.05, W * 0.9, H * 0.9);
    c.fillStyle = '#a0703c';
    for (const [y, rot] of [[0.3, -0.12], [0.55, 0.1], [0.78, -0.06]]) {
      c.save(); c.translate(W / 2, H * y); c.rotate(rot);
      c.fillRect(-W * 0.5, -H * 0.08, W, H * 0.16); c.strokeRect(-W * 0.5, -H * 0.08, W, H * 0.16);
      c.restore();
    }
  });
}

export function ghostClockPanel() {
  return textPanel(1.8, 1.8, (c, W, H) => {
    c.setLineDash([W * 0.06, W * 0.04]); c.lineWidth = W * 0.035; c.strokeStyle = 'rgba(255,255,255,0.75)';
    c.beginPath(); c.arc(W / 2, H / 2, W * 0.4, 0, Math.PI * 2); c.stroke();
    c.setLineDash([]); c.font = `900 ${H * 0.4}px Inter`; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillStyle = 'rgba(255,255,255,0.75)'; c.fillText('?', W / 2, H / 2);
  });
}

export function bill() {
  const g = new THREE.Group();
  const base = toon(rbox(1.5, 0.04, 0.68, 0.02), '#6fbf73'); g.add(base);
  const face = textPanel(1.44, 0.62, (c, W, H) => {
    c.fillStyle = '#c9ecc0'; c.fillRect(0, 0, W, H);
    c.strokeStyle = '#2f7a3a'; c.lineWidth = H * 0.05; c.strokeRect(H * 0.06, H * 0.06, W - H * 0.12, H - H * 0.12);
    c.fillStyle = '#9fd49a'; c.beginPath(); c.ellipse(W / 2, H / 2, H * 0.26, H * 0.32, 0, 0, Math.PI * 2); c.fill();
    c.fillStyle = '#2f7a3a'; c.font = `900 ${H * 0.32}px Inter`; c.textBaseline = 'middle';
    c.textAlign = 'left'; c.fillText('100', H * 0.15, H * 0.3);
    c.textAlign = 'right'; c.fillText('100', W - H * 0.15, H * 0.72);
    c.textAlign = 'center'; c.font = `900 ${H * 0.36}px Inter`; c.fillText('$', W / 2, H * 0.52);
  });
  face.rotation.x = -Math.PI / 2; face.position.y = 0.025; g.add(face);
  return g;
}

const chipGeo = new THREE.CylinderGeometry(0.38, 0.38, 0.09, 40);
export function chip(color = '#d6273a') {
  const tex = canvasTexture(256, 256, (c, W, H) => {
    c.fillStyle = color; c.beginPath(); c.arc(W / 2, H / 2, W / 2, 0, Math.PI * 2); c.fill();
    c.fillStyle = '#fff';
    for (let i = 0; i < 6; i++) { c.save(); c.translate(W / 2, H / 2); c.rotate((i * Math.PI) / 3); c.fillRect(-W * 0.06, -W * 0.5, W * 0.12, W * 0.16); c.restore(); }
    c.strokeStyle = '#fff'; c.lineWidth = W * 0.025; c.setLineDash([W * 0.04, W * 0.03]);
    c.beginPath(); c.arc(W / 2, H / 2, W * 0.28, 0, Math.PI * 2); c.stroke();
    c.setLineDash([]); c.fillStyle = '#fff'; c.font = `900 ${W * 0.26}px Inter`; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText('$', W / 2, H / 2 + W * 0.01);
  });
  const side = new THREE.MeshToonMaterial({ color, gradientMap });
  const top = new THREE.MeshToonMaterial({ map: tex, gradientMap });
  const g = new THREE.Group();
  g.add(new THREE.Mesh(chipGeo, [side, top, top]));
  g.add(new THREE.Mesh(chipGeo, outlineMat));
  return g;
}

export function chipStack(n, color, seed = 1) {
  const r = rng(seed);
  const g = new THREE.Group();
  for (let i = 0; i < n; i++) {
    const c = chip(color);
    c.position.set((r() - 0.5) * 0.04, 0.045 + i * 0.095, (r() - 0.5) * 0.04);
    c.rotation.y = r() * 6;
    g.add(c);
  }
  return g;
}

export function pokerTable() {
  const g = new THREE.Group();
  const rim = toon(rbox(6.4, 0.2, 3.5, 0.1), '#6b3a1e'); rim.position.y = 1.0; g.add(rim);
  const felt = toon(rbox(6.0, 0.08, 3.1, 0.04), '#1f8a4c', { outline: false }); felt.position.y = 1.1; g.add(felt);
  for (const [x, z] of [[-2.6, -1.2], [2.6, -1.2], [-2.6, 1.2], [2.6, 1.2]]) {
    const leg = toon(new THREE.CylinderGeometry(0.1, 0.1, 1.0, 10), '#4a2814'); leg.position.set(x, 0.5, z); g.add(leg);
  }
  return g;
}

export function grouchoPanel() {
  return textPanel(1.4, 0.9, (c, W, H) => {
    c.lineWidth = W * 0.025; c.strokeStyle = K; c.lineJoin = 'round';
    c.fillStyle = K;
    for (const x of [0.3, 0.7]) { c.beginPath(); c.ellipse(W * x, H * 0.12, W * 0.13, H * 0.06, x < 0.5 ? 0.15 : -0.15, 0, Math.PI * 2); c.fill(); }
    for (const x of [0.3, 0.7]) { c.fillStyle = 'rgba(200,230,255,0.5)'; c.beginPath(); c.arc(W * x, H * 0.33, W * 0.14, 0, Math.PI * 2); c.fill(); c.stroke(); }
    c.beginPath(); c.moveTo(W * 0.44, H * 0.33); c.quadraticCurveTo(W * 0.5, H * 0.26, W * 0.56, H * 0.33); c.stroke();
    c.fillStyle = '#f4a6a0'; c.beginPath(); c.ellipse(W * 0.5, H * 0.56, W * 0.09, H * 0.17, 0, 0, Math.PI * 2); c.fill(); c.stroke();
    c.fillStyle = K;
    c.beginPath(); c.moveTo(W * 0.24, H * 0.82); c.quadraticCurveTo(W * 0.5, H * 0.6, W * 0.76, H * 0.82); c.quadraticCurveTo(W * 0.5, H * 0.74, W * 0.24, H * 0.82); c.fill();
  });
}

export function noteIcon() {
  return textPanel(0.5, 0.6, (c, W, H) => {
    c.fillStyle = '#ffe066'; c.strokeStyle = K; c.lineWidth = W * 0.06;
    c.beginPath(); c.ellipse(W * 0.32, H * 0.78, W * 0.2, H * 0.12, -0.4, 0, Math.PI * 2); c.fill(); c.stroke();
    c.fillRect(W * 0.48, H * 0.12, W * 0.08, H * 0.66); c.strokeRect(W * 0.48, H * 0.12, W * 0.08, H * 0.66);
    c.beginPath(); c.moveTo(W * 0.56, H * 0.12); c.quadraticCurveTo(W * 0.95, H * 0.25, W * 0.82, H * 0.5); c.quadraticCurveTo(W * 0.8, H * 0.3, W * 0.56, H * 0.32); c.fill(); c.stroke();
  });
}

export function mouseTrap() {
  const g = new THREE.Group();
  const base = toon(rbox(1.8, 0.12, 0.9, 0.04), '#c9955a'); base.position.y = 0.06; g.add(base);
  const plate = toon(rbox(0.45, 0.04, 0.35, 0.02), '#9aa0a8'); plate.position.set(0.55, 0.14, 0); g.add(plate);
  const pivot = new THREE.Group(); pivot.position.set(0, 0.16, 0); g.add(pivot);
  const metal = '#d0d4da';
  const rod = (len, x, z, rotZ = 0) => {
    const m = toon(new THREE.CylinderGeometry(0.025, 0.025, len, 8), metal);
    m.rotation.z = rotZ; m.position.set(x, 0, z); return m;
  };
  pivot.add(rod(0.8, 0.4, 0.38, Math.PI / 2), rod(0.8, 0.4, -0.38, Math.PI / 2));
  const front = toon(new THREE.CylinderGeometry(0.025, 0.025, 0.78, 8), metal); front.rotation.x = Math.PI / 2; front.position.set(0.8, 0, 0); pivot.add(front);
  const spring = toon(new THREE.TorusGeometry(0.09, 0.025, 8, 16), metal); spring.position.set(0, 0.0, 0.2); g.add(spring);
  const bait = coin(); bait.scale.setScalar(0.9); bait.rotation.x = Math.PI / 2 - 0.2; bait.position.set(0.55, 0.42, 0); g.add(bait);
  pivot.rotation.z = Math.PI;
  g.userData = { pivot, bait };
  return g;
}

export function lightShaft(color = '#fff2c4', { r = 1.6, h = 8, opacity = 0.1 } = {}) {
  const m = new THREE.Mesh(
    new THREE.CylinderGeometry(0.15, r, h, 32, 1, true),
    new THREE.MeshBasicMaterial({ color, transparent: true, opacity, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }),
  );
  m.position.y = h / 2;
  return m;
}

export function confetti(n = 220, seed = 5) {
  const r = rng(seed);
  const geo = new THREE.PlaneGeometry(0.09, 0.05);
  const mat = new THREE.MeshBasicMaterial({ side: THREE.DoubleSide, toneMapped: false });
  const mesh = new THREE.InstancedMesh(geo, mat, n);
  const cols = ['#ffd400', '#ff3b8d', '#3bd5ff', '#5dff7a', '#ffffff', '#ff7a2a'];
  const parts = Array.from({ length: n }, (_, i) => {
    mesh.setColorAt(i, new THREE.Color(cols[i % cols.length]).multiplyScalar(1.4));
    return { v: new THREE.Vector3((r() - 0.5) * 6, 4 + r() * 5, (r() - 0.2) * 4), s: new THREE.Vector3(r() * 9, r() * 9, r() * 9), d: r() * 0.3 };
  });
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), p = new THREE.Vector3(), one = new THREE.Vector3(1, 1, 1);
  mesh.update = (t, origin) => {
    parts.forEach((pt, i) => {
      const tt = Math.max(0, t - pt.d);
      const drag = Math.min(tt, 1.2);
      p.set(origin.x + pt.v.x * drag, origin.y + pt.v.y * drag - 3.5 * drag * drag - Math.max(0, tt - 1.2) * 0.9, origin.z + pt.v.z * drag);
      e.set(pt.s.x * tt, pt.s.y * tt, pt.s.z * tt); q.setFromEuler(e);
      m4.compose(p, q, t > pt.d ? one : new THREE.Vector3(0, 0, 0));
      mesh.setMatrixAt(i, m4);
    });
    mesh.instanceMatrix.needsUpdate = true;
  };
  mesh.frustumCulled = false;
  return mesh;
}
