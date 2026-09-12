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

for (const required of ['.nojekyll', 'robots.txt', 'sitemap.xml', 'portfolio-manifest.json']) {
  if (!existsSync(join(dist, required))) fail(`нет ${required}`);
}

const canonicalUrl = 'https://pxl-head.github.io/pxl-head-portfolio/';
for (const requiredSeo of [
  `<link rel="canonical" href="${canonicalUrl}">`,
  '<meta name="robots" content="index,follow,max-image-preview:large,max-video-preview:-1,max-snippet:-1">',
  '<meta property="og:site_name" content="pxl_head">',
  '<meta name="twitter:image:alt" content="Логотип pxl_head">',
]) {
  if (!html.includes(requiredSeo)) fail(`нет SEO-разметки: ${requiredSeo}`);
}

const structuredDataMatch = html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/);
if (!structuredDataMatch) fail('нет JSON-LD');
const structuredData = JSON.parse(structuredDataMatch[1]);
const structuredTypes = new Set(structuredData['@graph']?.map(item => item['@type']));
if (!structuredTypes.has('WebSite') || !structuredTypes.has('Person')) {
  fail('JSON-LD не описывает WebSite и Person');
}

const sitemap = readFileSync(join(dist, 'sitemap.xml'), 'utf8');
if (!sitemap.includes(`<loc>${canonicalUrl}</loc>`) || !/<lastmod>\d{4}-\d{2}-\d{2}<\/lastmod>/.test(sitemap)) {
  fail('sitemap.xml не содержит канонический URL и lastmod');
}

const manifest = JSON.parse(readFileSync(join(dist, 'portfolio-manifest.json'), 'utf8'));
const projects = manifest.projects || [];
const photoCount = projects.reduce((sum, project) => sum + project.files.length, 0);
if (projects.length !== 15 || photoCount !== 454) {
  fail(`ожидалось 15 кейсов и 454 фото, получено ${projects.length} и ${photoCount}`);
}

for (const videoName of ['Fantasy Of Poison II.mp4', 'Съемка свадьбы.mp4', 'BASIA.mp4']) {
  const requiredVideo = join(dist, 'web-media', 'Портфолио', 'Видео', videoName);
  if (!existsSync(requiredVideo) || !statSync(requiredVideo).isFile()) {
    fail(`нет видео ${videoName}`);
  }
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
