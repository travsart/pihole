#!/bin/env python3
from requests import get
from argparse import ArgumentParser
from os.path import abspath


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36 Edg/106.0.1370.37'}


parser = ArgumentParser("Get pihole block hosts")
parser.add_argument('-i', '--infile', help='Path to url file')
parser.add_argument('-o', '--outfile', default='out.urls',
                    help='Path to output file')
args = parser.parse_args()

urlsFile = abspath(args.infile)
outFile = abspath(args.outfile)

urls = []
with open(urlsFile) as f:
    for i in f:
        urls.append(i.strip())

print('Checking urls')
o = []
index = 1
for u in urls:
    try:
        print(f'Getting {u}')
        r = get(u)
        if r.ok == False:
            print(f'failed to get url {u} {r.status_code}')
            continue
        r = r.text
        l = r.replace('\r', '').split('\n')
        if len(l) > 0:
            with open(f'file{index}','w') as f:
                f.write(f'{u}\n')
                f.write(r)
            index += 1
            o.append(u)
    except Exception as e:
        print(f'Failed to get {u} {e}')

print(f'Started with size {len(urls)} ended with size {len(o)}')

with open(outFile, 'w') as f:
    for i in o:
        f.write(i)
        f.write('\n')
