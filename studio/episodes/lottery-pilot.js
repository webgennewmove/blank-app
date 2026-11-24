import * as THREE from 'three';
import { createBuck } from '../engine/character.js';
import {
  makeStage, moveCamera, toon, rbox, textPanel, coin, coinStack, palm, sign, stamp, rng, popIn, clamp01,
} from '../engine/world.js';

function ticket() {
  const g = new THREE.Group();
  const body = toon(rbox(3.2, 1.7, 0.1, 0.05), '#ffd84d');
  g.add(body);
  const face = textPanel(3.05, 1.55, (c, W, H) => {
    c.fillStyle = '#e0242b'; c.fillRect(0, 0, W, H * 0.3);
    c.fillStyle = '#fff'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.font = `900 ${H * 0.22}px Inter`; c.fillText('LOTTO JACKPOT', W / 2, H * 0.16);
    const nums = [7, 14, 22, 31, 48];
    nums.forEach((n, i) => {
      const x = W * (0.14 + i * 0.18), y = H * 0.6;
      c.fillStyle = '#fff'; c.strokeStyle = '#151515'; c.lineWidth = H * 0.03;
      c.beginPath(); c.arc(x, y, H * 0.15, 0, Math.PI * 2); c.fill(); c.stroke();
      c.fillStyle = '#151515'; c.font = `900 ${H * 0.15}px Inter`; c.fillText(String(n), x, y + H * 0.01);
    });
    c.font = `800 ${H * 0.08}px Inter`; c.fillText('WINNER  WINNER  WINNER', W / 2, H * 0.9);
  });
  face.position.z = 0.056;
  g.add(face);
  return g;
}

function fallingCoins(scene, n, seed, { area = 9, depth = [-4, 1.5] } = {}) {
  const r = rng(seed);
  const coins = Array.from({ length: n }, () => {
    const c = coin();
    c.userData = { x: (r() - 0.5) * area, z: depth[0] + r() * (depth[1] - depth[0]), ph: r(), spin: 2 + r() * 4, sp: 2.5 + r() * 1.5 };
    scene.add(c);
    return c;
  });
  return (t, dir = -1) => {
    for (const c of coins) {
      const u = c.userData;
      const y = ((t * u.sp + u.ph * 10) % 10);
      c.position.set(u.x + (dir > 0 ? Math.sin(t + u.ph * 6) * 0.4 : 0), dir < 0 ? 8 - y : y - 1, u.z);
      c.rotation.set(t * u.spin, u.ph * 6, t * u.spin * 0.6);
    }
  };
}

