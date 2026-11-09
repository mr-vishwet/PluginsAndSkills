# Cardboard: the visual flow

Extracted from `https://www.cardboard.ai/` at viewport 531x593, document height 13930 px, using `scripts/page-flow.py`. Colours and type are viewport independent. Section order comes from the shipped HTML, which is the same markup the desktop layout renders.

## Brand system

- Background `#1a1a1a`, text `#d9d9d9`, strong text `#f5f5f5`, muted `#999`.
- Primary control is inverted: `#f4f4f4` fill with `#1a1a1a` text. Their brightest object is a light button, not a coloured one.
- Borders are translucent white rather than opaque grey: `#ffffff0f` subtle, `#ffffff29` strong, `#0a0a0a` hard.
- Surfaces step through `#2a2a2a` and `#404040`; focus ring `#a0a0a0`.
- The only chromatic accents in the rendered census: `#2680D9` on 73 elements, `#3CDDA7` on 48 elements. Blue for interactive, mint for success or live state.
- Display face Denton at weight 300: h1 `40px/300`, h2 `32px/300`. Body face Delight `16px/500`. UI and small text Geist or Inter `14px/400`. The ladder is the brand: large and thin, never large and bold.
- Radius token `8px`; 3, 4, 6, 8, 10 and 12 px all in use, plus full pills on chips.

## Pages, in funnel order

### `/`  Cardboard | AI Video Editor for Your Browser and Mac
Role: entry, product promise

> An agentic AI video editor in your browser and on your Mac. Describe your edit and Cardboard cuts, captions, reframes, and composes it.
- Opening line: **Make any video you can think of**
- Section order: Made with Cardboard -> Your first video in three steps -> Everything you need to make videos -> Make videos the way you do everything else -> Library -> Recent -> Your next video, made in Cardboard. Your next , made in Cardboard. -> Pricing for every stage of editing
- Actions: `Auto`, `Improve prompt`, `Launch Video`, `UGC`, `Explainer`, `Montage`, `Product Demo`, `Podcast Clip`

### `/pricing`  Pricing for Every Stage of Editing | Cardboard
Role: convert, plan choice

> Cardboard pricing plans for every stage of editing. From Lite on the Mac app to Pro, find the plan that fits your AI video editing workflow.
- Opening line: **Pricing for every stage of editing**
- Section order: Compare plans -> Frequently asked questions
- Actions: `Monthly`, `Annual Save up to 61 %`, `Get started`, `Can I cancel anytime?`, `Is there a free plan?`, `Can I change my plan later?`

### `/desktop`  Cardboard for Mac: The AI Video Editor for Your Mac
Role: native app install

> Drop in your footage, say what you want, and Cardboard edits it. Free to download, with the Lite plan included and your own Claude or Codex built in.
- Opening line: **The AI video editor for your Mac**
- Section order: Library -> Recent -> Cardboard for Mac comes with Lite, included. -> Faster editing, straight from your Mac. -> Made with Cardboard on the Mac -> Your first edit in three steps -> Use your own agents. -> Get started with one prompt.
- Actions: `Dashboard`, `Piece Runner launch`, `Makers documentary`, `M`, `GPT-6 Astra`, `Watch with sound 1:05`, `Do I need Claude or Codex?`, `Is Cardboard on Windows?`

### `/mcp`  Cardboard for ChatGPT and Claude
Role: agent surface, ChatGPT and Claude

> Edit video in ChatGPT or Claude. Attach your clips, say what you want, and Cardboard edits it.
- Opening line: **Your video editor, now in ChatGPT**
- Section order: How to connect -> What Cardboard can do in the chat -> Edit from your browser, desktop or phone. -> What users are asking -> Get started with one prompt. -> Frequently asked questions
- Actions: `ChatGPT`, `Claude`, `Launch video`, `Trendy edits`, `Effects`, `Product video`, `Talking heads`, `Vlogs`

### `/recipes`  AI video editing recipes and examples | Cardboard
Role: proof, outcomes you can make

> Make talking head videos, podcast clips, UGC ads, travel vlogs and product demos with AI editing recipes. Preview an edit, add your footage and make it yours.
- Opening line: **Recipes**
- Actions: `Remix`, `−`, `100 %`, `+`

### `/changelog`  Changelog | Cardboard
Role: momentum, shipping cadence

> The latest features, improvements, and fixes in the Cardboard AI video editor.
- Opening line: **What’s new in Cardboard**
- Section order: Edit Videos in ChatGPT and Claude -> Edit by asking -> No setup, no extra plan -> Finish in Cardboard -> YouTube, straight into your edit -> Faster Exports, Shareable Recipes, Photos to Video -> Faster, steadier exports -> Share a recipe
- Actions: `Edit Videos`, `Faster Exports`, `Meet Recipes`, `Any Footage`, `Now on`, `Reliable Exports`, `Fast Scrubbing`, `Canvas Text`

### `/hard-problems`  Hard problems in video editing | Cardboard
Role: engineering credibility

> Ten problems we have to solve to build the video editor that should exist, from a fast browser NLE and real-time collaboration to memory and version control.
- Opening line: **Hard problems**
- Section order: 01 High Performance NLE in the Browser -> 02 Collaboration -> 03 Multimodal Understanding -> 04 Better Context -> 05 Predicting Next Actions -> 06 Style References -> 07 Motion Graphics -> 08 Memory

### `/blog`  Blog | Cardboard
Role: voice and depth

> How we think about editing, the craft behind agentic video, and what we learn building Cardboard. Written by the team.
- Opening line: **Cuts & Notes**
- Section order: Match Cuts Explained: 2026 Guide

### `/careers`  We're hiring | Careers at Cardboard
Role: hiring

> We're a small, cracked team building the future of video editing. Open roles in design, engineering, content, and growth.
- Opening line: **Help build the editor that edits for you**
- Section order: Open roles 6 -> Think you can make Cardboard better? Show us.

### `/support`  Support: help with edits, exports and plans | Cardboard
Role: retention and trust

> Stuck on an edit, an export or your plan? Email humans@cardboard.ai and someone on the Cardboard team will get back to you.
- Opening line: **How can we help?**
- Section order: Email support -> Other places to look
- Actions: `Copy address`

## Reading the flow

The entry page makes the promise, proves it with output made inside the product, reduces risk with a three-step how-it-works, lists capability, then hands off to the free native app. Pricing is the only page carrying a billing decision and it shows no demo. `/desktop` and `/mcp` are the same engine framed by surface, which is how one product with three front doors keeps a single story. `/recipes` is the proof page and lists outcomes, not features. `/changelog`, `/blog`, `/hard-problems` and `/careers` are trust and hiring; `/hard-problems` is the one written for engineers, and it is the page a candidate should read before applying.
