---
phase: 3
title: "Instagram Pipeline Setup"
estimated_time: "60 minutes"
prerequisites: ["Phase 0 complete", "Phase 1 complete", "Phase 2 complete"]
outputs:
  - my-fx-instagram/ repo cloned locally with all Python files
  - instagram/requirements.txt installed
  - POST_TYPE=weekly python instagram/run.py generates a PNG without errors
  - Placeholder data files in place
  - Buffer folder structure created
---

# Phase 3 — Instagram Pipeline Setup

This phase builds the Instagram image generation and publishing pipeline inside your `my-fx-instagram` GitHub repo. Every file is shown in full. Lines marked with `# CUSTOMISE:` are the ones you must change.

---

## 3.1 Clone Your GitHub Repo Locally

```powershell
git clone https://github.com/yourusername/my-fx-instagram.git
cd my-fx-instagram
```

Replace `yourusername` with your GitHub username and `my-fx-instagram` with your repo name if you chose a different one.

---

## 3.2 Create Folder Structure

```powershell
mkdir instagram
mkdir instagram\assets
mkdir instagram\posts
mkdir instagram\buffer
mkdir instagram\buffer\daily
mkdir instagram\buffer\weekly
mkdir instagram\buffer\monthly
mkdir instagram\buffer\trust
mkdir instagram\buffer\edu
mkdir instagram\buffer\edu\risk
mkdir instagram\buffer\edu\pairs
mkdir instagram\buffer\edu\setup
mkdir data
```

Create `.gitkeep` files so Git tracks the empty folders:

```powershell
foreach ($dir in @(
  "instagram\buffer\daily",
  "instagram\buffer\weekly",
  "instagram\buffer\monthly",
  "instagram\buffer\trust",
  "instagram\buffer\edu\risk",
  "instagram\buffer\edu\pairs",
  "instagram\buffer\edu\setup",
  "instagram\posts"
)) {
  New-Item "$dir\.gitkeep" -ItemType File -Force
}
```

---

## 3.3 Create requirements.txt

**`instagram/requirements.txt`**
```
matplotlib==3.8.4
numpy==1.26.4
requests==2.31.0
Pillow==10.3.0
```

Install:

```powershell
pip install -r instagram\requirements.txt
```

---

## 3.4 Create instagram/post.py

This file handles the two-step Meta Graph API publishing flow. **No customisation needed.**

**`instagram/post.py`**
```python
import os
import time
import requests

GRAPH = 'https://graph.facebook.com/v19.0'
IG_ID = os.environ['IG_USER_ID']
TOKEN = os.environ['META_ACCESS_TOKEN']


def _check(r: requests.Response):
    if not r.ok:
        raise RuntimeError(f"Meta API error {r.status_code}: {r.text}")
    return r.json()


def publish(image_url: str, caption: str) -> str:
    # Step 1 — create media container
    data = _check(requests.post(
        f'{GRAPH}/{IG_ID}/media',
        params={
            'image_url':    image_url,
            'caption':      caption,
            'access_token': TOKEN,
        }
    ))
    container_id = data['id']
    print(f'  container created: {container_id}')

    # Wait for Instagram to process the image (up to 60 seconds)
    for attempt in range(12):
        time.sleep(5)
        status = _check(requests.get(
            f'{GRAPH}/{container_id}',
            params={'fields': 'status_code', 'access_token': TOKEN}
        ))
        if status.get('status_code') == 'FINISHED':
            break
        print(f'  processing… ({status.get("status_code")})')
    else:
        raise TimeoutError('Instagram container did not finish processing')

    # Step 2 — publish
    result = _check(requests.post(
        f'{GRAPH}/{IG_ID}/media_publish',
        params={
            'creation_id':  container_id,
            'access_token': TOKEN,
        }
    ))
    post_id = result['id']
    print(f'  published: {post_id}')
    return post_id
```

---

## 3.5 Create instagram/captions.py

Caption text for all post types. Brand-specific links are loaded from **GitHub Secrets** (environment variables) — never hardcoded in the file. You will add the secret values in Phase 4.

