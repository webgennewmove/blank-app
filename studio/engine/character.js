const K = '#151515';
const LW = 12;
const SKIN = '#fafaf5';

const POSES = {
  idle:  { L: [[420, 540], [395, 640], [402, 735]], R: [[605, 540], [630, 640], [622, 735]] },
  point: { L: [[420, 540], [395, 640], [402, 735]], R: [[605, 540], [700, 505], [810, 445]] },
  shrug: { L: [[420, 540], [320, 610], [295, 500]], R: [[605, 540], [705, 610], [730, 500]] },
  hold:  { L: [[420, 540], [370, 630], [455, 665]], R: [[605, 540], [655, 630], [570, 665]] },
  think: { L: [[420, 540], [395, 640], [402, 735]], R: [[605, 540], [745, 450], [705, 300]] },
  cheer: { L: [[420, 540], [330, 450], [320, 330]], R: [[605, 540], [695, 450], [705, 330]] },
};

const BROWS = {
  neutral: [[0, 0], [0, 0]],
  smug:    [[6, 6], [-12, -24]],
  shock:   [[-26, -20], [-26, -20]],
  sad:     [[-18, 8], [-18, 8]],
  happy:   [[-10, -10], [-10, -10]],
  excited: [[-28, -24], [-28, -24]],
  dizzy:   [[-14, 6], [6, -14]],
};

const ease = (x) => (x < 0.5 ? 2 * x * x : 1 - (-2 * x + 2) ** 2 / 2);

function at(schedule, t) {
  if (typeof schedule === 'string') return { a: schedule, b: schedule, k: 1 };
  let i = 0;
  while (i + 1 < schedule.length && schedule[i + 1][0] <= t) i++;
  const [t0, b] = schedule[i];
  const a = i > 0 ? schedule[i - 1][1] : b;
  return { a, b, k: ease(Math.min(1, Math.max(0, (t - t0) / 0.25))) };
}

function stroke2(c, path, fill, w = LW) {
  c.fillStyle = fill; path(); c.fill();
  c.lineWidth = w; c.strokeStyle = K; path(); c.stroke();
}

function limb(c, pts, color, w) {
  for (const [col, width] of [[K, w + LW * 2], [color, w]]) {
    c.strokeStyle = col; c.lineWidth = width;
    c.beginPath(); c.moveTo(...pts[0]);
    c.quadraticCurveTo(pts[1][0], pts[1][1], pts[2][0], pts[2][1]);
    c.stroke();
  }
}

function drawBody(c) {
  limb(c, [[465, 730], [458, 850], [452, 945]], '#2d3654', 44);
  limb(c, [[560, 730], [567, 850], [573, 945]], '#2d3654', 44);
  for (const x of [445, 580]) stroke2(c, () => { c.beginPath(); c.ellipse(x, 960, 42, 20, 0, 0, Math.PI * 2); }, '#222');
  stroke2(c, () => { c.beginPath(); c.roundRect(410, 470, 205, 290, 60); }, '#1e7a4f');
  stroke2(c, () => { c.beginPath(); c.moveTo(462, 474); c.lineTo(562, 474); c.lineTo(512, 575); c.closePath(); }, '#fff', 7);
  stroke2(c, () => {
    c.beginPath(); c.moveTo(500, 505); c.lineTo(524, 505); c.lineTo(536, 645);
    c.lineTo(512, 675); c.lineTo(488, 645); c.closePath();
  }, '#d63a2f', 7);
}

