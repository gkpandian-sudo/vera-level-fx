"""
Entry point for the Instagram Reels automation workflow.

Env vars required (same secrets as insta-post.yml plus):
  POST_TYPE         — weekly|monthly|daily|trust|edu|transparency|recovery-plan
  POST_LANG         — en|tamil (default en)
  RECOVERY_START    — YYYY-MM-DD (repo secret, optional)
  IG_USER_ID        — Instagram Business account numeric ID
  META_ACCESS_TOKEN — long-lived Page Access Token
  GITHUB_TOKEN      — automatically provided
  GITHUB_REPOSITORY — automatically provided (owner/repo)
"""

import json, os, subprocess, sys, time
from datetime import date, datetime
from pathlib import Path

ROOT      = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / 'data' / 'vera-snapshot.json'
REEL_DIR  = ROOT / 'instagram' / 'reels'


def load_data() -> dict:
    with open(DATA_FILE) as f:
        return json.load(f)


def commit_and_push(*paths: Path) -> list:
    """Commit one or more files and return their raw GitHub URLs."""
    repo   = os.environ.get('GITHUB_REPOSITORY', '')
    branch = 'master'

    cmds = [
        ['git', 'config', 'user.email', 'github-actions[bot]@users.noreply.github.com'],
        ['git', 'config', 'user.name',  'github-actions[bot]'],
        ['git', 'add'] + [str(p) for p in paths],
        ['git', 'commit', '-m', f'auto: instagram reel {date.today()} [skip ci]'],
        ['git', 'pull',   '--rebase', 'origin', branch],
        ['git', 'push',   'origin', branch],
    ]
    for cmd in cmds:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            if 'nothing to commit' in r.stdout or 'nothing to commit' in r.stderr:
                continue
            print(r.stderr, file=sys.stderr)
            raise RuntimeError(f'git command failed: {cmd[1]}')

    base = f'https://raw.githubusercontent.com/{repo}/{branch}'
    return [f'{base}/{p.relative_to(ROOT).as_posix()}' for p in paths]


def main():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / 'instagram'))

    from reels.scenes import (
        make_daily_reel, make_weekly_reel, make_trust_reel,
        make_monthly_reel, make_transparency_reel,
        make_recovery_plan_reel, make_edu_reel, make_broker_reel,
        make_thumbnail,
    )
    from reels.audio  import get_track
    from reels.render import render
    from captions     import (weekly, monthly, trust, daily_status,
                              transparency, recovery_plan, edu as edu_caption,
                              broker as broker_caption, monthly_pnl_from_daily)
    from post         import publish_reel

    data      = load_data()
    account   = data.get('account', {})
    today     = date.today()
    post_type = os.environ.get('POST_TYPE', 'weekly')
    lang      = os.environ.get('POST_LANG', 'en')

    # Recovery day counter — shown whenever RECOVERY_START is set, regardless of current gain
    recovery_day = 0
    rs = os.environ.get('RECOVERY_START', '')
    if rs:
        try:
            _start       = datetime.strptime(rs, '%Y-%m-%d').date()
            recovery_day = max(1, (today - _start).days + 1)
        except Exception:
            pass

    print(f'Generating Reel: {post_type} ({today}) lang={lang} recovery_day={recovery_day}')

    REEL_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REEL_DIR / f'{today.isoformat()}-{post_type}.mp4'

    # ── Select clips + caption ────────────────────────────────────────────────
    if post_type == 'daily':
        clips   = make_daily_reel(data, recovery_day=recovery_day)
        caption = daily_status(account, data.get('openTrades', []),
                               lang=lang, recovery_day=recovery_day)

    elif post_type == 'weekly':
        clips   = make_weekly_reel(data, recovery_day=recovery_day)
        caption = weekly(account, lang=lang, recovery_day=recovery_day)

    elif post_type == 'monthly':
        clips       = make_monthly_reel(data)
        monthly_pnl = monthly_pnl_from_daily(data.get('dailyGain', []))
        caption     = monthly(account, monthly_pnl, lang=lang)

    elif post_type == 'transparency':
        clips   = make_transparency_reel(data)
        caption = transparency(account, lang=lang)

    elif post_type == 'recovery-plan':
        clips   = make_recovery_plan_reel(recovery_day=recovery_day)
        caption = recovery_plan(lang=lang, recovery_day=recovery_day,
                                recovery_start_str=rs,
                                balance=float(account.get('balance') or 0),
                                pf=float(account.get('profitFactor') or 0))

    elif post_type == 'edu':
        from edu_content import get_edu_content
        from run         import read_counter, write_and_commit_counter
        idx               = read_counter()
        edu_type, content = get_edu_content(idx)
        next_idx          = (idx + 1) % 12
        clips             = make_edu_reel(edu_type, content)
        caption           = edu_caption(edu_type, content, lang=lang)
        write_and_commit_counter(next_idx)

    elif post_type == 'trust':
        clips   = make_trust_reel(data)
        caption = trust(account, lang=lang)

    elif post_type == 'broker':
        clips   = make_broker_reel()
        caption = broker_caption(lang=lang)

    else:
        raise ValueError(f'Unknown POST_TYPE: {post_type!r}. '
                         f'Expected: daily|weekly|monthly|trust|edu|transparency|recovery-plan|broker')

    # ── Render ────────────────────────────────────────────────────────────────
    audio_path = get_track(post_type)
    render(clips, audio_path, str(out_path))
    print(f'  rendered: {out_path}  ({out_path.stat().st_size // 1024} KB)')

    # ── Thumbnail ─────────────────────────────────────────────────────────────
    thumb_path = REEL_DIR / f'{today.isoformat()}-{post_type}-thumb.jpg'
    thumb_img  = make_thumbnail(post_type, data, recovery_day=recovery_day)
    thumb_img.save(str(thumb_path), 'JPEG', quality=92)
    print(f'  thumbnail: {thumb_path}  ({thumb_path.stat().st_size // 1024} KB)')

    # ── Commit + publish ──────────────────────────────────────────────────────
    video_url, thumb_url = commit_and_push(out_path, thumb_path)
    print(f'  url: {video_url}')
    print(f'  thumb: {thumb_url}')

    print('  waiting 60s for GitHub CDN...')
    time.sleep(60)

    publish_reel(video_url, caption, cover_url=thumb_url)
    print(f'Done — {post_type} Reel published.')


if __name__ == '__main__':
    main()