**`instagram/captions.py`**
```python
import os
from datetime import datetime

# CUSTOMISE: replace with hashtags relevant to your brand and location
TAGS = (
    "#forex #forextrader #forextrading #algotrading #algorithmic "
    "#icmarkets #myfxbook #xauusd #gold #forexsignals "
    "#tradingstrategy #YOURCOUNTRY #investing#YOURCOUNTRY "
    "#financialfreedom #wealthbuilding #YourBrandFX "
    "#forexlifestyle #passiveincome #tradingresults"
)

# Brand links are injected at runtime from GitHub Secrets (see Phase 4 section 4.4)
_TELEGRAM = os.environ.get('BRAND_TELEGRAM', '')
_WEBSITE  = os.environ.get('BRAND_WEBSITE', '')
_IB_URL   = os.environ.get('BRAND_IB_URL', '')

_CTA = (
    f"\n\n📲 Live signals → {_TELEGRAM}"
    f"\n🌐 Live account → {_WEBSITE}"
    f"\n🏦 Open IC Markets account →"
    f"\n{_IB_URL}"
)


def weekly(account: dict) -> str:
    bal   = account.get('balance', 0)
    gain  = account.get('gain', 0)
    mo    = account.get('monthly', 0)
    wr    = account.get('winRate', 0)
    pf    = account.get('profitFactor', 0)
    pips  = int(account.get('pips', 0))
    date  = datetime.now().strftime('%d %b %Y')

    return f"""📊 Weekly Performance Update — {date}

💰 Balance: ${bal:,.2f}
📈 Total Gain: +{gain:.2f}% since inception
📅 Monthly Avg: +{mo:.2f}%
🎯 Win Rate: {wr:.0f}%
⚡ Profit Factor: {pf:.2f}
💹 Total Pips: +{pips:,}

Fully automated algorithmic trading on IC Markets.
Every trade live-verified on Myfxbook — zero manipulation.
{_CTA}

{TAGS}"""


def monthly(account: dict, monthly_pnl: dict) -> str:
    last_months = list(monthly_pnl.items())[-6:]
    lines = '  '.join(
        f"{'🟢' if v >= 0 else '🔴'} {k}: {v:+.1f}%"
        for k, v in last_months
    )
    gain = account.get('gain', 0)

    return f"""📅 Monthly P&L Breakdown — {datetime.now().strftime('%B %Y')}

{lines}

📈 Total Gain to date: +{gain:.2f}%

Systematic execution. No emotions. No manual overrides.
IC Markets raw spreads — ASIC regulated.
{_CTA}

{TAGS}"""


def edu(edu_type: str, content: dict) -> str:
    base_tags = (
        "#forex #forextrader #forexsingapore #icmarkets #xauusd "
        "#YourBrandFX #tradingstrategy #YOURCOUNTRY #forexeducation "
        "#fxtrading #priceaction"
    )
    cta = _CTA

    if edu_type == 'risk':
        return (
            f"⚠️ Risk Management Rule #{content['rule_num']} — {content['title']}\n\n"
            f"{content['body']}\n\n"
            f"💰 Example: ${content['example_account']:,} account → "
            f"${content['example_risk']:,} max risk per trade\n"
            f"🎯 At {content['example_rr']} — that's the professional way."
            f"{cta}\n\n{base_tags}"
        )

    if edu_type == 'pairs':
        return (
            f"🌍 Pair Spotlight — {content['pair']} ({content['full_name']})\n\n"
            f"Best session: {content['best_session']}\n"
            f"Avg spread: {content['avg_spread']}\n"
            f"Volatility: {content['volatility']}\n"
            f"My edge: {content['my_edge']}\n\n"
            f'"{content["quote"]}"\n\n'
            f"— {os.environ.get('BRAND_AUTHOR', 'YourBrand FX')}"
            f"{cta}\n\n{base_tags}"
        )

    # setup
    steps_text = '\n'.join(
        f"{i+1}. {title} — {desc}"
        for i, (title, desc) in enumerate(content['steps'])
    )
    return (
        f"📈 Setup Breakdown — {content['pair']} {content['direction']} "
        f"({content['setup_type']})\n\n"
        f"Timeframe: {content['timeframe']}\n"
        f"Risk:Reward: {content['rr']}\n\n"
        f"{steps_text}\n\n"
        f"This is exactly how I structure every trade — no guessing, no emotion."
        f"{cta}\n\n{base_tags}"
    )


def daily_status(account: dict, open_trades: list) -> str:
    balance   = account.get('balance', 0)
    equity    = account.get('equity', balance)
    daily_pct = account.get('daily', 0)
    win_rate  = account.get('winRate', 0)
    pf        = account.get('profitFactor', 0)
    pips      = int(account.get('pips', 0))
    trades    = int(account.get('trades', 0))
    date      = datetime.now().strftime('%d %b %Y')

    direction_emoji = '📈' if daily_pct >= 0 else '📉'
    daily_sign      = '+' if daily_pct >= 0 else ''

    open_lines = []
    for t in open_trades[:5]:
        pair   = t.get('symbol', '')
        action = t.get('action', '').upper()
        profit = t.get('profit', 0)
        icon   = '🟢' if profit >= 0 else '🔴'
        open_lines.append(f"  {icon} {pair} {action}  ${profit:+.2f}")
    positions_block = '\n'.join(open_lines) if open_lines else '  No open positions'

    return f"""{direction_emoji} Live Trade Update — {date}

💰 Balance: ${balance:,.2f}
⚖️ Equity: ${equity:,.2f}
📊 Daily: {daily_sign}{daily_pct:.2f}%

🔓 Open Positions:
{positions_block}

📈 Running stats: {win_rate:.0f}% win rate · PF {pf:.2f} · +{pips:,} pips · {trades:,} trades

Fully automated system on IC Markets.
Every position tracked live on Myfxbook — zero manipulation.
{_CTA}

{TAGS}"""


def trust(account: dict) -> str:
    wr    = account.get('winRate', 0)
    pf    = account.get('profitFactor', 0)
    gain  = account.get('gain', 0)
    trades = int(account.get('trades', 0))
    pips  = int(account.get('pips', 0))

    brand = os.environ.get('BRAND_AUTHOR', 'YourBrand FX')
    return f"""✅ Live Track Record — {brand}

🎯 Win Rate: {wr:.0f}% across {trades:,} trades
⚡ Profit Factor: {pf:.2f}
📈 Total Gain: +{gain:.2f}%
💹 Pips: +{pips:,}

This is a LIVE account on IC Markets.
Not a demo. Not backtested. Publicly audited on Myfxbook.

Every entry. Every exit. Every result — visible to anyone.
{_CTA}

{TAGS}"""
```

