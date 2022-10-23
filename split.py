#!/bin/env python3
from sys import argv


def writeFiles(data, base):
    index = 1
    while len(data) > 0:
        f =  open(f'{base}{index}.txt', 'w')
        i = 0 
        while len(data) > 0:
            d = data.pop()
            line = f'{d}\n'
            f.write(line)
            i += 1
            if i > 5000:
                break
        index += 1
d = []
with open(argv[1]) as f:
    for i in f:
        d.append(i.strip())

writeFiles(d,'test_')
