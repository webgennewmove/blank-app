import * as THREE from 'three';
import { createBuck } from '../engine/character.js';
import {
  makeStage, moveCamera, toon, rbox, textPanel, coin, rng, popIn, clamp01, ease, lerp,
  glowMat, neonText, bulbRow, rectPoints, carpetTexture, stringBetween,
} from '../engine/world.js';
import {
  slotMachine, iconPanel, drawClover, drawX, brainPanel, clockPanel, windowPanel, ghostClockPanel,
  bill, chip, chipStack, pokerTable, grouchoPanel, noteIcon, mouseTrap, lightShaft, confetti,
} from '../engine/props.js';
import { wallet, gauge, ecg, popText, cite } from '../engine/hud.js';

const BH = 3.1;
const buckPoint = (pos, cx, cy) => new THREE.Vector3(pos.x + (cx / 1024 - 0.5) * BH, pos.y + (1 - cy / 1024) * BH - BH * (40 / 1024), pos.z);

const pop = (k) => Math.max(0.0001, popIn(k));
const showPop = (obj, since, dur = 0.25, base = 1) => {
  const k = clamp01(since / dur);
  obj.visible = since >= 0;
  obj.scale.setScalar(base * pop(k) * (1 + (1 - k) * 0.6));
};

function addBuck(scene, x, z = 0.5) {
  const b = createBuck(THREE, { height: BH });
  b.group.position.set(x, 0, z);
  scene.add(b.group);
  return b;
}

function pointLight(scene, color, intensity, pos, distance = 20) {
  const l = new THREE.PointLight(color, intensity, distance, 2);
  l.position.set(...pos);
  scene.add(l);
  return l;
}

function spot(scene, target, color = '#fff2c4', intensity = 160, pos = [0, 9, 1]) {
  const s = new THREE.SpotLight(color, intensity, 25, 0.45, 0.6, 1.5);
  s.position.set(...pos);
  s.target.position.copy(target);
  scene.add(s, s.target);
  return s;
}

function exterior(o) {
  const st = makeStage({ ...o, sky: ['#07051a', '#3b1250'], ground: '#140c1e', fog: ['#2a0f3a', 16, 80], hemi: 0.7, sunK: 0.5 });
  const { scene } = st;
  const r = rng(3);
  const starGeo = new THREE.BufferGeometry();
  const pts = [];
  for (let i = 0; i < 500; i++) { const a = r() * Math.PI * 2, e = 0.15 + r() * 1.2; pts.push(Math.cos(a) * 150 * Math.cos(e), 150 * Math.sin(e), Math.sin(a) * 150 * Math.cos(e) - 40); }
  starGeo.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
  scene.add(new THREE.Points(starGeo, new THREE.PointsMaterial({ color: '#ffffff', size: 0.9, fog: false })));

  const facade = toon(rbox(14, 8, 1.2, 0.2), '#2b1745'); facade.position.set(0, 4, -7); scene.add(facade);
  for (const x of [-8.2, 8.2]) { const tw = toon(rbox(3, 11, 1.8, 0.2), '#3a1d5c'); tw.position.set(x, 5.5, -7.2); scene.add(tw); }
  const door = toon(rbox(3.2, 3.4, 0.3, 0.05), '#0d0204'); door.position.set(0, 1.7, -6.35); scene.add(door);
  const toothMat = glowMat('#fff3cf', 1.05);
  const toothGeo = new THREE.ConeGeometry(0.14, 0.42, 4);
  for (let x = -1.35; x <= 1.36; x += 0.3) {
    const top = new THREE.Mesh(toothGeo, toothMat); top.rotation.x = Math.PI; top.position.set(x, 3.2, -6.15); scene.add(top);
    const bot = new THREE.Mesh(toothGeo, toothMat); bot.position.set(x + 0.15, 0.2, -6.15); scene.add(bot);
  }
  const bulbs = bulbRow(rectPoints(13.4, 7.4, 0.45), { size: 0.08, k: 2.2 }); bulbs.position.set(0, 4, -6.35); scene.add(bulbs);
  const sign = neonText('CASINO', { h: 1.7, color: '#ff3b8d', k: 2.8 }); sign.position.set(0, 5.75, -6.3); scene.add(sign);
  const open = neonText('OPEN 24/7', { h: 0.55, color: '#3bd5ff', k: 2.4 }); open.position.set(4.3, 3.0, -6.3); scene.add(open);
  pointLight(scene, '#ff3b8d', 22, [0, 5.5, -3], 18);
  pointLight(scene, '#ff6a2a', 10, [0, 1.5, -5], 8);
  const buck = addBuck(scene, -2.3, 0.8);
  const clover = iconPanel(1.5, drawClover); clover.position.set(2.5, 2.5, 1.0); scene.add(clover);
  const xm = iconPanel(1.7, drawX); xm.position.set(2.5, 2.5, 1.05); scene.add(xm);
  return { ...st, buck, bulbs, sign, clover, xm };
}

