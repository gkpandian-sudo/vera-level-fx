"""
One-off data correction notice — publishes a single card to Instagram
explaining the four data accuracy fixes deployed 2026-07-19.
"""
import json, os, subprocess, sys, time
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'instagram'))

NAVY    = '#010E1F'
EMERALD = '#059669'
WHITE   = '#FFFFFF'
MUTED   = '#B8CFEA'
RED     = '#EF4444'
GOLD    = '#F59E0B'


def make_card() -> plt.Figure:
    fig = plt.figure(figsize=(10.8, 10.8), dpi=100, facecolor=NAVY)
    ax  = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(NAVY)
    ax.set_xlim(0, 1080)
    ax.set_ylim(0, 1080)
    ax.axis('off')

    # Brand bar top
    ax.add_patch(mpatches.FancyBboxPatch(
        (0, 1050), 1080, 30, boxstyle='square,pad=0',
        facecolor=EMERALD, edgecolor='none'))

    # Header
    ax.text(540, 990, 'DATA CORRECTION NOTICE', ha='center', va='center',
            fontsize=30, fontweight='bold', color=WHITE, fontfamily='monospace')
    ax.text(540, 950, 'Four metrics were showing stale data. Now fixed.',
            ha='center', va='center', fontsize=14, color=MUTED)

    ax.axhline(y=920, xmin=0.06, xmax=0.94, color=EMERALD, linewidth=1)

    fixes = [
        ('DAILY RETURN',
         'Before: historical avg (-2.44%) — not today\'s result',
         'After:  actual day\'s trading P&L from Myfxbook chart'),
        ('WEEKLY REEL',
         'Before: total account return (-97.27%)',
         'After:  this week\'s gain calculated from daily data'),
        ('MONTHLY CHART',
         'Before: bars sorted alphabetically (Apr, Feb, Jul…)',
         'After:  chronological order (Feb → Mar → Apr…)'),
        ('WIN RATE',
         'Before: 40% from a limited 40-trade API sample',
         'After:  70% verified across all 968 closed trades'),
    ]

    y = 870
    for title, before, after in fixes:
        ax.text(64, y, title, ha='left', va='top',
                fontsize=13, fontweight='bold', color=GOLD)
        ax.text(64, y - 36, before, ha='left', va='top',
                fontsize=11, color='#FC8181', fontfamily='monospace')
        ax.text(64, y - 68, after, ha='left', va='top',
                fontsize=11, color='#6EE7B7', fontfamily='monospace')
        y -= 130

    ax.axhline(y=y - 10, xmin=0.06, xmax=0.94, color=MUTED, linewidth=0.6, alpha=0.3)

    ax.text(540, y - 50, 'I track live. I post live. When something\'s wrong, I say it.',
            ha='center', va='center', fontsize=13, color=MUTED, style='italic')

    # Brand footer
    ax.add_patch(mpatches.FancyBboxPatch(
        (0, 0), 1080, 30, boxstyle='square,pad=0',
        facecolor=EMERALD, edgecolor='none'))
    ax.text(540, 15, '@veralevel.fx', ha='center', va='center',
            fontsize=12, fontweight='bold', color=NAVY)

    return fig


CAPTION = """\
Data correction 🔵

A few posts this week were showing stale numbers. Here's what was wrong and what's now fixed:

— Daily % was showing a historical average (-2.44%) instead of that day's actual result
— Weekly reel was showing total account return (-97.27%) instead of the week's actual gain
— Monthly bar chart was sorting alphabetically, not chronologically
— Win rate was pulling from a limited 40-trade API sample (40%) instead of the verified trade history (70% across 968 trades)

All four issues are fixed and deployed. Every number you see from here reflects what the market actually printed.

I track live. I post live. When something's wrong, I say it.

t.me/pandiangk
icmarkets.com/?camp=91936

⚠️ Forex trading involves significant risk of loss. This account is real and tracked live on Myfxbook. Past performance is not indicative of future results.

#veralevelFX #forextrader #fxtransparency #xauusd #eurusd #audcad #ICMarkets #forexaccountability #liveaccount"""


def commit_and_push(path: Path) -> str:
    repo   = os.environ.get('GITHUB_REPOSITORY', '')
    branch = 'master'
    rel    = path.relative_to(ROOT).as_posix()

    cmds = [
        ['git', 'config', 'user.email', 'github-actions[bot]@users.noreply.github.com'],
        ['git', 'config', 'user.name',  'github-actions[bot]'],
        ['git', 'add',    str(path)],
        ['git', 'commit', '-m', 'auto: correction notice post [skip ci]'],
        ['git', 'pull',   '--rebase', 'origin', branch],
        ['git', 'push',   'origin', branch],
    ]
    for cmd in cmds:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0 and 'nothing to commit' not in r.stdout + r.stderr:
            print(r.stderr, file=sys.stderr)

    return f'https://raw.githubusercontent.com/{repo}/{branch}/{rel}'


def main():
    from post import publish

    out = ROOT / 'instagram' / 'posts' / '2026-07-19-correction.png'
    out.parent.mkdir(parents=True, exist_ok=True)

    fig = make_card()
    fig.savefig(str(out), dpi=100, bbox_inches='tight', facecolor=NAVY)
    plt.close('all')
    print(f'  saved: {out}')

    image_url = commit_and_push(out)
    print(f'  url:   {image_url}')

    print('  waiting 60s for GitHub CDN...')
    time.sleep(60)

    publish(image_url, CAPTION)
    print('Done — correction notice posted.')


if __name__ == '__main__':
    main()
