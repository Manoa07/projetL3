import requests
from config import API_BASE_URL, API_TIMEOUT

print('Requesting', API_BASE_URL + '/cours/all', 'with timeout', API_TIMEOUT)
try:
    r = requests.get(API_BASE_URL + '/cours/all', timeout=API_TIMEOUT)
    print('Status', r.status_code)
    print('Body (truncated):')
    print(r.text[:2000])
except Exception as e:
    print('ERROR', repr(e))
