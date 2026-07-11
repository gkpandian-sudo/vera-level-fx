# instagram/higgsfield/pipeline.py
"""Orchestrator: snapshot → script → generate → virality gate → composite → commit → post."""
import json, os, subprocess, sys, time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'instagram'))

from higgsfield.avatar    import generate_reel
from higgsfield.cinematic import generate_broker_reel
from higgsfield.client    import predict_virality, dub_to_tamil as _dub
from higgsfield.scripts   import build_script, ReelScript
from higgsfield.hashtags  import get_hashtags, get_hashtags_tamil
from higgsfield.composer  import composite_data_card


def publish_reel(video_url: str, caption: str, cover_url: str = '') -> str:
    """Thin wrapper around post.publish_reel — kept at module level so tests can patch it."""
    from post import publish_reel as _publish_reel
    return _publish_reel(video_url, caption, cover_url=cover_url)

DATA_FILE   = ROOT / 'data' / 'vera-snapshot.json'
EDU_COUNTER = ROOT / 'data' / 'edu-counter.json'
REEL_DIR    = ROOT / 'instagram' / 'reels'

VIRALITY_THRESHOLD = float(os.environ.get('VIRALITY_THRESHOLD', '65'))
MAX_RETRIES        = 2
try:
    from edu_content import ROTATION_SEQUENCE as _ROTATION_SEQUENCE
    ROTATION_LEN = len(_ROTATION_SEQUENCE)
except ImportError:
    ROTATION_LEN = 14  # fallback for test environments without edu_content on path


def load_snapshot() -> dict:
    with open(DATA_FILE) as f:
        return json.load(f)


def read_counter() -> int:
    try:
        with open(EDU_COUNTER) as f:
            return int(json.load(f).get('index', 0))
    except FileNotFoundError:
        return 0


def write_counter(idx: int) -> None:
    with open(EDU_COUNTER, 'w') as f:
        json.dump({'index': idx}, f)


def commit_and_push(*paths: Path) -> list[str]:
    """Commit files and return their raw GitHub URLs."""
    repo   = os.environ.get('GITHUB_REPOSITORY', '')
    branch = 'master'
    cmds = [
        ['git', 'config', 'user.email', 'github-actions[bot]@users.noreply.github.com'],
        ['git', 'config', 'user.name',  'github-actions[bot]'],
        ['git', 'add'] + [str(p) for p in paths],
        ['git', 'commit', '-m', f'auto: higgsfield reel {date.today()} [skip ci]'],
        ['git', 'pull',   '--rebase', 'origin', branch],
        ['git', 'push',   'origin', branch],
    ]
    for cmd in cmds:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0 and 'nothing to commit' not in r.stdout + r.stderr:
            print(r.stderr, file=sys.stderr)
            raise RuntimeError(f'git command failed: {cmd[1]}')
    base = f'https://raw.githubusercontent.com/{repo}/{branch}'
    return [f'{base}/{p.relative_to(ROOT).as_posix()}' for p in paths]


def dub_to_tamil_video(en_video_url: str) -> str:
    """Dub EN video URL to Tamil. Returns Tamil video URL."""
    voice_id = os.environ.get('HIGGSFIELD_VOICE_TAMIL_ID', '')
    return _dub(en_video_url, voice_id=voice_id)


def _make_data_card(reel_type: str, snapshot: dict, out_path: Path) -> None:
    """Render a static data card PNG using existing generate_*.py functions."""
    from generate import render_weekly_card, render_trust_card
    if reel_type in ('weekly', 'broker'):
        img = render_weekly_card(snapshot)
    else:  # trust, edu
        img = render_trust_card(snapshot)
    img.save(str(out_path), 'JPEG', quality=92)


def _tweak_hook(script: ReelScript, attempt: int) -> ReelScript:
    """Return a copy of script with a punchier hook for virality retry."""
    new_hook = (
        script.hook.replace('.', ' — watch this.', 1)
        if attempt == 0
        else f"I'll say this once: {script.hook}"
    )
    return ReelScript(
        hook=new_hook,
        content=script.content,
        proof=script.proof,
        cta=script.cta,
        language=script.language,
        reel_type=script.reel_type,
    )


def get_edu_content(idx: int):
    from edu_content import get_edu_content as _gec
    return _gec(idx)