---

## 3.6 Create instagram/edu_content.py

The rotating 12-slot educational content library. **Replace all content with your own trading methodology.**

See Phase 5 section 5.6 for a detailed guide on filling in this file. For now, create it with placeholder content so the pipeline can run:

**`instagram/edu_content.py`**
```python
# CUSTOMISE: Replace all content below with your own trading methodology
# This file is your 6-week rotating educational content library
# 12 slots: 5 RISK rules + 4 PAIRS + 4 SETUPS + (see ROTATION_SEQUENCE)

RISK_RULES = [
    {
        "rule_num": "01",
        "title": "Your Risk Rule Title Here",
        "body": "Explain your risk management rule in 2-3 sentences here.",
        "example_account": 3000,
        "example_risk": 90,
        "example_rr": "1:2.5 RR",
        "example_target": 225,
        "tag": "SIZING",
    },
    {
        "rule_num": "02",
        "title": "Your Second Risk Rule",
        "body": "Explain your second risk rule here.",
        "example_account": 3000,
        "example_risk": 30,
        "example_rr": "Per level",
        "example_target": 0,
        "tag": "RULE 2",
    },
    {
        "rule_num": "03",
        "title": "Your Third Risk Rule",
        "body": "Explain your third risk rule here.",
        "example_account": 3000,
        "example_risk": 60,
        "example_rr": "Context",
        "example_target": 0,
        "tag": "RULE 3",
    },
    {
        "rule_num": "04",
        "title": "Your Fourth Risk Rule",
        "body": "Explain your fourth risk rule here.",
        "example_account": 3000,
        "example_risk": 75,
        "example_rr": "Cross-pair",
        "example_target": 0,
        "tag": "RULE 4",
    },
    {
        "rule_num": "05",
        "title": "Your Fifth Risk Rule",
        "body": "Explain your fifth risk rule here.",
        "example_account": 3000,
        "example_risk": 100,
        "example_rr": "PF target",
        "example_target": 0,
        "tag": "RULE 5",
    },
]

PAIRS = [
    {
        "pair": "EURUSD",
        "full_name": "Euro / US Dollar",
        "best_session": "London+NY 1300–1700 SGT",
        "avg_spread": "0.0–0.2 pips (IC Raw)",
        "volatility": "Medium — 60–90 pips/day",
        "my_edge": "Describe your specific edge on this pair.",
        "quote": "Your quote about this pair.",
    },
    {
        "pair": "GBPJPY",
        "full_name": "British Pound / Japanese Yen",
        "best_session": "London Open 1500–1800",
        "avg_spread": "1.0–1.5 pips (IC Raw)",
        "volatility": "Very High — 150–200 pip",
        "my_edge": "Describe your specific edge on this pair.",
        "quote": "Your quote about this pair.",
    },
    {
        "pair": "XAUUSD",
        "full_name": "Gold / US Dollar",
        "best_session": "NY Open 2130–0000 SGT",
        "avg_spread": "0.2–0.5 pips (IC Raw)",
        "volatility": "High — 15–30 USD/session",
        "my_edge": "Describe your specific edge on this pair.",
        "quote": "Your quote about this pair.",
    },
    {
        "pair": "USDJPY",
        "full_name": "US Dollar / Japanese Yen",
        "best_session": "Asian 0100–0800 SGT",
        "avg_spread": "0.0–0.3 pips (IC Raw)",
        "volatility": "Low–Med 50–80 pips/day",
        "my_edge": "Describe your specific edge on this pair.",
        "quote": "Your quote about this pair.",
    },
]

SETUPS = [
    {
        "pair": "EURUSD",
        "direction": "LONG",
        "setup_type": "Your Setup Name Here",
        "timeframe": "H4 Bias · H1 Structure · M15 Entry",
        "rr": "1:2.5",
        "steps": [
            ("Step 1 Name", "Describe step 1."),
            ("Step 2 Name", "Describe step 2."),
            ("Step 3 Name", "Describe step 3."),
            ("Step 4 Name", "Entry conditions and risk parameters."),
        ],
    },
    {
        "pair": "XAUUSD",
        "direction": "SHORT",
        "setup_type": "Your Setup Name Here",
        "timeframe": "H4 Supply · H1 Confirmation · M15 Entry",
        "rr": "1:2.0",
        "steps": [
            ("Step 1 Name", "Describe step 1."),
            ("Step 2 Name", "Describe step 2."),
            ("Step 3 Name", "Describe step 3."),
            ("Step 4 Name", "Entry conditions and risk parameters."),
        ],
    },
    {
        "pair": "GBPJPY",
        "direction": "LONG",
        "setup_type": "Your Setup Name Here",
        "timeframe": "H1 Range · M15 Break · M5 Entry",
        "rr": "1:2.5",
        "steps": [
            ("Step 1 Name", "Describe step 1."),
            ("Step 2 Name", "Describe step 2."),
            ("Step 3 Name", "Describe step 3."),
            ("Step 4 Name", "Entry conditions and risk parameters."),
        ],
    },
    {
        "pair": "USDJPY",
        "direction": "SHORT",
        "setup_type": "Your Setup Name Here",
        "timeframe": "H1 Range · M15 Signal · M5 Trigger",
        "rr": "1:2.0",
        "steps": [
            ("Step 1 Name", "Describe step 1."),
            ("Step 2 Name", "Describe step 2."),
            ("Step 3 Name", "Describe step 3."),
            ("Step 4 Name", "Entry conditions and risk parameters."),
        ],
    },
]

# 12-slot, 6-week rotation: every Tue + Thu gets one slot
ROTATION_SEQUENCE = [
    ("risk",  0),   # Week 1 Tue
    ("pairs", 0),   # Week 1 Thu
    ("setup", 0),   # Week 2 Tue
    ("risk",  1),   # Week 2 Thu
    ("pairs", 2),   # Week 3 Tue
    ("setup", 1),   # Week 3 Thu
    ("risk",  2),   # Week 4 Tue
    ("pairs", 1),   # Week 4 Thu
    ("setup", 2),   # Week 5 Tue
    ("risk",  3),   # Week 5 Thu
    ("pairs", 3),   # Week 6 Tue
    ("setup", 3),   # Week 6 Thu
]


def get_edu_content(index: int) -> tuple:
    """Return (post_type, content_dict) for the given rotation index."""
    slot = ROTATION_SEQUENCE[index % len(ROTATION_SEQUENCE)]
    post_type, content_index = slot
    if post_type == "risk":
        return post_type, RISK_RULES[content_index]
    if post_type == "pairs":
        return post_type, PAIRS[content_index]
    return post_type, SETUPS[content_index]
```

