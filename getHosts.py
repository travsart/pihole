#!/bin/env python3
from argparse import ArgumentParser
from locale import strcoll
from os.path import abspath
from os import fstat

from requests import get

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
MAX_SIZE = 1024 * 1024 * 60  # 60 MB
WHOLE_FILE = 'whole.txt'


def inSkip(url, skip):
    try:
        for s in skip:
            if url.endswith(s):
                return True
    except Exception:
        pass
    return False


def writeFiles(data, base):
    index = 1
    while len(data) > 0:
        f = open(f'{base}{index}.txt', 'w')

        while len(data) > 0:
            d = data.pop()
            line = f'{d}\n'
            f.write(line)
            size = fstat(f.fileno()).st_size

            if(size > MAX_SIZE):
                break
        index += 1


def parse(r: str, data: list, ignore: list, raw: list):
    r = r.replace('\r', '')
    if '\n' in r:
        for i in r.split('\n'):
            try:
                raw.append(i)
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
                if '.' not in i or i.startswith('.'):
                    continue
                if ';' in i:
                    i = i.split(';')[0].strip()
                if ':' in i:
                    i = i.split(':')[0].strip()
                if '@' in i:
                    i = i.split('@')[0].strip()
                if '|' in i:
                    i = i.replace('|', '')
                if '^' in i:
                    i = i.replace('^', '')
                if i.startswith('-'):
                    i = i[1:]
                if i.isascii():
                    if i not in ignore:
                        data.append(i)
            except Exception as e:
                print(f'Failed parsing {u} {e} {org} {i}')
                continue
    return list(set(data))


parser = ArgumentParser("Get pihole block hosts")
parser.add_argument('-r', '--raw', help='Write out a raw file', action='store_true')
parser.add_argument('-u', '--urlsfile', help='Path to url file')
parser.add_argument('-s', '--skipfile', help='Path to skip urls file')
parser.add_argument('-a', '--addfile', help='Path to add urls file')
parser.add_argument('-i', '--ignore', help='Path to ignore urls file')
parser.add_argument('-o', '--outfile', default='out.txt',
                    help='Path to output file')
args = parser.parse_args()

urlsFile = abspath(args.urlsfile)
outFile = abspath(args.outfile)

urls = []
with open(urlsFile) as f:
    for i in f:
        urls.append(i.strip())

skip = []
if args.skipfile is not None:
    skipFile = abspath(args.skipfile)

    with open(skipFile) as f:
        for i in f:
            skip.append(i.strip())

addList = []
if args.addfile is not None:
    addFile = abspath(args.addfile)

    with open(addFile) as f:
        for i in f:
            addList.append(i.strip())

ignore = []
if args.ignore is not None:
    ignoreFile = abspath(args.ignore)

    with open(ignoreFile) as f:
        for i in f:
            ignore.append(i.strip())

data = []

print('Getting hosts')
for u in urls:
    try:
        raw = []
        print(f'Getting {u}')
        r = get(u, headers=HEADERS)
        if r.ok == False:
            print(f'failed to get url {u}')
            continue
        r = r.text

        data = parse(r, data, ignore, raw)

        if args.raw:
            with open(WHOLE_FILE, 'a') as f:
                for i in raw:
                    f.write(i)
                    f.write('\n')

    except Exception as e:
        print(f'Failed getting {u} {e}')
        continue

print('Adding custom hosts')
for i in addList:
    data.append(i)

print('Sorting list')
data = list(set(data))
data = sorted(data)

writeFiles(data, outFile)

# Use when pihole supports compressed addlists
# print(f'Writing list to {outFile}.gz')
# with gzip.open(f'{outFile}.gz', 'w') as f:
#     for d in data:
#         line = f'{d}\n'.encode()
#         f.write(line)
