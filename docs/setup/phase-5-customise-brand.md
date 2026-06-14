---
phase: 5
title: "Customise Your Brand"
estimated_time: "30–60 minutes"
prerequisites: ["Phase 3 complete — all files created", "Phase 4 complete"]
outputs:
  - All brand colours updated to your palette
  - Brand name / handle updated in all files
  - Hashtags and CTA block updated
  - QR code image added to instagram/assets/
  - Educational content filled with your own methodology
---

# Phase 5 — Customise Your Brand

The pipeline runs with placeholder branding from Phase 3. This phase replaces every brand element with your own. Work through each section in order.

---

## 5.1 Colour Palette — Master Reference Table

All three generator files share the same colour variable names. Change these to match your brand. The table below shows the default values and what each colour controls.

| Constant | Default Value | Used For |
|---|---|---|
| `NAVY` | `#010E1F` | Main card background |
| `NAVY_S` | `#051830` | Slightly lighter background sections |
| `NAVY_L` | `#0A2545` | Panel fills, table rows |
| `GOLD` | `#F0C040` | Brand accent — headings, borders, highlights |
| `WHITE` | `#FFFFFF` | Primary text on dark backgrounds |
| `CREAM` | `#F0EEE8` | Secondary text, subheadings |
| `MUTED` | `#B8CFEA` | Muted info text, labels |
| `DIM` | `#6A8EB8` | Tertiary text, footnotes |
| `GREEN` | `#00E096` | Profit, positive numbers |
| `RED` | `#FF6B6B` | Loss, negative numbers |
| `AMBER` | `#FFA040` | Warning, neutral states |

These constants appear at the top of each generator file:

- `instagram/generate_status.py` — lines 20–31
- `instagram/generate.py` — lines 13–26
- `instagram/generate_edu.py` — lines 23–35

> 💡 TIP: If you want a different primary background (e.g. dark green `#0A1F0E` instead of navy), change `NAVY` in all three files. The same value for the same concept must match across files to maintain visual consistency.

---

## 5.2 Brand Name — Find and Replace

Replace the following strings in the files listed. Every occurrence must be updated.

| Current string | Replace with | File(s) |
|---|---|---|
| `VERA LEVEL FX` | `YOUR BRAND FX` | `generate.py`, `generate_edu.py` |
| `@veralevel.fx` | `@yourusername` | `generate.py`, `generate_edu.py` |
| `Vera Level FX` | `Your Brand FX` | `captions.py` (trust function) |
| `YourBrand FX` | Your brand name | `captions.py` (trust, edu pair quote) |
| `YourBrand` | Your brand name | `captions.py` (all `_CTA` and tags) |
| `veralevelFX` | `YourBrandFX` | `captions.py` (`TAGS` and `base_tags`) |

> 💡 TIP: Use VS Code's Find & Replace (`Ctrl+H`) with "Search in files" to find all occurrences at once. In VS Code: `Ctrl+Shift+H` to replace across multiple files.

---

## 5.3 Hashtags

In `instagram/captions.py`, find the `TAGS` constant (line 3) and replace with hashtags that match your brand and location:

```python
TAGS = (
    "#forex #forextrader #forextrading #algotrading #algorithmic "
    "#icmarkets #myfxbook #xauusd #gold #forexsignals "
    "#tradingstrategy #YOURCOUNTRY #investing#YOURCOUNTRY "
    "#financialfreedom #wealthbuilding #YourBrandFX "
    "#forexlifestyle #passiveincome #tradingresults"
)
```

Replace:
- `#YOURCOUNTRY` → your country hashtag (e.g. `#australia`, `#malaysia`, `#india`)
- `#YourBrandFX` → your brand hashtag
- Add niche hashtags specific to your trading style or instruments

> 💡 TIP: Instagram allows up to 30 hashtags per post. Research popular forex hashtags in your region — local hashtags often have better reach than oversaturated global ones.

---

## 5.4 CTA Block (Call to Action)

In `instagram/captions.py`, replace the `_CTA` constant with your own links:

```python
_CTA = (
    "\n\n📲 Live signals → https://t.me/YOUR_TELEGRAM_USERNAME"
    "\n🌐 Live account → https://YOUR_WEBSITE_OR_VERCEL_URL"
    "\n🏦 Open IC Markets account →"
    "\nhttps://icmarkets.com/global/en/?camp=YOUR_CAMP_ID"
)
```

Replace:
- `YOUR_TELEGRAM_USERNAME` → your Telegram username or channel link
- `YOUR_WEBSITE_OR_VERCEL_URL` → your website, Linktree, or Vercel app URL
- `YOUR_CAMP_ID` → your IC Markets IB campaign number (from your IB portal)

> ⚠️ WARNING: Include the full `https://` prefix on all URLs. Instagram only makes links tappable in captions if they include the protocol. `t.me/username` is not tappable — `https://t.me/username` is.

---

## 5.5 QR Code