---

## 3.7 Create instagram/run.py

The pipeline entry point. **No customisation needed except the QR code asset filename** if you used a different name.

**`instagram/run.py`**
```python
"""
Entry point for the Instagram automation workflow.
"""
import json, os, sys, subprocess, time
from datetime import datetime, date
from pathlib import Path

import requests

ROOT         = Path(__file__).resolve().parent.parent
DATA_FILE    = ROOT / 'data' / 'vera-snapshot.json'
OUT_DIR      = ROOT / 'instagram' / 'posts'
COUNTER_FILE = ROOT / 'data' / 'edu-counter.json'
BUFFER_DIR   = ROOT / 'instagram' / 'buffer'
# CUSTOMISE: update filename if you saved your QR code with a different name
QR_PATH      = ROOT / 'instagram' / 'assets' / 'qr-icmarkets.jpg'


def overlay_qr(image_path: Path):
    """Stamp the IC Markets referral QR code onto the bottom-right corner."""
    try:
        from PIL import Image
        post = Image.open(image_path).convert('RGBA')
        W, H = post.size

        qr      = Image.open(QR_PATH).convert('RGBA')
        qr_size = max(140, W // 7)
        qr      = qr.resize((qr_size, qr_size), Image.LANCZOS)

        pad     = 10
        bg_size = qr_size + pad * 2
        bg      = Image.new('RGBA', (bg_size, bg_size), (255, 255, 255, 235))
        bg.paste(qr, (pad, pad), qr)

        margin = 18
        post.paste(bg, (W - bg_size - margin, H - bg_size - margin - 10), bg)
        post.convert('RGB').save(image_path, quality=95)
        print(f'  [qr] stamped referral QR onto {image_path.name}')
    except Exception as e:
        print(f'  [qr] skipped: {e}', file=sys.stderr)


def pop_buffer(post_type: str, edu_type: str = '') -> Path | None:
    """Return the oldest buffered image for this post type, or None."""
    if post_type == 'edu' and edu_type:
        folder = BUFFER_DIR / 'edu' / edu_type
    else:
        folder = BUFFER_DIR / post_type

    pngs = sorted(p for p in folder.glob('*.png') if p.name != '.gitkeep')
    if not pngs:
        return None

    src = pngs[0]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dst = OUT_DIR / f'{date.today().isoformat()}-{post_type}-buffered.png'
    src.rename(dst)
    print(f'  [buffer] using pre-made image: {src.name} → {dst.name}')
    return dst


def load_data() -> dict:
    with open(DATA_FILE) as f:
        return json.load(f)


def read_counter() -> int:
    with open(COUNTER_FILE) as f:
        return json.load(f)['index']


def write_and_commit_counter(index: int):
    with open(COUNTER_FILE, 'w') as f:
        json.dump({'index': index}, f)
    cmds = [
        ['git', 'config', 'user.email', 'github-actions[bot]@users.noreply.github.com'],
        ['git', 'config', 'user.name',  'github-actions[bot]'],
        ['git', 'add', str(COUNTER_FILE)],
        ['git', 'commit', '-m', f'chore: advance edu counter to {index} [skip ci]'],
        ['git', 'push',   'origin', 'master'],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if result.returncode != 0 and 'nothing to commit' not in result.stdout:
            print(result.stderr, file=sys.stderr)


def decide_post_type(today: date) -> str:
    if today.day <= 2:
        return 'monthly'
    weekday = today.weekday()   # 0=Mon … 6=Sun
    if weekday == 0:
        return 'weekly'
    if weekday in (1, 3):
        return 'edu'
    if weekday in (2, 4):
        return 'daily'
    return 'trust'


def save_image(fig, post_type: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    filename = OUT_DIR / f'{date.today().isoformat()}-{post_type}.png'
    fig.savefig(filename, dpi=100, bbox_inches='tight', facecolor='#060F24')
    return filename


def commit_and_push(image_path: Path) -> str:
    """Commit the image to the repo and return its raw GitHub URL."""
    repo   = os.environ.get('GITHUB_REPOSITORY', '')
    branch = 'master'
    rel    = image_path.relative_to(ROOT).as_posix()

    cmds = [
        ['git', 'config', 'user.email', 'github-actions[bot]@users.noreply.github.com'],
        ['git', 'config', 'user.name',  'github-actions[bot]'],
        ['git', 'add',    str(image_path)],
        ['git', 'commit', '-m', f'auto: instagram post {date.today()} [skip ci]'],
        ['git', 'push',   'origin', branch],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if result.returncode != 0 and 'nothing to commit' not in result.stdout:
            print(result.stderr, file=sys.stderr)

    raw_url = f'https://raw.githubusercontent.com/{repo}/{branch}/{rel}'
    return raw_url


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    sys.path.insert(0, str(ROOT / 'instagram'))
    from generate        import make_weekly_card, make_monthly_chart, make_winrate_card
    from generate_status import make_daily_card
    from captions        import weekly, monthly, trust, daily_status
    from post            import publish

    data      = load_data()
    account   = data.get('account', {})
    today     = date.today()
    post_type = os.environ.get('POST_TYPE') or decide_post_type(today)

    print(f'Generating post: {post_type} ({today})')

    if post_type == 'edu':
        from edu_content  import get_edu_content
        from generate_edu import make_risk_post, make_pairs_post, make_setup_post
        from captions     import edu as edu_caption

        idx               = read_counter()
        edu_type, content = get_edu_content(idx)
        next_idx          = (idx + 1) % 12

        caption    = edu_caption(edu_type, content)
        image_path = pop_buffer('edu', edu_type)

        if image_path is None:
            if edu_type == 'risk':
                fig = make_risk_post(content)
            elif edu_type == 'pairs':
                fig = make_pairs_post(content)
            else:
                fig = make_setup_post(content)
            image_path = save_image(fig, f'edu-{edu_type}')
            plt.close('all')

        print(f'  saved: {image_path}')
        overlay_qr(image_path)

        image_url = commit_and_push(image_path)
        print(f'  url:   {image_url}')

        write_and_commit_counter(next_idx)
        print(f'  counter: {idx} → {next_idx}')

        print('  waiting for CDN…')
        time.sleep(20)
        publish(image_url, caption)
        print(f'Done — edu/{edu_type} post published.')
        return

    image_path = pop_buffer(post_type)

    if post_type == 'daily':
        open_trades = data.get('openTrades', [])
        caption     = daily_status(account, open_trades)
        if image_path is None:
            fig = make_daily_card(data)
    elif post_type == 'weekly':
        caption = weekly(account)
        if image_path is None:
            fig = make_weekly_card(data)
    elif post_type == 'monthly':
        monthly_pnl = {}
        for item in data.get('dailyGain', []):
            ds  = item[0] if isinstance(item, list) else item.get('date', '')
            val = item[1] if isinstance(item, list) else item.get('value', 0)
            try:
                from datetime import datetime as dt
                key = dt.fromisoformat(str(ds)[:10]).strftime('%b %y')
                monthly_pnl[key] = monthly_pnl.get(key, 0) + float(val)
            except Exception:
                pass
        caption = monthly(account, monthly_pnl)
        if image_path is None:
            fig = make_monthly_chart(data)
    else:
        caption = trust(account)
        if image_path is None:
            fig = make_winrate_card(data)

    if image_path is None:
        image_path = save_image(fig, post_type)
        plt.close('all')
    print(f'  saved: {image_path}')
    overlay_qr(image_path)

    image_url = commit_and_push(image_path)
    print(f'  url:   {image_url}')

    print('  waiting for CDN…')
    time.sleep(20)

    publish(image_url, caption)
    print(f'Done — {post_type} post published.')


if __name__ == '__main__':
    main()
```