export default {
  title: 'Lottery winners still go broke',
  shots: [
    {
      line: 'Winning the lottery does not save people from going *broke.*',
      build: ({ W, H }) => {
        const { scene, camera } = makeStage({ W, H, sky: ['#ff8a3d', '#ffe9a8'], ground: '#e7a457', fog: ['#ffd89a', 14, 60] });
        const buck = createBuck(THREE);
        buck.group.position.set(-1.1, 0, 0);
        scene.add(buck.group);
        const t = ticket();
        t.position.set(1.5, 1.6, -0.6);
        t.rotation.set(0, -0.35, 0.08);
        scene.add(t);
        const s1 = coinStack(14, { seed: 3 }); s1.position.set(2.9, 0, 0.6);
        const s2 = coinStack(8, { seed: 5 }); s2.position.set(-2.8, 0, 0.9);
        scene.add(s1, s2);
        const rain = fallingCoins(scene, 36, 7);
        return {
          scene, camera,
          update: (lt, { speaking, dur }) => {
            moveCamera(camera, { from: [0.4, 1.7, 8.5], to: [-0.2, 1.5, 6.4], lookFrom: [0.2, 1.4, 0], lookTo: [-0.1, 1.35, 0], k: lt / dur });
            t.position.y = 1.6 + Math.sin(lt * 2) * 0.06;
            rain(lt);
            buck.update(lt, { speaking, expr: 'smug', pose: [[0, 'idle'], [0.5, 'point']] }, camera);
          },
        };
      },
    },
    {
      line: 'Economists tracked thousands of *Florida* lottery winners.',
      build: ({ W, H }) => {
        const { scene, camera } = makeStage({ W, H, sky: ['#2fb8e8', '#d9f6ff'], ground: '#f2d8a0', fog: ['#cfefff', 16, 70] });
        const buck = createBuck(THREE);
        buck.group.position.set(-1.3, 0, 0.3);
        scene.add(buck.group);
        const s = sign('FLORIDA', { w: 3, h: 1.3, color: '#fff7e0', sub: 'LOTTERY WINNERS STUDY' });
        s.position.set(1.4, 0, -0.5);
        s.rotation.y = -0.2;
        scene.add(s);
        [[-4, -3, 1], [4.2, -2, 2], [-6, -6, 3], [6.5, -7, 4], [0, -9, 5], [-2.5, -12, 6]].forEach(([x, z, sd]) => {
          const p = palm(3 + (sd % 3) * 0.6, sd); p.position.set(x, 0, z); scene.add(p);
        });
        const sea = new THREE.Mesh(new THREE.PlaneGeometry(400, 120), new THREE.MeshBasicMaterial({ color: '#28a8d8' }));
        sea.rotation.x = -Math.PI / 2; sea.position.set(0, 0.02, -75);
        scene.add(sea);
        return {
          scene, camera,
          update: (lt, { speaking, dur }) => {
            moveCamera(camera, { from: [-2.2, 1.6, 7.2], to: [0.8, 1.6, 7.0], lookFrom: [-0.4, 1.5, 0], lookTo: [0.4, 1.5, 0], k: lt / dur });
            buck.update(lt, { speaking, expr: 'neutral', pose: [[0, 'idle'], [0.3, 'point']] }, camera);
          },
        };
      },
    },
    {
      line: 'People who won *$150,000* went bankrupt about as often as people who won under *$10,000.*',
      build: ({ W, H }) => {
        const { scene, camera } = makeStage({ W, H, sky: ['#5b6cff', '#c9d2ff'], ground: '#8fd18a', fog: ['#c9d2ff', 14, 60] });
        const buck = createBuck(THREE);
        scene.add(buck.group);
        const big = coinStack(34, { seed: 11 });
        big.position.set(-2.1, 0, -0.2);
        const small = coinStack(4, { seed: 12 });
        small.position.set(2.1, 0, -0.2);
        scene.add(big, small);
        const labels = [['$150K', -2.1, 3.05], ['$10K', 2.1, 0.75]].map(([txt, x, y]) => {
          const s = toon(rbox(1.4, 0.6, 0.08, 0.05), '#ffffff');
          const tp = textPanel(1.3, 0.55, (c, W, H) => {
            c.fillStyle = '#151515'; c.textAlign = 'center'; c.textBaseline = 'middle';
            c.font = `900 ${H * 0.62}px Inter`; c.fillText(txt, W / 2, H / 2, W * 0.95);
          });
          tp.position.z = 0.05;
          s.add(tp);
          s.position.set(x, y, 0);
          s.userData.y = y;
          scene.add(s);
          return s;
        });
        const stamps = [[-2.1, 1.5, 5], [2.1, 0.35, 14]].map(([x, y, at]) => {
          const st = stamp('BANKRUPT', { w: 1.9 });
          st.position.set(x, y, 0.9);
          st.userData.at = at;
          scene.add(st);
          return st;
        });
        return {
          scene, camera,
          update: (lt, { speaking, dur, cue }) => {
            moveCamera(camera, { from: [0, 2.0, 9.5], to: [0, 1.7, 7.8], lookFrom: [0, 1.5, 0], k: lt / dur });
            for (const st of stamps) {
              const k = clamp01((lt - cue(st.userData.at)) / 0.25);
              st.visible = k > 0;
              st.scale.setScalar(Math.max(0.001, popIn(k)) * (1 + (1 - k) * 1.2));
            }
            labels.forEach((l, i) => { l.position.y = l.userData.y + Math.sin(lt * 2 + i) * 0.05; });
            buck.update(lt, { speaking, expr: [[0, 'neutral'], [cue(14), 'shock']], pose: [[0, 'idle'], [cue(2), 'point'], [cue(14), 'shrug']] }, camera);
          },
        };
      },
    },
    {
      line: 'The money did not stop it. It just *delayed* it by a few years.',
      build: ({ W, H }) => {
        const { scene, camera } = makeStage({ W, H, sky: ['#6b3fa0', '#f0b6d6'], ground: '#5f4b8b', fog: ['#e0a9cf', 12, 55] });
        const buck = createBuck(THREE);
        buck.group.position.set(-1.4, 0, 0.4);
        scene.add(buck.group);
        const frame = toon(rbox(2.4, 2.8, 0.14, 0.08), '#ffffff');
        frame.position.set(1.4, 2.0, -0.5);
        frame.rotation.y = -0.2;
        scene.add(frame);
        const page = textPanel(2.2, 2.5, (c, W, H, year = 1) => {
          c.fillStyle = '#e0242b'; c.fillRect(0, 0, W, H * 0.25);
          c.fillStyle = '#fff'; c.textAlign = 'center'; c.textBaseline = 'middle';
          c.font = `900 ${H * 0.13}px Inter`; c.fillText('AFTER WIN', W / 2, H * 0.125);
          c.fillStyle = '#151515'; c.font = `900 ${H * 0.13}px Inter`; c.fillText('YEAR', W / 2, H * 0.42);
          c.font = `900 ${H * 0.36}px Inter`; c.fillText(String(year), W / 2, H * 0.7);
        });
        page.position.set(0, 0, 0.075);
        frame.add(page);
        const st = stamp('BANKRUPT', { w: 2.3 });
        st.position.set(0, -0.2, 0.09);
        frame.add(st);
        const pillar = toon(new THREE.CylinderGeometry(0.12, 0.12, 0.9, 10), '#7a5230');
        pillar.position.set(1.4, 0.45, -0.5);
        scene.add(pillar);
        let shown = 0;
        return {
          scene, camera,
          update: (lt, { speaking, dur, cue }) => {
            moveCamera(camera, { from: [0.6, 1.8, 8.6], to: [0.2, 1.7, 7.0], lookFrom: [0.1, 1.6, 0], k: lt / dur });
            const year = Math.min(5, 1 + Math.floor(Math.max(0, lt - cue(6)) / 0.45));
            if (year !== shown) { page.userData.tex.redraw(year); shown = year; }
            const k = clamp01((lt - (cue(6) + 0.9)) / 0.25);
            st.visible = k > 0;
            st.scale.setScalar(Math.max(0.001, popIn(k)) * (1 + (1 - k)));
            buck.update(lt, { speaking, expr: [[0, 'neutral'], [cue(8), 'sad']], pose: [[0, 'idle'], [cue(1), 'point'], [cue(8), 'shrug']] }, camera);
          },
        };
      },
    },
    {
      line: 'So why does sudden money *vanish* so fast?',
      tail: 1.2,
      build: ({ W, H }) => {
        const { scene, camera } = makeStage({ W, H, sky: ['#5a0814', '#e0443a'], ground: '#b5452e', fog: ['#c43a32', 10, 45] });
        const buck = createBuck(THREE);
        scene.add(buck.group);
        const r = rng(21);
        for (let i = 0; i < 14; i++) {
          const rock = toon(rbox(1 + r() * 2, 2 + r() * 6, 1 + r() * 2, 0.3), r() > 0.5 ? '#8f2a22' : '#a8382b');
          const a = (i / 14) * Math.PI - Math.PI;
          rock.position.set(Math.cos(a) * (9 + r() * 6), 0, -6 - r() * 10);
          rock.rotation.y = r() * 3;
          scene.add(rock);
        }
        const rise = fallingCoins(scene, 30, 22, { area: 10, depth: [-5, 1] });
        return {
          scene, camera,
          update: (lt, { speaking, dur }) => {
            moveCamera(camera, { from: [0, 1.4, 8.0], to: [0, 1.75, 4.6], lookFrom: [0, 1.4, 0], lookTo: [0, 1.75, 0], k: lt / dur });
            rise(lt, 1);
            buck.update(lt, { speaking, expr: 'smug', pose: [[0, 'idle'], [0.4, 'think']] }, camera);
          },
        };
      },
    },
  ],
};