function drawHead(c, expr, open, talk, look, t) {
  const head = () => { c.beginPath(); c.arc(512, 300, 190, 0, Math.PI * 2); };
  c.fillStyle = SKIN; head(); c.fill();
  c.save(); head(); c.clip();
  c.fillStyle = '#5b3a24';
  c.beginPath(); c.moveTo(300, 215);
  c.bezierCurveTo(400, 170, 620, 170, 724, 215);
  c.lineTo(724, 60); c.lineTo(300, 60); c.closePath(); c.fill();
  c.restore();
  c.lineWidth = LW; c.strokeStyle = K; head(); c.stroke();

  for (const [col, w] of [[K, 26 + LW * 2], ['#2e9d5b', 26]]) {
    c.strokeStyle = col; c.lineWidth = w;
    c.beginPath(); c.moveTo(330, 222); c.quadraticCurveTo(512, 175, 694, 222); c.stroke();
  }
  stroke2(c, () => {
    c.beginPath(); c.moveTo(290, 232);
    c.quadraticCurveTo(512, 320, 734, 232);
    c.quadraticCurveTo(512, 250, 290, 232); c.closePath();
  }, 'rgba(70,200,120,0.78)', 10);

  const brows = BROWS[expr] ?? BROWS.neutral;
  [[450, -1], [575, 1]].forEach(([x, side], i) => {
    const [inner, outer] = brows[i];
    c.lineWidth = 11; c.strokeStyle = K;
    c.beginPath(); c.moveTo(x - side * 26, 290 + inner); c.lineTo(x + side * 26, 290 + outer); c.stroke();

    const lx = look * 10;
    if (expr === 'shock' || expr === 'excited') {
      stroke2(c, () => { c.beginPath(); c.arc(x, 345, 34, 0, Math.PI * 2); }, '#fff', 8);
      c.fillStyle = K; c.beginPath(); c.arc(x + lx * 1.6, 348, 11 * Math.max(open, 0.3), 0, Math.PI * 2); c.fill();
    } else if (expr === 'dizzy') {
      stroke2(c, () => { c.beginPath(); c.arc(x, 345, 34, 0, Math.PI * 2); }, '#fff', 8);
      c.lineWidth = 6; c.beginPath();
      for (let a = 0; a < Math.PI * 5; a += 0.25) {
        const r = 1 + a * 1.8, px = x + Math.cos(a + t * 9 * side) * r, py = 345 + Math.sin(a + t * 9 * side) * r;
        a ? c.lineTo(px, py) : c.moveTo(px, py);
      }
      c.stroke();
    } else if (expr === 'smug') {
      c.fillStyle = K; c.beginPath(); c.ellipse(x + lx, 342, 22, 13 * open, 0, 0, Math.PI); c.fill();
      c.lineWidth = 9; c.beginPath(); c.moveTo(x - 27, 342); c.lineTo(x + 27, 340); c.stroke();
    } else if (expr === 'happy') {
      c.lineWidth = 11; c.beginPath(); c.arc(x, 352, 20, Math.PI * 1.1, Math.PI * 1.9); c.stroke();
    } else {
      c.fillStyle = K; c.beginPath(); c.ellipse(x + lx, 340, 16, 24 * open, 0, 0, Math.PI * 2); c.fill();
    }
  });

  const mx = 512, my = 425;
  c.lineWidth = 10; c.strokeStyle = K;
  if (talk > 0.12) {
    const rx = 30, ry = 6 + 30 * talk;
    const m = () => { c.beginPath(); c.ellipse(mx, my, rx, ry, 0, 0, Math.PI * 2); };
    c.fillStyle = '#4a1010'; m(); c.fill();
    c.save(); m(); c.clip();
    c.fillStyle = '#e0626b'; c.beginPath(); c.ellipse(mx, my + ry * 0.9, rx * 0.8, ry * 0.6, 0, 0, Math.PI * 2); c.fill();
    c.restore();
    m(); c.stroke();
  } else if (expr === 'excited') {
    stroke2(c, () => { c.beginPath(); c.moveTo(mx - 44, my - 8); c.quadraticCurveTo(mx, my - 2, mx + 44, my - 8); c.quadraticCurveTo(mx, my + 62, mx - 44, my - 8); c.closePath(); }, '#4a1010', 10);
  } else if (expr === 'happy') {
    c.beginPath(); c.arc(mx, my - 20, 36, Math.PI * 0.2, Math.PI * 0.8); c.stroke();
  } else if (expr === 'smug') {
    c.beginPath(); c.moveTo(mx - 30, my + 2); c.quadraticCurveTo(mx + 5, my + 16, mx + 36, my - 12); c.stroke();
  } else if (expr === 'shock') {
    stroke2(c, () => { c.beginPath(); c.ellipse(mx, my + 8, 17, 24, 0, 0, Math.PI * 2); }, '#4a1010', 10);
  } else if (expr === 'sad') {
    c.beginPath(); c.arc(mx, my + 30, 30, Math.PI * 1.2, Math.PI * 1.8); c.stroke();
  } else {
    c.beginPath(); c.moveTo(mx - 22, my); c.quadraticCurveTo(mx, my + 8, mx + 22, my); c.stroke();
  }
}

export function createBuck(THREE, { height = 3.1 } = {}) {
  const cv = document.createElement('canvas');
  cv.width = cv.height = 1024;
  const c = cv.getContext('2d');
  c.lineJoin = 'round'; c.lineCap = 'round';
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;

  const geo = new THREE.PlaneGeometry(height, height);
  geo.translate(0, height / 2 - height * (40 / 1024), 0);
  const mesh = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({
    map: tex, transparent: true, alphaTest: 0.02, toneMapped: false,
  }));
  const shadow = new THREE.Mesh(
    new THREE.CircleGeometry(height * 0.17, 32),
    new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.28, depthWrite: false }),
  );
  shadow.rotation.x = -Math.PI / 2;
  shadow.scale.y = 0.45;
  shadow.position.y = 0.01;

  const group = new THREE.Group();
  group.add(shadow, mesh);

  function update(t, { pose = 'idle', expr = 'neutral', talk = 0, look = 0 } = {}, camera) {
    const open = t % 3.3 < 0.12 ? 0.15 : 1;
    const e = at(expr, t).b;
    const lk = typeof look === 'number' ? look : at(look, t).b;
    const p = at(pose, t);

    c.clearRect(0, 0, 1024, 1024);
    drawBody(c);
    drawHead(c, e, open, talk, lk, t);
    for (const side of ['L', 'R']) {
      const A = POSES[p.a][side], B = POSES[p.b][side];
      const pts = A.map((q, i) => [
        q[0] + (B[i][0] - q[0]) * p.k,
        q[1] + (B[i][1] - q[1]) * p.k + (i === 2 ? Math.sin(t * 2.2 + (side === 'L' ? 0 : 1.7)) * 6 : 0),
      ]);
      limb(c, pts, '#f4f4ee', 26);
      stroke2(c, () => { c.beginPath(); c.arc(pts[2][0], pts[2][1], 25, 0, Math.PI * 2); }, SKIN, 10);
    }
    tex.needsUpdate = true;

    const bob = 0.008 * Math.sin(t * 2) + talk * 0.02;
    mesh.scale.set(1 - bob * 0.6, 1 + bob, 1);
    if (camera) {
      mesh.rotation.y = Math.atan2(camera.position.x - group.position.x, camera.position.z - group.position.z) - group.rotation.y;
    }
  }

  return { group, update };
}
