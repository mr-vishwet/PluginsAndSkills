// Run this as the page function of a browser evaluate call and save the result
// to a file; the payload is large and does not belong in conversation context.
//
// It reports what the page renders. `vars` is the declared token set and is
// included only so the rendered census can be compared against it.
() => {
  const PROPS = ['backgroundColor', 'color', 'fontFamily', 'fontSize', 'fontWeight',
    'lineHeight', 'letterSpacing', 'borderTopLeftRadius', 'padding', 'borderTopWidth',
    'borderTopColor', 'boxShadow', 'textTransform'];

  const vars = {};
  for (const sheet of document.styleSheets) {
    let rules;
    try { rules = sheet.cssRules; } catch { continue; }   // cross-origin sheets
    for (const r of rules) {
      if (!r.style) continue;
      for (const p of r.style) {
        if (!p.startsWith('--')) continue;
        const v = r.style.getPropertyValue(p).trim();
        if (v && !(p in vars)) vars[p] = v;
      }
    }
  }

  const computed = (el) => {
    const c = getComputedStyle(el), o = {};
    for (const k of PROPS) o[k] = c[k];
    return o;
  };
  const els = {};
  for (const sel of ['html', 'body', 'h1', 'h2', 'h3', 'h4', 'p', 'a', 'button']) {
    const e = document.querySelector(sel);
    if (e) els[sel] = computed(e);
  }

  const tally = (o, k) => { o[k] = (o[k] || 0) + 1; };
  const radii = {}, bgs = {}, colors = {}, fonts = {}, weights = {};
  for (const e of document.querySelectorAll('*')) {
    const r = e.getBoundingClientRect();
    if (!r.width || !r.height) continue;              // skip unrendered nodes
    const c = getComputedStyle(e);
    if (c.borderTopLeftRadius !== '0px') tally(radii, c.borderTopLeftRadius);
    if (c.backgroundColor !== 'rgba(0, 0, 0, 0)' && c.backgroundColor !== 'transparent') tally(bgs, c.backgroundColor);
    tally(colors, c.color);
    tally(fonts, c.fontFamily);
    if (/^(H[1-6]|P|LI|SPAN|BUTTON)$/.test(e.tagName)) tally(weights, c.fontSize + '/' + c.fontWeight);
  }

  const top = (o, n = 16) => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, n);
  const hrefs = [...new Set([...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')))]
    .filter(h => h && !/^mailto|^tel|^#/.test(h));
  const nav = [...document.querySelectorAll('nav a, header a, footer a')]
    .map(a => ({ t: a.textContent.trim().slice(0, 30), h: a.getAttribute('href') }))
    .filter(x => x.t);
  const media = [...document.querySelectorAll('img,video')].slice(0, 15)
    .map(m => ({ tag: m.tagName, alt: (m.alt || '').slice(0, 40), w: m.naturalWidth || m.videoWidth, h: m.naturalHeight || m.videoHeight }));

  return {
    url: location.href, title: document.title,
    viewport: { w: innerWidth, h: innerHeight }, docHeight: document.body.scrollHeight,
    vars, els,
    radii: top(radii), bgs: top(bgs), colors: top(colors),
    fonts: top(fonts, 6), typeScale: top(weights, 20),
    links: hrefs, nav, media,
  };
};
