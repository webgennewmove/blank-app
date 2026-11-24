import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const root = path.dirname(fileURLToPath(import.meta.url));

const args = Object.fromEntries(process.argv.slice(2).map((a) => a.replace(/^--/, '').split('=')));
const ep = args.ep ?? 'casino-hook';
const [W, H] = (args.size ?? '1920x1080').split('x').map(Number);
const fps = +(args.fps ?? 30);
const outFile = path.resolve(root, args.out ?? `out/${ep}-${W}x${H}.mp4`);
const stills = args.stills?.split(',').map(Number);

const types = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!p.startsWith(root) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': types[path.extname(p)] ?? 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const port = server.address().port;

const voice = path.join(root, 'audio', ep, 'voice.mp3');
const pcm = spawnSync('ffmpeg', ['-loglevel', 'error', '-i', voice, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], { maxBuffer: 1 << 28 }).stdout;
const samples = new Int16Array(pcm.buffer, pcm.byteOffset, pcm.length / 2);
const hop = 16000 / 60;
const rms = [];
for (let i = 0; i + hop <= samples.length; i += hop) {
  let acc = 0;
  for (let j = Math.floor(i); j < Math.floor(i + hop); j++) acc += (samples[j] / 32768) ** 2;
  rms.push(Math.sqrt(acc / hop));
}
const ref = [...rms].sort((x, y) => x - y)[Math.floor(rms.length * 0.95)] || 1;
const env = rms.map((v) => +Math.min(1, v / ref).toFixed(3));

const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 800, height: 600 } });
await page.addInitScript((e) => { window.__env = e; }, env);
page.on('pageerror', (e) => console.error('page error:', e.message));
page.on('console', (m) => { if (m.type() === 'error') console.error('console:', m.text()); });
await page.goto(`http://127.0.0.1:${port}/engine/index.html?ep=${ep}&w=${W}&h=${H}`);
await page.waitForFunction(() => window.__ready, null, { timeout: 20000 });
const duration = await page.evaluate(() => window.__duration);
fs.mkdirSync(path.dirname(outFile), { recursive: true });

const grab = async (t) => Buffer.from((await page.evaluate((t) => window.__frame(t), t)).split(',')[1], 'base64');

if (stills) {
  for (const t of stills) {
    const f = outFile.replace(/\.mp4$/, `-t${t}.jpg`);
    fs.writeFileSync(f, await grab(t));
    console.log(f);
  }
} else {
  const script = await page.evaluate(() => window.__script);
  fs.writeFileSync(outFile.replace(/\.mp4$/, '.script.json'), JSON.stringify(script, null, 2));
  const mixSpec = await page.evaluate(() => window.__mix);
  const audio = ['-i', voice];
  if (mixSpec) {
    const dir = path.join(root, 'audio', ep);
    const sfxFile = (n) => ['wav', 'mp3'].map((x) => path.join(dir, 'sfx', `${n}.${x}`)).find((f) => fs.existsSync(f));
    const inputs = ['-i', voice, '-i', path.join(dir, 'music.mp3')];
    const graph = ['[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit[v1][v2]'];
    const mute = mixSpec.music.mutes.map(([a, b]) => `between(t,${a.toFixed(3)},${b.toFixed(3)})`).join('+') || '0';
    graph.push(`[1:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:${duration.toFixed(3)},volume='if(${mute},0,${mixSpec.music.gain})':eval=frame[m]`);
    graph.push('[m][v2]sidechaincompress=threshold=0.04:ratio=5:attack=15:release=350[duck]');
    const labels = ['[v1]', '[duck]'];
    mixSpec.cues.forEach(([t, name, gain], i) => {
      inputs.push('-i', sfxFile(name));
      graph.push(`[${i + 2}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=${gain},adelay=${Math.max(0, Math.round(t * 1000))}:all=1[c${i}]`);
      labels.push(`[c${i}]`);
    });
    graph.push(`${labels.join('')}amix=inputs=${labels.length}:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,apad=whole_dur=${duration.toFixed(3)}[out]`);
    const mixed = outFile.replace(/\.mp4$/, '.mix.wav');
    const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', ...inputs, '-filter_complex', graph.join(';'), '-map', '[out]', mixed], { stdio: 'inherit' });
    if (r.status !== 0) throw new Error('audio mix failed');
    audio[1] = mixed;
  }
  if (args.remux) {
    const src = path.resolve(root, args.remux);
    spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', src, ...audio, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', outFile], { stdio: 'inherit' });
    console.log(`remuxed: ${outFile}`);
    await browser.close(); server.close(); process.exit(0);
  }
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    ...audio, '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-maxrate', '14M', '-bufsize', '28M', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k', '-af', 'apad', '-shortest', '-movflags', '+faststart', outFile], { stdio: ['pipe', 'inherit', 'inherit'] });
  const frames = Math.ceil(duration * fps);
  const t0 = Date.now();
  for (let i = 0; i < frames; i++) {
    const buf = await grab(i / fps);
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    if (i % 60 === 0) console.log(`frame ${i}/${frames} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  console.log(`done: ${outFile} (${duration.toFixed(1)}s)`);
}
await browser.close();
server.close();