Generate your IC Markets referral QR code:

1. Get your IC Markets IB referral URL — it looks like `https://icmarkets.com/global/en/?camp=XXXXXXX`
2. Go to [qr-code-generator.com](https://www.qr-code-generator.com) (free, no account needed)
3. Paste your referral URL
4. Download as PNG — choose at least **400×400 pixels**
5. Rename the file to `qr-icmarkets.jpg` (the pipeline expects this exact filename)
6. Save to `instagram/assets/qr-icmarkets.jpg`

> ✅ CHECKPOINT: Scan the QR code with your phone before committing. Confirm it opens your IC Markets referral URL in a browser.

> 💡 TIP: The pipeline resizes the QR code to ~154px on the final 1080px image. A higher-resolution source QR produces a sharper result. 400×400 or 600×600 is ideal.

---

## 5.6 Educational Content — Fill in Your Methodology

Edit `instagram/edu_content.py` and replace all placeholder content with your own trading methodology. This is the most time-consuming part — but it is also what makes your content authentic and valuable.

### 5.6.1 Five Risk Management Rules

For each rule in `RISK_RULES`, fill in:

| Field | What to write |
|---|---|
| `rule_num` | `"01"` through `"05"` — keep the numbering |
| `title` | Short rule title (3–6 words) |
| `body` | 2–3 sentences explaining the rule and why it matters |
| `example_account` | A representative account size (e.g. `3000`, `10000`) |
| `example_risk` | Dollar amount at risk per trade for that account size |
| `example_rr` | Your standard risk:reward ratio (e.g. `"1:2.5 RR"`) |
| `tag` | One-word category shown on the card (e.g. `"SIZING"`, `"PSYCHOLOGY"`) |

Example of a well-filled rule:

```python
{
    "rule_num": "01",
    "title": "Risk 1% Per Trade Maximum",
    "body": (
        "Every position is sized so that a full stop-loss hit equals exactly 1% of "
        "current balance. This means a 10-trade losing streak only costs 10% — "
        "recoverable. A 50% drawdown requires a 100% gain to recover. 1% per trade "
        "keeps you in the game long enough for your edge to play out."
    ),
    "example_account": 5000,
    "example_risk": 50,
    "example_rr": "1:3.0 RR",
    "example_target": 150,
    "tag": "SIZING",
},
```

### 5.6.2 Four Pair Spotlights

For each entry in `PAIRS`, fill in:

| Field | What to write |
|---|---|
| `pair` | Symbol (e.g. `"EURUSD"`) |
| `full_name` | Full name (e.g. `"Euro / US Dollar"`) |
| `best_session` | When you trade this pair (in your local time) |
| `avg_spread` | Typical spread on IC Markets Raw account |
| `volatility` | Average daily range |
| `my_edge` | 2–3 sentences — what specific approach you use on this pair |
| `quote` | 1–2 sentences — a memorable insight about this pair |

### 5.6.3 Four Trade Setup Breakdowns

For each entry in `SETUPS`, fill in:

| Field | What to write |
|---|---|
| `pair` | Symbol |
| `direction` | `"LONG"` or `"SHORT"` |
| `setup_type` | Name of your pattern (e.g. `"Support Zone Bounce"`) |
| `timeframe` | Multi-timeframe context (e.g. `"D1 Trend · H4 Zone · M15 Entry"`) |
| `rr` | Your standard R:R for this setup (e.g. `"1:2.5"`) |
| `steps` | List of 4 tuples — `("Step Name", "Step description here.")` |

> 💡 TIP: The `steps` field drives the card layout. 4 steps is the ideal number — fewer looks sparse, more gets cramped. Each step title should be 2–4 words; each description 1–2 sentences.

---

## 5.7 Daily Card Background Image

The daily card (`generate_status.py`) uses a photo background from `instagram/assets/bg-daily-notepad.jpg`.

Requirements:
- A close-up photo of a notebook, trading journal, or clean desk
- JPEG format, minimum 1080×1080 pixels
- Neutral or dark tones (the generator adds a navy overlay for contrast)

> 💡 TIP: Phone photos of a notebook or journal work well. The system crops and resizes automatically. If you don't have a suitable photo, use a solid dark colour fill as a placeholder — any valid JPEG works.

---

## ✅ Phase 5 Checkpoint

After completing all sections, run a test for each post type locally:

```powershell
# Test daily card
$env:POST_TYPE = "daily"
python instagram/run.py

# Test weekly performance card
$env:POST_TYPE = "weekly"
python instagram/run.py

# Test educational post
$env:POST_TYPE = "edu"
python instagram/run.py
```

For each run:
- Open the generated PNG in `instagram/posts/`
- Confirm your brand name, colours, and CTA links appear correctly
- Confirm the QR code is visible in the bottom-right corner

**Time spent so far:** ~3 hours 30 minutes total. Next: go live and verify the full pipeline end-to-end.
