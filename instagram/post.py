import os
import time
import requests

GRAPH = 'https://graph.facebook.com/v19.0'
IG_ID = os.environ['IG_USER_ID']
TOKEN = os.environ['META_ACCESS_TOKEN']

_IB_COMMENT = 'https://www.icmarkets.com/global/en/?camp=91936'


def _check(r: requests.Response):
    if not r.ok:
        raise RuntimeError(f"Meta API error {r.status_code}: {r.text}")
    return r.json()


def _post_first_comment(post_id: str) -> None:
    """Pin the IC Markets referral URL as the first comment on any published post."""
    try:
        _check(requests.post(
            f'{GRAPH}/{post_id}/comments',
            params={'message': _IB_COMMENT, 'access_token': TOKEN},
        ))
        print(f'  first comment: {_IB_COMMENT}')
    except Exception as e:
        print(f'  [warn] first comment failed: {e}')


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

    # Wait for Instagram to process the image
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
    _post_first_comment(post_id)
    return post_id


def publish_reel(video_url: str, caption: str, cover_url: str = '') -> str:
    """Publish a video as an Instagram Reel.

    Two-step Meta Graph API: create container → poll until FINISHED → publish.
    Poll timeout is 5 minutes (30 × 10s — video encoding is slower than images).
    cover_url — optional public JPEG URL used as the reel cover/thumbnail.
    """
    params = {
        'media_type':   'REELS',
        'video_url':    video_url,
        'caption':      caption,
        'access_token': TOKEN,
    }
    if cover_url:
        params['cover_url'] = cover_url
    data = _check(requests.post(f'{GRAPH}/{IG_ID}/media', params=params))
    container_id = data['id']
    print(f'  reel container created: {container_id}')

    for attempt in range(30):          # 30 × 10s = 5 minutes
        time.sleep(10)
        status = _check(requests.get(
            f'{GRAPH}/{container_id}',
            params={'fields': 'status_code', 'access_token': TOKEN}
        ))
        code = status.get('status_code')
        if code == 'FINISHED':
            break
        print(f'  encoding… ({code}) attempt {attempt + 1}/30')
    else:
        raise TimeoutError('Reel container did not finish processing within 5 minutes')

    result = _check(requests.post(
        f'{GRAPH}/{IG_ID}/media_publish',
        params={
            'creation_id':  container_id,
            'access_token': TOKEN,
        }
    ))
    post_id = result['id']
    print(f'  reel published: {post_id}')
    _post_first_comment(post_id)
    return post_id