function brainRoom(o) {
  const st = makeStage({ ...o, sky: ['#050507', '#15152a'], ground: '#101018', fog: ['#101018', 9, 30], hemi: 0.45, sunK: 0.3 });
  const { scene } = st;
  const buck = addBuck(scene, -0.5, 0.3);
  scene.add(Object.assign(lightShaft('#fff2c4', { r: 1.7, h: 9, opacity: 0.05 }), {}));
  scene.children.at(-1).position.set(-0.5, 4.5, 0.3);
  spot(scene, new THREE.Vector3(-0.5, 0, 0.3), '#fff2c4', 30, [-0.5, 9, 1]);
  const bar = new THREE.Group();
  bar.add(toon(rbox(2.4, 0.14, 0.14, 0.05), '#7a5230'));
  const cross = toon(rbox(0.14, 0.14, 1.2, 0.05), '#7a5230'); bar.add(cross);
  bar.position.set(-0.5, 5.2, 0.3);
  scene.add(bar);
  const strMat = glowMat('#ffffff', 1.3);
  const strings = [0, 1, 2].map(() => { const m = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 1, 6), strMat); scene.add(m); return m; });
  const brain = brainPanel(); brain.position.set(2.1, 2.5, 0); scene.add(brain);
  const red = pointLight(scene, '#ff2a3a', 0, [2.1, 2.5, 1.5], 8);
  return { ...st, buck, bar, strings, brain, red };
}

function casinoFloor(o) {
  const st = makeStage({ ...o, sky: ['#1a0710', '#2a0b14'], ground: '#ffffff', fog: ['#2a0b14', 12, 40], hemi: 1.0, sunK: 0.5 });
  const { scene, ground } = st;
  ground.material.map = carpetTexture(60); ground.material.needsUpdate = true;
  const wall = toon(rbox(26, 6.2, 0.4, 0.1), '#3b1622'); wall.position.set(0, 3.1, -6.2); scene.add(wall);
  for (const x of [-11, 11]) { const w = toon(rbox(0.4, 6.2, 16, 0.1), '#3b1622'); w.position.set(x, 3.1, 0); scene.add(w); }
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(26, 18), new THREE.MeshBasicMaterial({ color: '#1a080e', side: THREE.DoubleSide }));
  ceil.rotation.x = Math.PI / 2; ceil.position.y = 6.1; scene.add(ceil);
  const lampMat = glowMat('#ffd9a0', 2.2);
  for (let x = -8; x <= 8; x += 3.2) for (let z = -4; z <= 4; z += 3) {
    const l = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.05, 0.3), lampMat); l.position.set(x, 6.05, z); scene.add(l);
  }
  const r = rng(7);
  const machines = [];
  for (let i = -4; i <= 4; i++) {
    const m = slotMachine({ body: ['#c81e3a', '#1e5ac8', '#7a1ec8'][(i + 9) % 3] });
    m.scale.setScalar(0.9); m.position.set(i * 2.2, 0, -4.2);
    m.userData.set({ reels: [Math.floor(r() * 8), Math.floor(r() * 8), Math.floor(r() * 8)] });
    scene.add(m); machines.push(m);
  }
  for (const s of [-1, 1]) for (let j = 0; j < 3; j++) {
    const m = slotMachine({ body: '#c81e3a' });
    m.scale.setScalar(0.9); m.position.set(s * 7.2, 0, -1.2 + j * 2.4); m.rotation.y = -s * Math.PI / 2;
    m.userData.set({ reels: [j, j + 3, j + 5] });
    scene.add(m); machines.push(m);
  }
  const ghost = ghostClockPanel(); ghost.position.set(-3.2, 4.6, -5.95); scene.add(ghost);
  const win = windowPanel(); win.position.set(3.2, 4.6, -5.95); scene.add(win);
  const x1 = iconPanel(1.9, drawX); x1.position.set(-3.2, 4.6, -5.9); scene.add(x1);
  const x2 = iconPanel(1.9, drawX); x2.position.set(3.2, 4.6, -5.9); scene.add(x2);
  pointLight(scene, '#ffb36b', 22, [0, 5, 2], 18);
  const buck = addBuck(scene, 0, 1.4);
  return { ...st, buck, machines, x1, x2 };
}

function timeWarp(o) {
  const st = makeStage({ ...o, sky: ['#12072a', '#4b2380'], ground: '#1c0c36', fog: ['#30145a', 9, 40], hemi: 1.0, sunK: 0.6 });
  const { scene } = st;
  const buck = addBuck(scene, -1.9, 0.6);
  const clock = clockPanel(3.0); clock.position.set(1.3, 2.4, -1.2); scene.add(clock);
  const r = rng(13);
  const minis = Array.from({ length: 7 }, (_, i) => {
    const m = clockPanel(0.8); m.position.set((r() - 0.5) * 12, 1 + r() * 4, -4 - r() * 5);
    m.userData.ph = r() * 6; m.userData.i = i; scene.add(m); return m;
  });
  pointLight(scene, '#b66bff', 18, [1.3, 3, 2], 12);
  return { ...st, buck, clock, minis };
}