---

## 3.8 Image Generator Files

The system uses three image generator files that produce the 1080×1080 PNG cards. These files are complex and contain the visual layout logic. The key values to customise are the **brand colours** and **brand name strings** — covered in detail in Phase 5.

For now, copy these files directly from the reference repo or create them as shown in Phase 5 section 5.1. The generator files are:

| File | Post types |
|---|---|
| `instagram/generate_status.py` | `daily` — live position card with notepad background |
| `instagram/generate.py` | `weekly`, `monthly`, `trust` — performance cards |
| `instagram/generate_edu.py` | `edu` (risk, pairs, setup) — educational posts |

The colour palette used across all three files:

```python
NAVY   = '#010E1F'   # deep navy — main background
NAVY_S = '#051830'   # slightly lighter navy
NAVY_L = '#0A2545'   # lighter navy for panels
GOLD   = '#F0C040'   # brand gold — headings and accents
WHITE  = '#FFFFFF'   # primary text
CREAM  = '#F0EEE8'   # secondary text on dark backgrounds
MUTED  = '#B8CFEA'   # muted blue — tertiary text
GREEN  = '#00E096'   # profit / positive values
RED    = '#FF6B6B'   # loss / negative values
```

> 💡 TIP: You can change any of these colours to match your brand. See Phase 5 section 5.1 for the full colour reference table across all three files.

