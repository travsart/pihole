#!/bin/env python3

from glob import glob
from sys import argv

l = []
for g in glob(argv[1]):
    with open(g) as f:
        for i in f:
            l.append(i.strip())

with open('bad.txt','w') as f:
    f.write('\n'.join(l)) 