#!/usr/bin/env python3
"""
Fetch Instagram account insights to find optimal posting times.

Usage:
  python instagram/fetch_insights.py
  (requires IG_USER_ID and META_ACCESS_TOKEN env vars)

Output:
  - Best posting hours per day of week (from online_followers metric)
  - Top 10 posts by reach (to see which content performs best)
  - Recommended posting time window for @veralevel.fx
"""
import os, sys, json, requests
from datetime import datetime, timedelta, timezone

GRAPH = 'https://graph.facebook.com/v19.0'
IG_ID = os.environ.get('IG_USER_ID', '')
TOKEN = os.environ.get('META_ACCESS_TOKEN', '')

DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def get(path: str, **params) -> dict:
    r = requests.get(
        f'{GRAPH}/{path}',
        params={'access_token': TOKEN, **params},
        timeout=30,
    )
    if not r.ok:
        print(f'  [warn] {r.status_code}: {r.text[:200]}', file=sys.stderr)
        return {}
    return r.json()


def fetch_online_followers() -> dict:
    """Returns {day_of_week: {hour: follower_count}} — when your audience is online."""
    data = get(f'{IG_ID}/insights', metric='online_followers', period='lifetime')
    if not data or 'data' not in data:
        print('  [warn] online_followers metric not available (may require 100+ followers)')
        return {}
    try:
        return data['data'][0]['values'][0]['value']
    except (KeyError, IndexError, TypeError):
        return {}


def fetch_media_insights(since_days: int = 90) -> list[dict]:
    """Return reach + impressions for last N days of posts."""
    until = datetime.now(timezone.utc)
    since = until - timedelta(days=since_days)

    media = get(
        f'{IG_ID}/media',
        fields='id,timestamp,media_type',
        since=int(since.timestamp()),
        until=int(until.timestamp()),
        limit=50,
    )
    if not media.get('data'):
        return []

    results = []
    for post in media['data']:
        mid = post['id']
        ins = get(f'{mid}/insights', metric='reach,impressions,engagement')
        if not ins.get('data'):
            continue
        row = {
            'id':        mid,
            'type':      post.get('media_type'),
            'posted_at': post.get('timestamp'),
        }
        for m in ins['data']:
            row[m['name']] = m['values'][0]['value'] if m.get('values') else m.get('value', 0)
        results.append(row)
    return results


def print_online_hours(online: dict) -> None:
    if not online:
        return
    print('\n── When your followers are online (SGT = UTC+8) ──')
    for day_idx_str, hours in sorted(online.items(), key=lambda x: int(x[0])):
        day_idx = int(day_idx_str)
        day     = DAYS[day_idx]
        if not hours:
            continue
        best_hours = sorted(hours.items(), key=lambda x: -int(x[1]))[:3]
        best_str   = ', '.join(
            f'{(int(h) + 8) % 24:02d}:00 SGT ({v} online)' for h, v in best_hours
        )
        print(f'  {day}: {best_str}')


def print_top_posts(posts: list[dict]) -> None:
    if not posts:
        return
    print('\n── Top 10 posts by reach (last 90 days) ──')
    by_reach = sorted(posts, key=lambda x: -x.get('reach', 0))[:10]
    for p in by_reach:
        ts   = p.get('posted_at', '')
        dt   = datetime.fromisoformat(ts.rstrip('Z')).replace(tzinfo=timezone.utc)
        sgt  = dt + timedelta(hours=8)
        day  = DAYS[sgt.weekday()]
        hour = sgt.strftime('%H:%M')
        print(f"  {day} {hour} SGT | reach={p.get('reach',0):,} | imp={p.get('impressions',0):,} | {p['type']}")


def recommend(online: dict, posts: list[dict]) -> None:
    print('\n── Recommendation for @veralevel.fx ──')
    if not online and not posts:
        print('  Not enough data. Run again after 30+ days of posting.')
        return

    # Best hour from online_followers (average across all days)
    if online:
        hour_totals: dict[int, int] = {}
        for hours in online.values():
            for h, v in hours.items():
                hour_totals[int(h)] = hour_totals.get(int(h), 0) + int(v)
        best_utc_hour = max(hour_totals, key=lambda h: hour_totals[h])
        best_sgt_hour = (best_utc_hour + 8) % 24
        print(f'  Peak audience hour: {best_sgt_hour:02d}:00 SGT')

    # Best day from post performance
    if posts:
        day_reach: dict[str, list] = {d: [] for d in DAYS}
        for p in posts:
            ts  = p.get('posted_at', '')
            dt  = datetime.fromisoformat(ts.rstrip('Z')).replace(tzinfo=timezone.utc)
            sgt = dt + timedelta(hours=8)
            day_reach[DAYS[sgt.weekday()]].append(p.get('reach', 0))
        avg_by_day = {d: (sum(v) / len(v)) for d, v in day_reach.items() if v}
        best_day = max(avg_by_day, key=lambda d: avg_by_day[d])
        print(f'  Best performing day: {best_day} (avg reach {avg_by_day[best_day]:,.0f})')

    print()
    print('  Current schedule: 06:00 SGT static · 07:00 SGT reel · 20:00 SGT daily reel')
    print('  If peak hour differs significantly from 06:00–07:00 SGT,')
    print('  update insta-post.yml and insta-reel.yml crons accordingly.')


def main():
    if not IG_ID or not TOKEN:
        sys.exit('Set IG_USER_ID and META_ACCESS_TOKEN env vars first.')

    print('Fetching Instagram insights…')
    online = fetch_online_followers()
    posts  = fetch_media_insights(since_days=90)

    print(f'  {len(posts)} posts analysed')

    print_online_hours(online)
    print_top_posts(posts)
    recommend(online, posts)


if __name__ == '__main__':
    main()
