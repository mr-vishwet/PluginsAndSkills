# Reference — App Store Asset Generation

## Exact store dimensions

| Asset | Store | Final px (deliver) | Accepted alternates | Author canvas (logical) | render.sh FINAL args |
|---|---|---|---|---|---|
| Featured Graphic (banner) | Google Play | **1024 × 500** | PNG or JPEG, ≤ 15 MB | 1024 × 500 | `1024 500` |
| Header Asset | App Store (iOS) | **5244 × 2950** | 3840 × 1646 | 2622 × 1475 | `5244 2950` (or `3840 1646`) |
| Search Results Asset | App Store (iOS) | **3840 × 2560** | 5244 × 2950, 1920 × 1280 | 1920 × 1280 | `3840 2560` (or `1920 1280`) |

Author at the logical canvas, capture at `--force-device-scale-factor=2`, then resample to the exact final px. PNG is the primary deliverable; also emit a JPEG (quality 92) — both are accepted and stay well under 15 MB.

## render.sh recipes

```bash
S=~/.qoder/skills/app-store-assets
# Featured graphic (1024x500)
bash $S/scripts/render.sh  work/featured.html  1024 500  out/FeaturedGraphic_1024x500  1024 500
# iOS header (5244x2950)
bash $S/scripts/render.sh  work/header.html     2622 1475 out/Header_5244x2950         5244 2950
# iOS search results (3840x2560)
bash $S/scripts/render.sh  work/search.html     1920 1280 out/SearchResults_3840x2560  3840 2560
```

`work/` is a scratch dir next to the copies of `logo.png` / `screenshot.jpg` so relative `url(...)` paths resolve.

## Theme extraction (adapt to the pointed-at app)

Do not hardcode a brand. Pull the theme from the target project:

1. **Colors** — find the palette file (e.g. Flutter `lib/src/core/constants/colors.dart`, iOS `Assets.xcassets`, Android `colors.xml`, web `:root`/Tailwind config). Map to tokens:
   - `--brand` = primary/brand color; `--brand-dark` = darker variant (pressed/eyebrow text).
   - `--accent1` / `--accent2` = the two ends of the brand gradient (headline highlight, glow).
   - `--ink` = primary text; `--muted` = secondary text.
   - `--bg1/2/3` = a light tint ramp of the brand for the background (or reuse the app's scaffold background).
2. **Fonts** — reuse the app's display + body faces. If they are web-font-loadable, add a Google Fonts `<link>`; otherwise reference bundled `@font-face` files placed in `work/`. The templates default to Playfair Display (serif) + Inter (sans) — swap to the app's real faces.
3. **Logo** — copy the app icon (square, ≥ 512 px) to `work/logo.png`.
4. **Screenshot (optional)** — copy one representative app screen to `work/screenshot.jpg`; it renders as a faint, gradient-masked texture behind the copy. Keep opacity low (≤ 0.17) so text stays crisp.
5. **Copy** — eyebrow (short category tagline), a 2-line headline, one value sub-line, and 2–3 feature pills. Keep the SAME copy across featured/header/search for a consistent listing.

## Safe-zone rules (critical)

- **Header**: the App Store product-page info card overlaps the **bottom ~45%** of the image on every device, and iPhone additionally crops to the **center width**. Therefore keep the icon + copy as one **horizontally-centered group in the upper band** (template uses `.center { height:1150px; align-items:center; top:0 }`). Put the app icon **beside** the copy (not stacked above) to minimize height. Verify by simulating a center-width crop:
  ```bash
  sips -c 2950 2884 header.png --out header_phoneCrop.png   # center ~55% width, full height
  ```
  All text and every pill must remain fully visible.
- **Search / Featured**: no device overlap, but keep copy inside generous side padding so nothing looks cramped.
- **Ghost screenshot**: use `background-size: 250% auto` + `background-position` to zoom past any baked-in marketing text in the screenshot, and a mask gradient so it fades at the edges. This prevents the screenshot's own headline from bleeding through and duplicating the real headline.

## Design quality bar

- Render at 2× then downscale for crisp glyph edges.
- White "spotlight" behind text over the texture guarantees contrast.
- Feature pills: translucent white pill, thin brand-tinted border, small leading icon, consistent set across all assets.
- Prefer 2–3 short feature pills over long sentences.