function tableSet(o) {
  const st = makeStage({ ...o, sky: ['#120806', '#2a120c'], ground: '#ffffff', fog: ['#2a120c', 9, 30], hemi: 0.9, sunK: 1.0 });
  const { scene, ground } = st;
  ground.material.map = carpetTexture(60); ground.material.needsUpdate = true;
  const table = pokerTable(); scene.add(table);
  const buck = addBuck(scene, -2.5, -1.9);
  const cash = bill(); cash.position.set(0.3, 1.17, 0.5); scene.add(cash);
  const stacks = [['#d6273a', 5, -0.7, 0.6], ['#2457d6', 7, 0.3, 0.8], ['#1b1b1b', 4, 1.3, 0.5]].map(([c, n, x, z], i) => {
    const s = chipStack(n, c, i + 1); s.position.set(x, 1.14, z); scene.add(s); return s;
  });
  const cashUp = bill(); cashUp.rotation.x = Math.PI / 2; cashUp.position.set(-1.3, 2.5, 0.9); scene.add(cashUp);
  const chipUp = chip('#d6273a'); chipUp.scale.setScalar(1.6); chipUp.rotation.x = Math.PI / 2; chipUp.position.set(1.3, 2.5, 0.9); scene.add(chipUp);
  const shade = toon(new THREE.ConeGeometry(0.8, 0.6, 24, 1, true), '#1f5a3a'); shade.position.set(0, 5.2, 0.2); scene.add(shade);
  const shaft = lightShaft('#fff2c4', { r: 2.2, h: 4.2, opacity: 0.04 }); shaft.position.set(0, 3.0, 0.2); scene.add(shaft);
  pointLight(scene, '#ffe2b0', 12, [0, 4.6, 0.6], 10);
  return { ...st, buck, cash, stacks, cashUp, chipUp };
}

function slotRoom(o) {
  const st = makeStage({ ...o, sky: ['#120306', '#2a070c'], ground: '#3a0a12', fog: ['#1a0508', 9, 30], hemi: 0.55, sunK: 0.35 });
  const { scene } = st;
  const wall = toon(rbox(18, 7.5, 0.4, 0.1), '#2a0a10'); wall.position.set(0, 3.75, -3); scene.add(wall);
  const machine = slotMachine(); machine.scale.setScalar(1.25); machine.position.set(1.3, 0, -0.6); scene.add(machine);
  const shadow = textPanel(4.2, 5.6, (c, W, H) => {
    c.fillStyle = '#000';
    c.beginPath(); c.roundRect(W * 0.2, H * 0.3, W * 0.6, H * 0.7, W * 0.06); c.fill();
    for (const s of [-1, 1]) {
      c.beginPath();
      c.moveTo(W / 2 + s * W * 0.16, H * 0.32);
      c.quadraticCurveTo(W / 2 + s * W * 0.42, H * 0.2, W / 2 + s * W * 0.3, H * 0.02);
      c.quadraticCurveTo(W / 2 + s * W * 0.3, H * 0.2, W / 2 + s * W * 0.04, H * 0.32);
      c.fill();
    }
  });
  shadow.material.opacity = 0.15; shadow.position.set(2.6, 3.4, -2.78); scene.add(shadow);
  const red = pointLight(scene, '#ff2a3a', 10, [1.3, 2.4, 2.2], 12);
  const buck = addBuck(scene, -1.7, 0.5);
  const winner = neonText('WINNER!', { h: 0.95, color: '#ffd400', k: 3 }); winner.position.set(1.3, 4.65, -0.4); scene.add(winner);
  const conf = confetti(240, 5); scene.add(conf);
  const r = rng(31);
  const coins = Array.from({ length: 22 }, () => {
    const c = coin(); c.userData = { v: new THREE.Vector3((r() - 0.5) * 3, 3 + r() * 3, 1.5 + r() * 2.5), s: 3 + r() * 6, d: r() * 0.5 };
    scene.add(c); return c;
  });
  const notes = Array.from({ length: 5 }, (_, i) => { const n = noteIcon(); n.userData.i = i; scene.add(n); return n; });
  return { ...st, buck, machine, shadow, red, winner, conf, coins, notes };
}

function disguiseSet(o) {
  const st = makeStage({ ...o, sky: ['#05060c', '#141a2e'], ground: '#0e1220', fog: ['#0e1220', 9, 30], hemi: 0.5, sunK: 0.3 });
  const { scene } = st;
  const ped = toon(new THREE.CylinderGeometry(0.75, 0.85, 1.2, 32), '#e8e2d4'); ped.position.set(1.1, 0.6, 0); scene.add(ped);
  const hero = new THREE.Group(); hero.position.set(1.1, 2.15, 0); scene.add(hero);
  const big = coin(); big.scale.setScalar(3.2); big.rotation.x = Math.PI / 2; hero.add(big);
  const specs = grouchoPanel(); specs.position.set(0, 0.12, 0.2); hero.add(specs);
  const shaft = lightShaft('#cfe0ff', { r: 1.6, h: 8, opacity: 0.05 }); shaft.position.set(1.1, 4, 0); scene.add(shaft);
  spot(scene, new THREE.Vector3(1.1, 1.5, 0), '#e6eeff', 28, [1.1, 9, 1.5]);
  const label = neonText('LOSS DISGUISED AS A WIN', { h: 0.55, color: '#ff3b8d', k: 2.8 }); label.position.set(0, 4.1, -1.5); scene.add(label);
  const buck = addBuck(scene, -1.9, 0.6);
  return { ...st, buck, hero, specs, label };
}

