#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Steffen Remus
"""

import sys
import click
from signal import signal, SIGPIPE, SIG_DFL; signal(SIGPIPE, SIG_DFL)

articles = set()


def get_article_ids(fin):
    print('reading category file.', file=sys.stderr)
    l = 0
    for line in fin:
        l += 1
        if l % 10000 == 0:
            print('line {}'.format(l),file=sys.stderr)
        line = line.strip()
        splits = line.split('\t')
        id = splits[0][:splits[0].find(':')]
        articles.add(int(id))
    print('Read {} lines.'.format(l), file=sys.stderr)


def get_articles(fin):
    print('reading doc file.', file=sys.stderr)
    l = 0
    for line in fin:
        l += 1
        if l % 10000 == 0:
            print('line {}'.format(l),file=sys.stderr)
        splits = line.split('\t')
        id = int(splits[0])
        if id in articles:
            print(line)
    print('Read {} lines.'.format(l), file=sys.stderr)



@click.command()
#@click.option('-c', '--categories', help='List of desired category articles separated by ; ', required=False, default='')
@click.option('-i', '--infile', help='One wiki doc per line. Specify "-" to read from stdin. Format: <id> tab <title> tab <text>', type=click.File('r'), required=False, default='-')
@click.option('-cf', '--categories-file', help='Categories file. Contains article to category mapping. Format: <id:title> tab (<category> tab)*', type=click.File('r'), required=True)
def cli_run(infile, categories_file):
    get_article_ids(categories_file)
    get_articles(infile)

if __name__ == '__main__':
    cli_run()