def _generate_with_virality_gate(
    script: ReelScript,
    out_path: Path,
    reel_type: str,
    voice_id: str = '',
) -> tuple[str, Path]:
    """Generate reel, virality-gate the hook clip URL, retry up to MAX_RETRIES times."""
    current = script
    for attempt in range(MAX_RETRIES + 1):
        if reel_type == 'broker':
            hook_url, assembled = generate_broker_reel(current, out_path, voice_id)
        else:
            hook_url, assembled = generate_reel(current, out_path, voice_id)

        score = predict_virality(hook_url)
        print(f'  [pipeline] virality={score:.1f} threshold={VIRALITY_THRESHOLD} attempt={attempt + 1}')

        if score >= VIRALITY_THRESHOLD or attempt == MAX_RETRIES:
            if score < VIRALITY_THRESHOLD:
                print(f'  [pipeline] WARNING: posting after {MAX_RETRIES} retries')
            return hook_url, assembled

        current = _tweak_hook(current, attempt)

    return hook_url, assembled  # unreachable; satisfies type checker


def run(
    reel_type: str,
    lang: str = 'en',
    snapshot: dict | None = None,
) -> None:
    """End-to-end pipeline for one Higgsfield reel."""
    from captions import (weekly, trust, edu as edu_caption, broker as broker_caption)  # noqa: F401

    if snapshot is None:
        snapshot = load_snapshot()

    account    = snapshot.get('account', {})
    daily_gain = snapshot.get('dailyGain', [])
    today      = date.today()
    reel_index = int(today.strftime('%j'))
    voice_id   = os.environ.get('HIGGSFIELD_VOICE_EN_ID', '')

    REEL_DIR.mkdir(parents=True, exist_ok=True)
    out_path   = REEL_DIR / f'{today.isoformat()}-hf-{reel_type}-{lang}.mp4'
    thumb_path = REEL_DIR / f'{today.isoformat()}-hf-{reel_type}-{lang}-thumb.jpg'

    # ── Build script + caption ────────────────────────────────────────────────
    next_idx = None
    if reel_type == 'edu':
        idx              = read_counter()
        edu_type, edu_ct = get_edu_content(idx)
        script           = build_script('edu', account=account,
                                        edu_type=edu_type, edu_content=edu_ct,
                                        language=lang)
        caption          = edu_caption(edu_type, edu_ct, lang=lang)
        next_idx         = (idx + 1) % ROTATION_LEN

    elif reel_type == 'trust':
        script  = build_script('trust', account=account, language=lang)
        caption = trust(account, lang=lang)

    elif reel_type == 'weekly':
        gain    = float(account.get('gain') or 0)
        script  = build_script('weekly', account=account, weekly_gain=gain, language=lang)
        caption = weekly(account, lang=lang)

    elif reel_type == 'broker':
        script  = build_script('broker', account=account, language=lang)
        caption = broker_caption(lang=lang)

    else:
        raise ValueError(f'Unknown reel_type: {reel_type!r}')

    # ── Generate + virality gate ───────────────────────────────────────────────
    print(f'  [pipeline] generating {reel_type} ({lang})')
    hook_url, _ = _generate_with_virality_gate(script, out_path, reel_type, voice_id)

    # ── Data card composite ───────────────────────────────────────────────────
    _make_data_card(reel_type, snapshot, thumb_path)
    composite_data_card(
        video_url=hook_url,
        data_card_path=thumb_path,
        out_path=out_path,
    )

    # ── Commit EN reel to get public URL ─────────────────────────────────────
    en_video_url, thumb_gh_url = commit_and_push(out_path, thumb_path)
    print(f'  [pipeline] committed: {en_video_url}')

    # ── Tamil dub (after commit — needs public URL) ───────────────────────────
    if lang == 'tamil':
        video_url = dub_to_tamil_video(en_video_url)
        print(f'  [pipeline] Tamil dubbed: {video_url}')
    else:
        video_url = en_video_url

    # ── Hashtags ──────────────────────────────────────────────────────────────
    tags = get_hashtags_tamil(reel_index) if lang == 'tamil' else get_hashtags(reel_index)
    caption += '\n\n' + ' '.join(tags)

    # ── Publish ───────────────────────────────────────────────────────────────
    print('  [pipeline] waiting 60s for CDN...')
    time.sleep(60)
    publish_reel(video_url, caption, cover_url=thumb_gh_url)
    print(f'  [pipeline] published: {reel_type} ({lang})')

    # ── Increment edu counter after successful publish ─────────────────────────
    if next_idx is not None:
        write_counter(next_idx)


def main() -> None:
    reel_type = os.environ.get('REEL_TYPE', 'trust')
    lang      = os.environ.get('POST_LANG', 'en')
    print(f'Higgsfield pipeline: reel_type={reel_type} lang={lang}')
    run(reel_type=reel_type, lang=lang)
    print('Done.')


if __name__ == '__main__':
    main()
