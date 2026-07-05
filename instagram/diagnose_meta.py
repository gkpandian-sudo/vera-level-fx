"""
Run locally to diagnose Meta API permission state.

  $env:META_ACCESS_TOKEN = "your-token-here"
  $env:IG_USER_ID = "17841423399956054"
  python instagram/diagnose_meta.py
"""

import os, requests, json, sys

GRAPH = 'https://graph.facebook.com/v19.0'
TOKEN = os.environ['META_ACCESS_TOKEN']
IG_ID = os.environ['IG_USER_ID']           # no fallback — must be set explicitly
APP_ID = os.environ['META_APP_ID']         # set: $env:META_APP_ID = "your-app-id"
APP_SECRET = os.environ.get('APP_SECRET', '')


def get(path, **params):
    r = requests.get(f'{GRAPH}/{path}', params={'access_token': TOKEN, **params})
    return r.status_code, r.json()


def section(title):
    print(f'\n{"="*60}')
    print(f'  {title}')
    print('='*60)


section('1. Token identity')
status, data = get('me', fields='id,name')
print(json.dumps(data, indent=2))

section('2. Token debug — granted permissions')
debug_url = f'{GRAPH}/debug_token'
r = requests.get(debug_url, params={
    'input_token': TOKEN,
    'access_token': f'{APP_ID}|{APP_SECRET}' if APP_SECRET else TOKEN,
})
debug = r.json().get('data', {})
print(f"App ID:    {debug.get('app_id')}")
print(f"Type:      {debug.get('type')}")
print(f"Valid:     {debug.get('is_valid')}")
print(f"Expires:   {debug.get('expires_at', 'never')}")
print(f"Scopes:    {', '.join(debug.get('scopes', []))}")

section('3. Facebook Pages visible to this token')
status, data = get('me/accounts', fields='id,name,instagram_business_account')
pages = data.get('data', [])
for page in pages:
    ib = page.get('instagram_business_account', {})
    print(f"  Page: {page['name']} (ID: {page['id']})")
    print(f"    → IG business account: {ib.get('id', 'NOT LINKED')}")

section(f'4. Direct IG account lookup — {IG_ID}')
status, data = get(IG_ID, fields='id,username,name,biography')
print(f"HTTP {status}: {json.dumps(data, indent=2)}")

section('5. Try creating a test media container (dry-run check)')
r = requests.post(
    f'{GRAPH}/{IG_ID}/media',
    params={
        'image_url': 'https://via.placeholder.com/1080',
        'caption': 'test',
        'access_token': TOKEN,
    }
)
print(f"HTTP {r.status_code}: {r.text}")
