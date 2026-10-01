# pxl_head — Portfolio

A personal portfolio for photographer and videographer pxl_head, with a bespoke interface for Photo, Video and Sites. I designed and built the website myself with Codex in ChatGPT.

## Features

- A bespoke interface built around three areas of work: Photo, Video and Sites.
- Photography projects arranged in thematic collections and presented in responsive galleries.
- Dedicated video project pages and a catalogue of websites I have created.
- Russian and English versions, with the language preference saved in the browser.
- Images shown in their original proportions, with a restrained layout that gives the work room to breathe.
- SEO metadata, a sitemap and layouts adapted for desktop and mobile.

## Technology

Static HTML, CSS and JavaScript. A manifest defines the project catalogue, and the production site is published through GitHub Pages.

## Live website

[View the portfolio](https://pxl-head.github.io/pxl-head-portfolio/).

## Repository structure

- The `source` branch contains the source files, build tools and manifest generator.
- The `main` branch contains the finished static site for GitHub Pages.
- `portfolio-manifest.json` describes the published projects and their media files.
- `assets/` and `web-media/` contain images, covers and videos.

## Local development

Work on the source files in the `source` branch:

```bash
git switch source
npm install
npm run check
npm run build
npm run verify
```

## Deployment

The production build prepares the static files for the `main` branch. GitHub Pages serves the public website.

## Authorship

I designed and built this website myself with Codex in ChatGPT.

## Rights and materials

Photographs, videos, texts and other original materials belong to their respective creators and are presented as part of this portfolio.