function bodySet(o) {
  const st = makeStage({ ...o, sky: ['#0a0316', '#2a0a3a'], ground: '#1a0a24', fog: ['#1a0a24', 9, 30], hemi: 0.8, sunK: 0.5 });
  const { scene } = st;
  const buck = addBuck(scene, -1.3, 0.6);
  const heart = textPanel(2.2, 2.0, (c, W, H) => {
    c.fillStyle = '#ff2a4a'; c.strokeStyle = '#151515'; c.lineWidth = W * 0.035; c.lineJoin = 'round';
    c.beginPath(); c.moveTo(W / 2, H * 0.92);
    c.bezierCurveTo(W * 0.05, H * 0.55, W * 0.08, H * 0.08, W / 2, H * 0.28);
    c.bezierCurveTo(W * 0.92, H * 0.08, W * 0.95, H * 0.55, W / 2, H * 0.92);
    c.fill(); c.stroke();
    c.fillStyle = 'rgba(255,255,255,0.6)'; c.beginPath(); c.ellipse(W * 0.3, H * 0.33, W * 0.07, H * 0.1, -0.5, 0, Math.PI * 2); c.fill();
  });
  heart.position.set(1.7, 2.4, 0); scene.add(heart);
  const glow = pointLight(scene, '#ff2a4a', 20, [1.7, 2.4, 1.5], 10);
  return { ...st, buck, heart, glow };
}

function trapSet(o) {
  const st = makeStage({ ...o, sky: ['#020203', '#0a0a10'], ground: '#0b0b0f', fog: ['#050507', 7, 22], hemi: 0.3, sunK: 0.15 });
  const { scene } = st;
  const trap = mouseTrap(); trap.scale.setScalar(1.4); trap.position.set(0.9, 0, 0.3); trap.rotation.y = -0.35; scene.add(trap);
  const shaft = lightShaft('#fff2c4', { r: 1.5, h: 8, opacity: 0.05 }); shaft.position.set(0.9, 4, 0.3); scene.add(shaft);
  spot(scene, new THREE.Vector3(0.9, 0, 0.3), '#fff2c4', 30, [0.9, 9, 1.2]);
  const buck = addBuck(scene, -2.4, 0.4);
  return { ...st, buck, trap };
}

const bpmCurve = (a) => (tt) => {
  const k = clamp01((tt - a.at(99)) / (a.at(103) - a.at(99) + 0.4));
  return 72 + 60 * ease(k);
};

