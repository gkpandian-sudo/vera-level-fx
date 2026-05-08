"""
Entry point for the Instagram automation workflow.

Post schedule (set via GitHub Actions cron):
  Monday    09:00 SGT → weekly performance card
  Wednesday 09:00 SGT → win rate / trust card
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

ROOT      = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / 'data' / 'vera-snapshot.json'
OUT_DIR   = ROOT / 'instagram' / 'posts'


def load_data() -> dict:
    with open(DATA_FILE) as f:
        return json.load(f)


def decide_post_type(today: date) -> str:
    if today.day <= 2:
        return 'monthly'
    weekday = today.weekday()   # 0=Mon … 6=Sun
    if weekday in (0,):
        return 'weekly'
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
    from generate  import make_weekly_card, make_monthly_chart, make_winrate_card
    from captions  import weekly, monthly, trust
    from post      import publish

    data       = load_data()
    account    = data.get('account', {})
    today      = date.today()
    post_type  = os.environ.get('POST_TYPE') or decide_post_type(today)

    print(f'Generating post: {post_type} ({today})')

    if post_type == 'weekly':
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
