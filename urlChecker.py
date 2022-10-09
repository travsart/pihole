#!/bin/env python3

from whois import whois


urls = []
with open('outHost1.txt') as f:
    for i in f:
        urls.append(i.strip())
with open('outHost2.txt') as f:
    for i in f:
        urls.append(i.strip())

purls = []
with open('outpHost1.txt') as f:
    for i in f:
        purls.append(i.strip())
with open('outpHost2.txt') as f:
    for i in f:
        purls.append(i.strip())
with open('outpHost3.txt') as f:
    for i in f:
        purls.append(i.strip())

print(f'Normal {len(urls)} P {len(purls)}')
new = []
bad = []
for u in urls:
    try:
        get_info = whois(u)
        new.append(u)   
    except:
        bad.append(u)
        pass
print('Outputting valid urls')
with open('urls_new.txt','w') as f:
    f.write('/n'.join(new))

with open('urls_bad.txt','w') as f:
    f.write('/n'.join(bad))

newp = []
badp = []
for u in purls:
    try:
        get_info = whois(u)
        newp.append(u)
    except:
        badp.append(u)
        pass

with open('purls_new.txt','w') as f:
    f.write('/n'.join(newp))

with open('urls_badp.txt','w') as f:
    f.write('/n'.join(badp))

