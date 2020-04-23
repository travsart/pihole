#!/bin/env python3
import sys
from urllib.request import Request, urlopen


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}


def get(url):
    ret = ''
    try:
        req = Request(url, headers=HEADERS)
        res = urlopen(req)
        ret = res.read()
        ret = ret.decode()
    except UnicodeDecodeError:
        ret = ret.decode('latin-1')
    except Exception as e:
        print(f'Problem getting url {url} with exception {e}')

    return ret


def inSkip(url, skip):
    try:
        for s in skip:
            if url.endswith(s):
                return True
    except Exception:
        pass
    return False


urls = []
with open(sys.argv[1]) as f:
    for i in f:
        urls.append(i.strip())

skip = []

if len(sys.argv) > 2:
    with open(sys.argv[2]) as f:
        for i in f:
            skip.append(i.strip())


data = []

print('Getting hosts')
for u in urls:
    try:
        print(f'Getting {u}')
        r = get(u)
        if r == '':
            print(f'failed to get url {u}')
            continue

        r = r.replace('\r', '')

        if '\n' in r:
            for i in r.split('\n'):
                i = i.strip()
                if i == '':
                    continue
                if i == 'Malvertising list by Disconnect':
                    continue
                if '#' in i:
                    continue
                if '0.0.0.0' in i or '127.0.0.1' in i:
                    i = i.split()[1].strip()
                if i == '':
                    continue
                if 'localhost' in i or i == 'broadcasthost' or i == 'local' or 'ip6-localnet' in i or 'ip6-mcastprefix' in i or 'ip6-all' in i or i == '0.0.0.0':
                    continue
                if len(skip) > 0:
                    if inSkip(i, skip):
                        continue
                data.append(i)
        data = list(set(data))
    except Exception as e:
        print(f'Failed getting {u} {e}')
        continue
print('Sorting list')
data = sorted(data)

print('Writing list')
with open('outHost.txt', 'w') as f:
    f.writelines('%s\n' % d for d in data)
