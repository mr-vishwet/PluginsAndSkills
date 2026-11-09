---
name: app-store-assets
description: Generate app-store marketing graphics — Google Play Featured Graphic (banner, 1024x500), iOS App Store Header Asset (5244x2950 / 3840x1646), and Search Results Asset (3840x2560 / 5244x2950 / 1920x1280) — at exact store dimensions, adapting the theme (colors, fonts, logo, screenshots) of the app/project currently pointed at. Renders HTML through headless Chrome and resamples with sips. Use when the user asks to create or refresh a store banner, featured graphic, header asset, search results asset, listing artwork, or "app store assets", or asks to match a listing to an app's branding.
---

# App Store Assets

Generate pixel-exact store marketing graphics from the target app's own branding. The pipeline is: **extract theme → fill a template → render at 2× → resample to exact px → verify safe zone → deliver PNG + JPEG.**

## When to use

- The user asks for a store **banner / Featured Graphic**, iOS **Header Asset**, or **Search Results Asset**.
- The user wants listing artwork to match an app's existing branding/screenshots.

## Exact dimensions (deliver at these)

| Asset | Final px | Author canvas | Accepted alternates |
|---|---|---|---|
| Featured Graphic (Play) | 1024 × 500 | 1024 × 500 | PNG/JPEG ≤ 15 MB |
| Header (iOS) | 5244 × 2950 | 2622 × 1475 | 3840 × 1646 |
| Search Results (iOS) | 3840 × 2560 | 1920 × 1280 | 5244 × 2950, 1920 × 1280 |

Always render the page at `--force-device-scale-factor=2` and resample down to the exact final px (crisp text). Emit both `.png` and `.jpg`.

## Workflow

Copy this checklist and track progress:

```
- [ ] 1. Confirm which asset(s) + target app/project
- [ ] 2. Extract theme (colors, fonts, logo, optional screenshot) from the project
- [ ] 3. Set up work/ dir; copy logo.png + screenshot.jpg; write copy
- [ ] 4. Fill the matching template's :root tokens + content
- [ ] 5. Render via scripts/render.sh to exact dimensions
- [ ] 6. Verify (header: simulate center-width crop; all text/pills visible)
- [ ] 7. Deliver PNG + JPEG to the app-listing folder; report sizes
```

### 1–2. Scope + theme

Identify the target project and pull its real branding — never invent a palette. See [reference.md](reference.md) "Theme extraction" for where to look (Flutter `colors.dart`, iOS `Assets.xcassets`, Android `colors.xml`, web tokens) and how to map to the `--brand / --accent1 / --accent2 / --ink / --muted / --bg*` tokens used by every template.

### 3. Working directory

Create a scratch `work/` folder (inside the project, e.g. `<project>/.todo/store-assets/`) and copy assets next to the HTML so relative `url(...)` resolves:
- `work/logo.png` — the app icon (square, ≥ 512 px).
- `work/screenshot.jpg` — optional; one representative screen used as a faint masked texture.

Keep the **same copy** (eyebrow, headline, sub-line, feature pills) across all three assets for a consistent listing.

### 4. Fill a template

Start from the closest template and edit only the `:root` block and the body copy:
- Featured / banner → [templates/featured.html](templates/featured.html)
- iOS header → [templates/header.html](templates/header.html)
- Search results → [templates/search.html](templates/search.html)

Copy the template into `work/`, then replace placeholder text ("Your tagline eyebrow", "Short punchy headline here", "Feature one/two/three") and the theme hex values.

### 5. Render

```bash
S=~/.qoder/skills/app-store-assets
bash $S/scripts/render.sh work/featured.html 1024 500   out/FeaturedGraphic_1024x500   1024 500
bash $S/scripts/render.sh work/header.html   2622 1475  out/Header_5244x2950           5244 2950
bash $S/scripts/render.sh work/search.html   1920 1280  out/SearchResults_3840x2560    3840 2560
```

`render.sh <html> <logicalW> <logicalH> <outPrefix> [finalW finalH]` writes `<outPrefix>.png` and `<outPrefix>.jpg`. Requires Google Chrome (or chromium) and macOS `sips`.

### 6. Verify the header safe zone (critical)

The App Store info card covers the bottom ~45% of the header on all devices, and iPhone crops to the center width. The header template already places the icon **beside** the copy as a centered group in the upper band. Confirm nothing is stripped:

```bash
sips -c 2950 2884 out/Header_5244x2950.png --out /tmp/header_phoneCrop.png
```

Open `/tmp/header_phoneCrop.png` — the icon, headline, sub-line, and **every** pill must be fully visible. If any pill is clipped, reduce `h1`/`.pill` font sizes or shorten the sub-line, then re-render.

### 7. Deliver

Copy the final PNG + JPEG to the app-listing folder the user uses (e.g. `.../App Listing/Android` for the featured graphic, `.../App Listing/iOS` for header/search). Report each file's size and confirm each is ≤ 15 MB.

## Notes

- The Write/SearchReplace tools are scoped to the workspace; author HTML inside the project (e.g. `.todo/`), then use Bash (`cp`) to place finals in an external Documents folder.
- For the faint screenshot texture, keep `opacity` ≤ 0.17 and use `background-size: 250% auto` so any baked-in text in the screenshot doesn't bleed through behind the real headline.
- More detail (dimension alternates, theme-token mapping, quality bar) is in [reference.md](reference.md).