---

## 3.9 Create Background Image

The daily card uses a photo background (`instagram/assets/bg-daily-notepad.jpg`). This should be a clean, close-up photo of a notebook, trading journal, or flat-lay workspace.

Requirements:
- Minimum 1080×1080 pixels
- Save as `instagram/assets/bg-daily-notepad.jpg`
- The generator crops it to a square automatically
- Dark or neutral tones work best — the navy overlay makes light backgrounds look muddy

> 💡 TIP: You can use any JPEG image here. If you don't have a suitable photo, a solid dark navy image (`#010E1F` filled) also works as a fallback — PIL will create one.

---

## 3.10 Create Placeholder Data Files

**`data/vera-snapshot.json`** — placeholder with representative values so the pipeline can run before live data:

```json
{
  "account": {
    "balance": 3000.00,
    "equity": 3000.00,
    "daily": 0.0,
    "monthly": 1.5,
    "gain": 8.5,
    "drawdown": 2.1,
    "profitFactor": 1.62,
    "winRate": 72,
    "trades": 150,
    "pips": 1200
  },
  "openTrades": [],
  "history": [],
  "dailyGain": [],
  "fetchedAt": "2026-01-01T00:00:00.000Z"
}
```

**`data/edu-counter.json`**
```json
{"index": 0}
```

---

## ✅ Phase 3 Checkpoint

Generate a test post locally:

```powershell
$env:POST_TYPE = "weekly"
python instagram/run.py
```

Expected output:

```
Generating post: weekly (2026-06-14)
  saved: C:\...\instagram\posts\2026-06-14-weekly.png
  [qr] skipped: [Errno 2] No such file or directory (expected — QR not added yet)
Done — weekly post published.
```

> ✅ CHECKPOINT: An image file is created at `instagram/posts/YYYY-MM-DD-weekly.png`. Open it — you should see a navy performance card with your placeholder stats. The QR skip warning is expected until you add your QR code image in Phase 5.

> ⚠️ WARNING: If you see `ModuleNotFoundError: No module named 'generate'`, confirm you are running from the repo root (`my-fx-instagram/`) directory, not from inside `instagram/`.

**Time spent so far:** ~2 hours 35 minutes total. Next: wire up GitHub Actions and get your Meta API keys.
