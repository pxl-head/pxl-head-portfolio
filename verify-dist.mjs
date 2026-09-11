import { existsSync, readFileSync, statSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const dist = resolve(root, 'dist');
const expectedBase = '/pxl-head-portfolio/';

function fail(message) {
  throw new Error(`Проверка dist не пройдена: ${message}`);
}

const indexPath = join(dist, 'index.html');
if (!existsSync(indexPath)) fail('нет index.html');
const html = readFileSync(indexPath, 'utf8');
if (!html.includes(`${expectedBase}assets/`)) {
  fail(`ресурсы Vite не используют ${expectedBase}`);
}
if (/\b(?:src|href)=["']\/assets\//.test(html)) {
  fail('найдена ссылка на корневой /assets/');
}

for (const required of ['robots.txt', 'sitemap.xml', 'portfolio-manifest.json']) {
  if (!existsSync(join(dist, required))) fail(`нет ${required}`);
}

const manifest = JSON.parse(readFileSync(join(dist, 'portfolio-manifest.json'), 'utf8'));
const projects = manifest.projects || [];
const photoCount = projects.reduce((sum, project) => sum + project.files.length, 0);
if (projects.length !== 14 || photoCount !== 452) {
  fail(`ожидалось 14 кейсов и 452 фото, получено ${projects.length} и ${photoCount}`);
}

for (const project of projects) {
  const textValues = [project.title, project.group, project.dir, project.cover, ...project.files];
  if (textValues.some(value => value.normalize('NFC') !== value)) {
    fail(`Unicode-путь не в NFC: ${project.title}`);
  }
  for (const file of project.files) {
    const imagePath = join(dist, project.dir, file);
    if (!existsSync(imagePath) || !statSync(imagePath).isFile()) {
      fail(`нет фотографии ${project.dir}/${file}`);
    }
    const header = readFileSync(imagePath).subarray(0, 12);
    if (header.toString('ascii', 0, 4) !== 'RIFF' || header.toString('ascii', 8, 12) !== 'WEBP') {
      fail(`повреждён WebP ${project.dir}/${file}`);
    }
  }
}

console.log(`OK: dist проверен — ${projects.length} кейсов, ${photoCount} фото`);
