#!/bin/env python3
from socket import gethostbyname
from queue import Queue, Empty
from argparse import ArgumentParser
from time import monotonic
from threading import Thread, Lock
from subprocess import Popen
from shutil import which
from glob import glob
from os.path import basename

NUM_OF_PROG = 3
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 Edg/114.0.1823.43'}


class Checker:
    bad = []
    total = []
    queue = Queue()
    workers = []
    updateLock = Lock()
    totalLock = Lock()
    badFile = f'urls_bad_{monotonic()}.txt'
    prev = 0

    def lookup(self, url):
        try:
           _ = gethostbyname(url)
        except Exception as e:
            with self.updateLock:
                self.bad.append(url)

    def worker(self):
        while True:
            try:
                url = self.queue.get(timeout=10)
                self.lookup(url)
                with self.totalLock:
                    self.total.append(1)

                if len(self.total) % 5000 == 0:
                    with self.updateLock:
                        c = monotonic()
                        print(f'{len(self.total)} completed {c- self.prev}')
                        print(f'{self.name}: Outputting bad urls')
                        f = open(self.badFile, 'a')
                        f.write('\n'.join(self.bad))
                        f.close()

                        self.prev = c
                        self.bad = []
                self.queue.task_done()
            except Empty:
                break

    def start(self, fil, spawn, name):
        if spawn:
            g = glob(fil)
            pids = []
            while True:
                if len(pids) < NUM_OF_PROG:
                    try:
                        h = g.pop()
                        cmd = f'{which("python3")} {__file__} -f {h} -n process-{basename(h)}'
                        print(cmd)
                        pids.append(
                            Popen(cmd, stdin=None, stdout=None, shell=True))
                    except Exception:
                        break
                else:
                    l = []
                    for i in pids:
                        if i.poll() is None:
                            l.append(i)
                            continue
                    pids = l
            print('Finished main loop waiting for last spawned programs')
            while len(pids) > 0:
                l = []
                for i in pids:
                    if i.poll() is None:
                        l.append(i)
                        continue
                pids = l
            print('Finished with spawned programs')
        else:
            self.name = name
            i = 0
            for i in range(15):
                t = Thread(target=self.worker)
                self.workers.append(t)
                t.start()

            started_at = monotonic()
            self.prev = started_at

            with open(fil) as f:
                for u in f:
                    self.queue.put_nowait(u.strip())

            print(f'{self.name}: Joining')
            self.queue.join()
            print(
                f'{self.name}: Normal downloading took {monotonic() - started_at} seconds')

            print(f'{self.name}: Outputting bad urls')
            with open(self.badFile, 'w') as f:
                f.write('\n'.join(self.bad))

            print(f'{self.name}: Finished')


parser = ArgumentParser("Get pihole block hosts")
parser.add_argument('-n', '--name')
parser.add_argument('-f', '--fil')
parser.add_argument('-p', '--spawn', action='store_true')

args = parser.parse_args()

c = Checker()
c.start(args.fil, args.spawn, args.name)
