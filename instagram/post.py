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
    return post_id