export default {
  title: 'How casinos hack your brain',
  tail: 1.6,
  emph: {
    5: '#ffd400', 12: '#ff8fb1', 18: '#ff4d4d', 20: '#ff4d4d', 29: '#c58bff', 38: '#5dff7a', 43: '#c58bff',
    48: '#ffd400', 60: '#ff2a2a', 63: '#ff4d4d', 67: '#5dff7a', 73: '#ffd400', 81: '#ff2a2a', 84: '#ff2a2a',
    91: '#ff4d4d', 92: '#ff8fb1', 95: '#5dff7a', 98: '#ff8fb1', 103: '#5dff7a', 110: '#ff2a2a', 111: '#ff2a2a',
  },

  setup: (o) => ({
    exterior: exterior(o), brain: brainRoom(o), floor: casinoFloor(o), warp: timeWarp(o), table: tableSet(o),
    slot: slotRoom(o), disguise: disguiseSet(o), body: bodySet(o), trap: trapSet(o),
  }),

  mix(a) {
    const snapAt = a.duration - 0.75;
    const cues = a.shots.slice(1).map((s) => [s.start - 0.12, 'whoosh', 0.3]);
    cues.push(
      [a.at(5) + 0.25, 'impact', 0.8], [a.at(10), 'glitch', 0.55], [a.at(12), 'impact', 0.45],
      [a.at(18) + 0.15, 'impact', 0.7], [a.at(20) + 0.1, 'impact', 0.7],
      [a.at(43), 'chips', 0.7],
      [a.at(60), 'impact', 0.9], [a.at(60), 'glitch', 0.45],
      [a.at(62), 'reels', 0.45], [a.at(65) + 0.1, 'clunk', 0.6], [a.at(66) + 0.1, 'clunk', 0.6], [a.at(67) - 0.05, 'clunk', 0.6],
      [a.at(73), 'jackpot', 0.55],
      [a.at(80) - 0.05, 'scratch', 0.8], [a.at(84), 'impact', 0.8], [a.at(92), 'impact', 0.35],
      [snapAt, 'snap', 1.0], [snapAt, 'impact', 0.7],
    );
    for (let tt = a.at(21), step = 0.5; tt < a.at(34) - 0.2; tt += step) {
      cues.push([tt, 'tick', tt > a.at(29) ? 0.2 : 0.35]);
      step = tt > a.at(29) ? 0.11 : tt > a.at(25) ? 0.25 : 0.5;
    }
    const bpm = bpmCurve(a);
    let last = null;
    for (let tt = a.at(96); tt < a.at(105) - 0.1; tt += 1 / 240) {
      const k = Math.floor((tt * bpm(tt)) / 60);
      if (last !== null && k !== last) cues.push([tt, 'heartbeat', 0.5 + 0.4 * clamp01((tt - a.at(99)) / 2)]);
      last = k;
    }
    return { music: { gain: 0.24, mutes: [[a.at(80) - 0.05, a.at(87) - 0.15], [snapAt, a.duration + 2]] }, cues };
  },

  hud(ctx, t, a) {
    const { W, H } = a;
    if (t >= a.at(37) - 0.2 && a.shot.set !== 'trap') {
      let s = { label: 'CASH', value: '$100.00', color: '#5dff7a' };
      if (t >= a.at(43)) s = { label: 'CHIPS', value: '$100.00', color: '#c58bff' };
      if (t >= a.at(62)) s = { label: 'CHIPS', value: '$99.00', color: '#ff8a8a', delta: '-$1.00', deltaColor: '#ff4d4d', deltaAge: t - a.at(62) };
      if (t >= a.at(67)) s = { label: 'CHIPS', value: '$99.50', color: '#c58bff', delta: '+$0.50', deltaColor: '#5dff7a', deltaAge: t - a.at(67) };
      if (t >= a.at(84)) s = { label: 'NET RESULT', value: '-$0.50', color: '#ff4d4d', delta: '', deltaAge: 99 };
      const age = Math.min(s.deltaAge ?? 99, t - a.at(43), t - a.at(84));
      wallet(ctx, W, H, { ...s, appear: (t - a.at(37) + 0.2) / 0.35, pulse: age >= 0 && age < 0.25 ? 1 - age / 0.25 : 0 });
    }
    a.shot.hud?.(ctx, t, a);
  },

  shots: [
    {
      at: 0, set: 'exterior',
      update(lt, a) {
        const s = a.set;
        moveCamera(s.camera, { from: [0, 2.6, 13], to: [0.2, 2.1, 7.2], lookFrom: [0, 3.6, -3], lookTo: [0.3, 2.2, 0], k: lt / a.dur });
        s.bulbs.chase(a.t, 9);
        s.sign.setGlow(2.6 + Math.sin(a.t * 30) * 0.3 * (Math.sin(a.t * 3) > 0.7 ? 1 : 0));
        showPop(s.clover, a.since(5) + 0.15);
        showPop(s.xm, a.since(5) - 0.25, 0.2);
        if (a.since(5) - 0.25 > 0 && a.since(5) < 0.2) a.fx.shake = 0.6;
        s.buck.update(a.t, { talk: a.talk, expr: [[0, 'smug']], pose: [[0, 'idle'], [a.cue(4), 'point']] }, s.camera);
      },
    },
    {
      at: 6, set: 'brain',
      update(lt, a) {
        const s = a.set;
        const punch = ease(clamp01(a.since(12) / 0.18));
        moveCamera(s.camera, { from: [0, 2.0, 7.4 - punch * 1.6], to: [0, 2.0, 7.4 - punch * 1.6], lookFrom: [0.2, 2.2, 0], k: 0 });
        s.bar.rotation.z = Math.sin(a.t * 2.4) * 0.12;
        s.bar.rotation.x = Math.sin(a.t * 1.7) * 0.08;
        s.bar.position.x = -0.5 + Math.sin(a.t * 1.2) * 0.15;
        const ends = [[-1.1, 0], [1.1, 0], [0, 0]].map(([x]) => new THREE.Vector3(x, 0, 0).applyEuler(s.bar.rotation).add(s.bar.position));
        const p = s.buck.group.position;
        const lift = Math.sin(a.t * 2.4) * 20;
        const targets = [buckPoint(p, 295, 500 + lift), buckPoint(p, 730, 500 - lift), buckPoint(p, 512, 112)];
        s.strings.forEach((m, i) => stringBetween(m, ends[i], targets[i]));
        const hacked = a.since(10) >= 0;
        if (s.brain.userData.h !== hacked) { s.brain.userData.tex.redraw(hacked); s.brain.userData.h = hacked; }
        s.brain.scale.setScalar(1 + (hacked ? 0.04 * Math.sin(a.t * 18) : 0));
        s.red.intensity = hacked ? 14 + 7 * Math.sin(a.t * 12) : 0;
        if (a.since(10) >= 0 && a.since(10) < 0.35) { a.fx.glitch = 1 - a.since(10) / 0.35; a.fx.shake = 0.5; }
        if (a.since(12) >= 0 && a.since(12) < 0.25) a.fx.shake = 1;
        s.buck.update(a.t, { talk: a.talk, expr: [[0, 'smug'], [a.cue(10), 'shock']], pose: 'shrug' }, s.camera);
      },
    },
    {
      at: 13, set: 'floor',
      update(lt, a) {
        const s = a.set;
        moveCamera(s.camera, { from: [0, 2.0, 8.6], to: [0, 2.0, 6.8], lookFrom: [0, 2.2, -2], k: lt / a.dur });
        s.machines.forEach((m, i) => m.userData.bulbs.chase(a.t + i * 0.3, 7));
        s.x1.visible = s.x2.visible = false;
        s.buck.update(a.t, { talk: a.talk, expr: 'neutral', look: [[0, 0], [a.cue(14), -1], [a.cue(16), 1]] }, s.camera);
      },
    },
    {
      at: 18, set: 'floor',
      update(lt, a) {
        const s = a.set;
        moveCamera(s.camera, { from: [-3.2, 4.2, -1.6], to: [-3.2, 4.4, -2.4], lookFrom: [-3.2, 4.5, -6], k: lt / a.dur });
        showPop(s.x1, a.since(18) - 0.15, 0.2);
        if (a.since(18) > 0.15 && a.since(18) < 0.35) a.fx.shake = 0.6;
        s.x2.visible = false;
      },
    },
    {
      at: 19, set: 'floor',
      update(lt, a) {
        const s = a.set;
        const k = ease(clamp01(lt / 0.22));
        moveCamera(s.camera, { from: [lerp(-3.2, 3.2, k), 4.4, -2.4], to: [lerp(-3.2, 3.2, k), 4.4, -2.4], lookFrom: [lerp(-3.2, 3.2, k), 4.5, -6], k: 0 });
        s.x1.visible = true;
        showPop(s.x2, a.since(20) - 0.1, 0.2);
        if (a.since(20) > 0.1 && a.since(20) < 0.3) a.fx.shake = 0.6;
        if (lt < 0.22) a.fx.glitch = 0.15;
      },
    },
    {
      at: 21, set: 'warp',
      update(lt, a) {
        const s = a.set;
        const f = clamp01(a.since(29) / 1.4);
        moveCamera(s.camera, { from: [0, 2.2, 7.6], to: [-0.2, 2.1, 6.0], lookFrom: [0, 2.2, 0], k: lt / a.dur });
        s.camera.rotateZ(Math.sin(a.t * 1.3) * 0.03 + f * 0.06 * Math.sin(a.t * 2.1));
        const spin = lt * 0.6 + Math.max(0, a.since(25)) * 2.5 + Math.max(0, a.since(29)) ** 2 * 6;
        s.clock.userData.tex.redraw(spin / 12, spin, ease(f));
        s.minis.forEach((m) => {
          m.position.y += Math.sin(a.t + m.userData.ph) * 0.003;
          m.rotation.z = a.t * 0.4 + m.userData.ph;
          if (m.userData.i === Math.floor(a.t * 10) % 7) m.userData.tex.redraw(a.t + m.userData.ph, a.t * 6, f);
        });
        a.fx.tint = [1 - f * 0.25, 1 - f * 0.3, 1];
        a.fx.sat = 1 - f * 0.25;
        s.buck.update(a.t, { talk: a.talk, expr: [[0, 'smug'], [a.cue(29), 'dizzy']], pose: [[0, 'idle'], [a.cue(25), 'point']] }, s.camera);
      },
    },
    {
      at: 34, set: 'table',
      update(lt, a) {
        const s = a.set;
        moveCamera(s.camera, { from: [0, 3.6, 6.2], to: [0.2, 3.1, 5.0], lookFrom: [0, 1.6, 0], k: lt / a.dur });
        s.cashUp.visible = s.chipUp.visible = false;
        const cashIn = a.since(38);
        s.cash.visible = cashIn >= 0;
        const swap = a.since(43);
        if (swap < 0) {
          s.cash.position.y = 1.17 + Math.max(0, 1 - cashIn / 0.25) * 1.5;
          s.cash.rotation.y = Math.max(0, 1 - cashIn / 0.25) * 2;
          s.cash.scale.setScalar(1);
        } else {
          const k = clamp01(swap / 0.3);
          s.cash.scale.setScalar(Math.max(0.0001, 1 - k));
          s.cash.rotation.y = k * 6;
          s.cash.position.y = 1.17 + k * 0.8;
        }
        s.stacks.forEach((st, i) => showPop(st, swap - i * 0.12, 0.25));
        if (swap >= 0 && swap < 0.2) a.fx.shake = 0.4;
        s.buck.update(a.t, { talk: a.talk, expr: [[0, 'smug'], [a.cue(43), 'happy']], pose: [[0, 'hold'], [a.cue(40), 'point']] }, s.camera);
      },
    },
    {
      at: 44, set: 'table',
      update(lt, a) {
        const s = a.set;
        moveCamera(s.camera, { from: [0, 2.6, 6.4], to: [0, 2.5, 5.6], lookFrom: [0, 2.3, 0.5], k: lt / a.dur });
        s.cash.visible = false;
        s.stacks.forEach((st) => { st.visible = true; st.scale.setScalar(1); });
        s.cashUp.visible = s.chipUp.visible = true;
        s.cashUp.rotation.z = Math.sin(a.t * 2) * 0.06;
        s.chipUp.rotation.z = a.t * 0.8;
        s.cashUp.position.y = 2.5 + Math.sin(a.t * 2.2) * 0.05;
        s.chipUp.position.y = 2.5 + Math.sin(a.t * 2.2 + 1) * 0.05;
        s.buck.update(a.t, { talk: a.talk, expr: 'smug', pose: 'idle' }, s.camera);
      },
      hud(ctx, t, a) {
        const { W, H } = a;
        const drop = ease(clamp01((t - a.at(48)) / 0.6));
        gauge(ctx, W * 0.3, H * 0.33, H * 0.11, 0.92, { label: 'PAIN: CASH', appear: (t - a.at(45)) / 0.25 });
        gauge(ctx, W * 0.7, H * 0.33, H * 0.11, lerp(0.92, 0.12, drop), { label: 'PAIN: CHIPS', appear: (t - a.at(46)) / 0.25 });
      },
    },
    {
      at: 52, set: 'slot',
      update(lt, a) {
        const s = a.set;
        const ev = a.since(60);
        moveCamera(s.camera, { from: [-0.6, 2.4, 9], to: [0.2, 2.3, 6.6], lookFrom: [0.4, 2.3, -0.6], k: lt / a.dur });
        s.machine.userData.bulbs.chase(a.t, 8);
        s.machine.userData.set({ reels: [0, 2, 4], eyes: ev >= 0 && ev < 0.9, bet: '', win: '' });
        s.winner.visible = false;
        s.conf.visible = false;
        s.coins.forEach((c) => { c.visible = false; });
        s.notes.forEach((n) => { n.visible = false; });
        s.shadow.material.opacity = ev >= 0 ? lerp(0.15, 0.6, clamp01(ev / 0.3)) : 0.15;
        s.red.intensity = ev >= 0 ? 30 : 10;
        if (ev >= 0) {
          a.fx.tint = [1.15, 0.7, 0.7];
          a.fx.flash = Math.max(0, 0.45 - ev * 3);
          a.fx.shake = Math.max(0, 1 - ev * 2);
          if (ev < 0.25) a.fx.glitch = 0.5;
        }
        s.buck.update(a.t, { talk: a.talk, expr: [[0, 'smug'], [a.cue(60), 'shock']], pose: [[0, 'idle'], [a.cue(54), 'point']] }, s.camera);
      },
    },
    {
      at: 61, set: 'slot',
      update(lt, a) {
        const s = a.set;
        moveCamera(s.camera, { from: [1.3, 2.25, 3.2], to: [1.3, 2.2, 2.5], lookFrom: [1.3, 2.18, 0], k: lt / a.dur });
        const spin = a.since(62);
        const stops = [a.at(65) - a.at(62) + 0.1, a.at(66) - a.at(62) + 0.1, a.at(67) - a.at(62) - 0.05];
        const target = [1, 2, 3];
        const reels = target.map((tg, i) => (spin < 0 ? [0, 2, 4][i] : tg + Math.max(0, stops[i] - spin) * 16));
        s.machine.userData.set({ reels, bet: spin >= 0 ? '$1.00' : '', win: a.since(67) >= 0 ? '$0.50' : '', eyes: false });
        s.machine.userData.bulbs.chase(a.t, 12);
        s.red.intensity = 10;
        s.shadow.material.opacity = 0.15;
      },
    },
    {
      at: 69, set: 'slot',
      update(lt, a) {
        const s = a.set;
        const cz = a.since(73);
        moveCamera(s.camera, { from: [-0.2, 2.6, 8.2], to: [0.2, 2.5, 7.0], lookFrom: [0.4, 2.5, -0.6], k: lt / a.dur });
        s.machine.userData.set({ reels: [1, 2, 3], bet: '$1.00', win: '$0.50', eyes: false });
        s.machine.userData.bulbs.blink(a.t, cz >= 0 ? 14 : 6);
        s.winner.visible = cz >= 0;
        if (cz >= 0) { s.winner.setGlow(Math.floor(a.t * 8) % 2 ? 3.5 : 1.2); s.winner.scale.setScalar(pop(clamp01(cz / 0.25))); }
        s.conf.visible = cz >= 0;
        if (cz >= 0) s.conf.update(cz, new THREE.Vector3(1.3, 3.6, 0));
        s.coins.forEach((c) => {
          const u = c.userData, tt = Math.max(0, cz - u.d);
          c.visible = cz - u.d >= 0;
          c.position.set(1.3 + u.v.x * tt, Math.max(0.05, 0.9 + u.v.y * tt - 4.9 * tt * tt), 0.4 + u.v.z * tt * 0.5);
          c.rotation.set(tt * u.s, tt * u.s * 0.7, 0);
        });
        const mu = a.since(75);
        s.notes.forEach((n) => {
          const tt = mu - n.userData.i * 0.15;
          n.visible = tt >= 0;
          n.position.set(0.5 + n.userData.i * 0.45, 3.2 + tt * 1.2, 0.8);
          n.rotation.z = Math.sin(tt * 6 + n.userData.i) * 0.3;
          n.scale.setScalar(pop(clamp01(tt / 0.2)));
        });
        s.red.intensity = cz >= 0 ? 4 + 5 * (Math.floor(a.t * 10) % 2) : 10;
        if (cz >= 0) {
          a.fx.shake = 0.35 + Math.max(0, 0.6 - cz);
          a.fx.sat = 1.15; a.fx.bloom = 1.05;
          a.fx.flash = Math.max(0, 0.4 - cz * 2);
          for (const i of [74, 75]) { const k = a.since(i); if (k >= 0 && k < 0.15) a.fx.flash = Math.max(a.fx.flash, 0.45 - k * 3); }
        }
        s.buck.update(a.t, { talk: a.talk, expr: [[0, 'neutral'], [a.cue(73), 'excited']], pose: [[0, 'idle'], [a.cue(73), 'cheer']] }, s.camera);
      },
    },
    {
      at: 80, set: 'slot',
      update(lt, a) {
        const s = a.set;
        moveCamera(s.camera, { from: [-1.2, 2.2, 5.0], to: [-1.3, 2.2, 4.4], lookFrom: [-0.9, 2.1, 0], k: lt / a.dur });
        s.winner.visible = true; s.winner.setGlow(1.0);
        s.conf.visible = true; s.conf.update(1.4, new THREE.Vector3(1.3, 3.6, 0));
        s.notes.forEach((n) => { n.visible = false; });
        a.fx.sat = 0.12; a.fx.bloom = 0.3; a.fx.tint = [0.9, 0.92, 1.0];
        if (lt < 0.12) a.fx.flash = 0;
        const l = a.since(84);
        if (l >= 0 && l < 0.25) a.fx.shake = 0.8;
        s.buck.update(a.t, { talk: a.talk, expr: 'sad', pose: [[0, 'cheer'], [0.15, 'idle']] }, s.camera);
      },
      hud(ctx, t, a) { popText(ctx, a.W, a.H, '-$0.50', t - a.at(84), { color: '#ff2a2a', size: 0.2, y: 0.24 }); },
    },
    {
      at: 87, set: 'disguise',
      update(lt, a) {
        const s = a.set;
        moveCamera(s.camera, { from: [-0.4, 2.4, 7.6], to: [0.1, 2.4, 6.2], lookFrom: [0.0, 2.6, 0], k: lt / a.dur });
        s.hero.rotation.y = Math.sin(a.t * 1.4) * 0.25;
        s.hero.position.y = 2.15 + Math.sin(a.t * 2) * 0.05;
        showPop(s.specs, a.since(92), 0.22);
        showPop(s.label, a.since(91) + 0.05, 0.3);
        s.label.setGlow(2.8);
        if (a.since(92) >= 0 && a.since(92) < 0.2) a.fx.shake = 0.4;
        s.buck.update(a.t, { talk: a.talk, expr: 'smug', pose: [[0, 'idle'], [a.cue(89), 'point']] }, s.camera);
      },
      hud(ctx, t, a) { cite(ctx, a.W, a.H, 'Study: Dixon et al. (2010), Addiction', (t - a.at(87)) / 0.3); },
    },
    {
      at: 96, set: 'body',
      update(lt, a) {
        const s = a.set;
        moveCamera(s.camera, { from: [0, 2.0, 6.6], to: [-0.1, 2.0, 5.6], lookFrom: [0.1, 2.0, 0], k: lt / a.dur });
        const bpm = bpmCurve(a)(a.t);
        const ph = (a.t * bpm) / 60 % 1;
        const beat = Math.exp(-ph * 8);
        s.heart.scale.setScalar(1 + beat * 0.18);
        s.glow.intensity = 5 + beat * 18;
        a.fx.tint = [1 + beat * 0.12, 1, 1];
        a.fx.bloom = 0.9 + beat * 0.4;
        s.buck.update(a.t, { talk: a.talk, expr: [[0, 'neutral'], [a.cue(99), 'excited']], pose: [[0, 'idle'], [a.cue(103), 'cheer']] }, s.camera);
      },
      hud(ctx, t, a) {
        const { W, H } = a;
        ecg(ctx, W * 0.6, H * 0.05, W * 0.36, H * 0.2, t, {
          bpm: bpmCurve(a), gain: (tt) => 0.55 + 0.45 * clamp01((tt - a.at(99)) / 0.6), appear: (t - a.at(97)) / 0.25, label: 'YOUR BODY',
        });
      },
    },
    {
      at: 105, set: 'trap',
      update(lt, a) {
        const s = a.set;
        const snapAt = a.duration - 0.75;
        const sn = a.t - snapAt;
        moveCamera(s.camera, { from: [-0.4, 1.8, 7.2], to: [0.4, 1.1, 4.0], lookFrom: [0.2, 0.9, 0.3], lookTo: [0.6, 0.6, 0.3], k: lt / (snapAt - (a.t - lt)) });
        s.buck.group.position.x = lerp(-2.6, -1.7, ease(clamp01(lt / 2.2)));
        s.trap.userData.pivot.rotation.z = sn < 0 ? Math.PI : Math.PI * (1 - ease(clamp01(sn / 0.07)));
        s.trap.userData.bait.position.y = 0.42 + (sn > 0 ? Math.min(1.2, sn * 5) : Math.sin(a.t * 3) * 0.03);
        s.trap.userData.bait.rotation.y = sn > 0 ? sn * 20 : a.t;
        if (sn >= 0) { a.fx.flash = Math.max(0, 0.8 - sn * 4); a.fx.shake = Math.max(0, 1.3 - sn * 2.5); }
        if (sn > 0.4) a.fx.tint = [0, 0, 0];
        s.buck.update(a.t, { talk: a.talk, expr: sn >= 0 ? 'shock' : 'neutral', look: 1, pose: 'idle' }, s.camera);
      },
    },
  ],
};
