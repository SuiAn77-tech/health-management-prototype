// Keep the exported SVG vectors. Extract embedded photographs without re-encoding them.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const out = path.join(root, 'assets', 'screens');
fs.mkdirSync(out, { recursive: true });
const sources = {
  home: ['首页未打卡.svg', [20, 0, 390, 1173]],
  homeDone: ['首页已打卡.svg', [20, 0, 390, 1176]],
  report: ['诱因.svg', [20, 0, 390, 1253.75]],
  journal: ['皮肤影像日志与时间轴.svg', [20, 0, 390, 1447]],
  plan: ['档案.svg', [20, 0.27, 390, 1294.71]],
  checkin: ['打卡页面.svg', [39, 13, 388, 1358.94]],
};
for (const [key, [source, box]] of Object.entries(sources)) {
  let svg = fs.readFileSync(path.join(root, 'figma-source', source), 'utf8');
  svg = svg.replace(/(?:xlink:)?href="data:image\/([^;]+);base64,([^"]+)"/g, (_, type, data) => {
    const bytes = Buffer.from(data, 'base64');
    const ext = type === 'jpeg' ? 'jpg' : type.replace('+xml', '');
    const name = `photo-${crypto.createHash('sha256').update(bytes).digest('hex').slice(0, 12)}.${ext}`;
    fs.writeFileSync(path.join(out, name), bytes);
    return `xlink:href="assets/screens/${name}"`;
  });
  svg = svg.replace(/<svg\b[^>]*>/, `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${box[2]}" height="${box[3]}" viewBox="${box.join(' ')}" fill="none">`);
  // Export shadow around the device is not part of the mobile page.
  if (key === 'checkin') svg = svg.replace('<g filter="url(#filter0_d_32_11681)">', '<g>');
  fs.writeFileSync(path.join(out, `${key}.svg`), svg);
  console.log(`${key}: ${box[2]} × ${box[3]}, SVG ${Buffer.byteLength(svg)} bytes`);
}
