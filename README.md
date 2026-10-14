# pxl_head portfolio

Source files for photographer and videographer pxl_head's portfolio. [View the live website](https://pxl-head.github.io/pxl-head-portfolio/).

## Local development

Requires Node.js 20.19+ or 22.12+ and Python 3.

```sh
npm ci
npm run dev
```

## Checks and build

```sh
npm run check
npm run build
```

`npm run check` checks the photography catalogue against `portfolio-manifest.json`. The build repeats this check, creates `dist/` and validates the base URL, Unicode paths and the file signatures of all 485 WebP images.

GitHub Pages serves the site at `/pxl-head-portfolio/`, as configured in `vite.config.mjs`. The `main` branch contains the finished static site; the `source` branch holds the source files.

Photographs, the logo and other original materials may not be reused without permission from the rights holder.
