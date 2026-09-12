import { cpSync, copyFileSync, readdirSync, rmSync, statSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const dist = resolve(root, 'dist');
const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm';

execFileSync(npm, ['exec', 'vite', '--', 'build'], { cwd: root, stdio: 'inherit' });
copyFileSync(join(root, '.nojekyll'), join(dist, '.nojekyll'));
copyFileSync(join(root, 'portfolio-manifest.json'), join(dist, 'portfolio-manifest.json'));
copyFileSync(join(root, 'info.html'), join(dist, 'info.html'));
// Retain source media locally, but publish only the portfolio and site assets.
cpSync(join(root, 'web-media'), join(dist, 'web-media'), {
  recursive: true,
  filter: source => !['задний фон', 'background'].includes(basename(source).normalize('NFC')),
});

function removeJunk(folder) {
  for (const name of readdirSync(folder)) {
    const path = join(folder, name);
    if (name === '.DS_Store' || name.startsWith('._')) {
      rmSync(path, { force: true, recursive: true });
    } else if (statSync(path).isDirectory()) {
      removeJunk(path);
    }
  }
}

removeJunk(dist);
execFileSync(process.execPath, [join(root, 'verify-dist.mjs')], { cwd: root, stdio: 'inherit' });
let bytes = 0;
function measure(folder) {
  for (const name of readdirSync(folder)) {
    const path = join(folder, name);
    if (statSync(path).isDirectory()) measure(path);
    else bytes += statSync(path).size;
  }
}
measure(dist);
console.log(`OK → dist/: ${(bytes / 1024 / 1024).toFixed(0)} МБ`);
