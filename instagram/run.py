"""
Entry point for the Instagram automation workflow.

Post schedule (set via GitHub Actions cron):
  Monday    09:00 SGT → weekly performance card
  Tuesday   09:00 SGT → educational post (rotating 6-week library)
  Wednesday 09:00 SGT → win rate / trust card
  Thursday  09:00 SGT → educational post (rotating 6-week library)
  Friday    09:00 SGT → win rate / trust card
  1st of month        → monthly P&L chart

Env vars required:
  IG_USER_ID        — Instagram Business account numeric ID
  META_ACCESS_TOKEN — long-lived Page Access Token
  GITHUB_TOKEN      — automatically provided by GitHub Actions
  GITHUB_REPOSITORY — automatically provided (owner/repo)
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
QR_PATH      = ROOT / 'instagram' / 'assets' / 'qr-icmarkets.jpg'


def overlay_qr(image_path: Path):
    """Stamp the IC Markets referral QR code onto the bottom-left corner."""
    try:
        from PIL import Image
        post = Image.open(image_path).convert('RGBA')
        W, H = post.size

        qr      = Image.open(QR_PATH).convert('RGBA')
        qr_size = max(140, W // 7)          # ~154px on 1080 canvas
        qr      = qr.resize((qr_size, qr_size), Image.LANCZOS)

        pad     = 10
        bg_size = qr_size + pad * 2
        bg      = Image.new('RGBA', (bg_size, bg_size), (255, 255, 255, 235))
        bg.paste(qr, (pad, pad), qr)

        margin = 18
        post.paste(bg, (margin, H - bg_size - margin - 10), bg)
        post.convert('RGB').save(image_path, quality=95)
        print(f'  [qr] stamped referral QR onto {image_path.name} (bottom-left)')
    except Exception as e:
        print(f'  [qr] skipped: {e}', file=sys.stderr)


def pop_buffer(post_type: str, edu_type: str = '') -> Path | None:
    """Return the oldest buffered image for this post type, or None.

    For edu posts, edu_type ('risk'|'pairs'|'setup') selects the sub-folder.
    The file is moved to OUT_DIR immediately so it won't be used twice.
    """
    if post_type == 'edu' and edu_type:
        folder = BUFFER_DIR / 'edu' / edu_type
    else:
        folder = BUFFER_DIR / post_type

    pngs = sorted(p for p in folder.glob('*.png') if p.name != '.gitkeep')
    if not pngs:
        return None

    src = pngs[0]   # oldest alphabetically / by name
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
        ['git', 'pull',   '--rebase', 'origin', 'master'],
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
    if weekday == 1:            # Tuesday only — one edu per week
        return 'edu'
    return 'daily'


def save_image(fig, post_type: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    filename = OUT_DIR / f'{date.today().isoformat()}-{post_type}.png'
    fig.savefig(filename, dpi=100, bbox_inches='tight', facecolor='#060F24')
    return filename


def commit_and_push(image_path: Path) -> str:
    """Commit the image to the repo and return its raw GitHub URL."""
    repo = os.environ.get('GITHUB_REPOSITORY', '')   # owner/repo
    branch = 'master'
    rel    = image_path.relative_to(ROOT).as_posix()

    cmds = [
        ['git', 'config', 'user.email', 'github-actions[bot]@users.noreply.github.com'],
        ['git', 'config', 'user.name',  'github-actions[bot]'],
        ['git', 'add',    str(image_path)],
        ['git', 'commit', '-m', f'auto: instagram post {date.today()} [skip ci]'],
        ['git', 'pull',   '--rebase', 'origin', branch],
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

    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / 'instagram'))
    from generate        import make_weekly_card, make_monthly_chart, make_winrate_card, make_transparency_card, make_recovery_plan_card
    from generate_status import make_daily_card
    from captions        import weekly, monthly, trust, daily_status, transparency, recovery_plan, monthly_pnl_from_daily
    from post            import publish

    data       = load_data()
    account    = data.get('account', {})
    today      = date.today()
    post_type  = os.environ.get('POST_TYPE') or decide_post_type(today)
    lang       = os.environ.get('POST_LANG', 'en')

    # Recovery day counter — shown whenever RECOVERY_START is set, regardless of current gain
    recovery_day = 0
    recovery_start_str = os.environ.get('RECOVERY_START', '')
    if recovery_start_str:
        try:
            from datetime import datetime as _dt
            _start = _dt.strptime(recovery_start_str, '%Y-%m-%d').date()
            recovery_day = max(1, (today - _start).days + 1)
        except Exception:
            pass
    recovery_total = int(os.environ.get('RECOVERY_TOTAL', '180'))

    print(f'Generating post: {post_type} ({today}) lang={lang} recovery_day={recovery_day}')

    if post_type == 'edu':
        from edu_content  import get_edu_content
        from generate_edu import make_risk_post, make_pairs_post, make_setup_post
        from captions     import edu as edu_caption

        idx               = read_counter()
        edu_type, content = get_edu_content(idx)
        next_idx          = (idx + 1) % 12

        caption    = edu_caption(edu_type, content, lang=lang)
        image_path = pop_buffer('edu', edu_type)   # use buffered image if available

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

    # ── Non-edu post types — check buffer first ───────────────────
    image_path = pop_buffer(post_type)

    if post_type == 'daily':
        open_trades = data.get('openTrades', [])
        caption     = daily_status(account, open_trades, lang=lang, recovery_day=recovery_day)
        if image_path is None:
            fig = make_daily_card(data)
    elif post_type == 'weekly':
        caption = weekly(account, lang=lang, recovery_day=recovery_day)
        if image_path is None:
            fig = make_weekly_card(data)
    elif post_type == 'monthly':
        # rebuild monthly_pnl for caption (Myfxbook MM/DD/YYYY dates)
        monthly_pnl = monthly_pnl_from_daily(data.get('dailyGain', []))
        caption = monthly(account, monthly_pnl, lang=lang)
        if image_path is None:
            fig = make_monthly_chart(data)
    elif post_type == 'transparency':
        caption = transparency(account, lang=lang)
        if image_path is None:
            fig = make_transparency_card(data)
    elif post_type == 'recovery-plan':
        caption = recovery_plan(lang=lang, recovery_day=recovery_day,
                                recovery_start_str=recovery_start_str,
                                balance=float(account.get('balance') or 0),
                                pf=float(account.get('profitFactor') or 0))
        if image_path is None:
            fig = make_recovery_plan_card(data)
    else:
        caption = trust(account, lang=lang)
        if image_path is None:
            fig = make_winrate_card(data)

    if image_path is None:
        image_path = save_image(fig, post_type)
        plt.close('all')
    print(f'  saved: {image_path}')
    overlay_qr(image_path)

    image_url = commit_and_push(image_path)
    print(f'  url:   {image_url}')

    # Give GitHub CDN ~20 s to propagate
    print('  waiting for CDN…')
    time.sleep(20)

    publish(image_url, caption)
    print(f'Done — {post_type} post published.')


if __name__ == '__main__':
    main()
