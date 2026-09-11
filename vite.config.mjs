import { createReadStream, statSync } from 'node:fs';
import { resolve, sep } from 'node:path';
import { defineConfig } from 'vite';

export default defineConfig({
  base: '/pxl-head-portfolio/',
  plugins: [{
    name: 'portfolio-apostrophe-paths',
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        if (!request.url?.startsWith('/web-media/') || !/%27/i.test(request.url)) {
          next();
          return;
        }
        const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
        const root = resolve(process.cwd());
        const file = resolve(root, `.${pathname}`);
        if (!file.startsWith(`${root}${sep}`)) {
          next();
          return;
        }
        try {
          if (!statSync(file).isFile()) throw new Error('not a file');
          response.setHeader('Content-Type', 'image/webp');
          createReadStream(file).pipe(response);
        } catch {
          next();
        }
      });
    },
  }],
});
