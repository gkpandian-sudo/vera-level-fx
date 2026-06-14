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
    if weekday in (1, 3):       # Tuesday, Thursday
        return 'edu'
    if weekday in (2, 4):       # Wednesday, Friday
        return 'daily'
    return 'trust'


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

    data       = load_data()
    account    = data.get('account', {})
    today      = date.today()
    post_type  = os.environ.get('POST_TYPE') or decide_post_type(today)

    print(f'Generating post: {post_type} ({today})')

    if post_type == 'edu':
        from edu_content  import get_edu_content
        from generate_edu import make_risk_post, make_pairs_post, make_setup_post
        from captions     import edu as edu_caption

        idx              = read_counter()
        edu_type, content = get_edu_content(idx)
        next_idx         = (idx + 1) % 12

        if edu_type == 'risk':
            fig = make_risk_post(content)
        elif edu_type == 'pairs':
            fig = make_pairs_post(content)
        else:
            fig = make_setup_post(content)

        caption    = edu_caption(edu_type, content)
        image_path = save_image(fig, f'edu-{edu_type}')
        plt.close('all')
        print(f'  saved: {image_path}')

        image_url = commit_and_push(image_path)
        print(f'  url:   {image_url}')

        write_and_commit_counter(next_idx)
        print(f'  counter: {idx} → {next_idx}')

        print('  waiting for CDN…')
        time.sleep(20)
        publish(image_url, caption)
        print(f'Done — edu/{edu_type} post published.')
        return

    if post_type == 'daily':
        open_trades = data.get('openTrades', [])
        fig         = make_daily_card(data)
        caption     = daily_status(account, open_trades)
    elif post_type == 'weekly':
        fig     = make_weekly_card(data)
        caption = weekly(account)
    elif post_type == 'monthly':
        fig     = make_monthly_chart(data)
        # rebuild monthly_pnl for caption
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
    else:
        fig     = make_winrate_card(data)
        caption = trust(account)

    image_path = save_image(fig, post_type)
    plt.close('all')
    print(f'  saved: {image_path}')

    image_url = commit_and_push(image_path)
    print(f'  url:   {image_url}')

    # Give GitHub CDN ~20 s to propagate
    print('  waiting for CDN…')
    time.sleep(20)

    publish(image_url, caption)
    print(f'Done — {post_type} post published.')


if __name__ == '__main__':
    main()
