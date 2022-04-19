#!/bin/env python3
from sys import argv
from requests import get
from argparse import ArgumentParser
from os.path import abspath

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}

def inSkip(url, skip):
    try:
        for s in skip:
            if url.endswith(s):
                return True
    except Exception:
        pass
    return False

parser = ArgumentParser("Get pihole block hosts")
parser.add_argument('-u', '--urlsfile', help='Path to url file')
parser.add_argument('-s', '--skipfile', help='Path to skip urls file')
parser.add_argument('-a', '--addfile', help='Path to add urls file')
parser.add_argument('-o', '--outfile', default='out.txt', help='Path to output file')
args = parser.parse_args()

urlsFile = abspath(args.urlsfile)
skipFile = abspath(args.urlsfile)
addFile = abspath(args.urlsfile)
outFile = abspath(args.urlsfile)

urls = []
with open(urlsFile) as f:
    for i in f:
        urls.append(i.strip())

skip = []
with open(skipFile) as f:
    for i in f:
        skip.append(i.strip())

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.44'
}
data = []

print('Getting hosts')
for u in urls:
    try:
        print(f'Getting {u}')
        r = get(u)
        if r.ok == False:
            print(f'failed to get url {u}')
            continue
        r = r.text
        r = r.replace('\r', '')

        if '\n' in r:
            for i in r.split('\n'):
                try:
                    org = i
                    i = i.strip()
                    if i == '':
                        continue
                    if i == 'Malvertising list by Disconnect':
                        continue
                    if '#' in i:
                        continue
                    if '0.0.0.0' in i or '127.0.0.1' in i:
                        if len(i.split()) > 1:
                            i = i.split()[1].strip()
                        else: 
                            continue
                    if i == '':
                        continue
                    if 'localhost' in i or i == 'broadcasthost' or i == 'local' or 'ip6-localnet' in i or 'ip6-mcastprefix' in i or 'ip6-all' in i or i == '0.0.0.0':
                        continue
                    if len(skip) > 0:
                        if inSkip(i, skip):
                            continue
                    if ';' in i:
                        i = i.split(';')[0].strip()
                    if ':' in i:
                        i = i.split(':')[0].strip()
                    if '@' in i:
                        i = i.split('@')[0].strip()
                    if i.isascii():
                        data.append(i)
                except Exception as e:
                    print(f'Failed parsing {u} {e} {org} {i}')
                    continue
        data = list(set(data))
    except Exception as e:
        print(f'Failed getting {u} {e}')
        continue

print('Adding custom hosts')
with open(addFile) as f:
    for i in f:
        data.append(i.strip())

print('Sorting list')
data = list(set(data))
data = sorted(data)

print(f'Writing list to {outFile}')
with open(outFile, 'w') as f:
    f.writelines('%s\n' % d for d in data)
