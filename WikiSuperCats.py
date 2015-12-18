#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Steffen Remus
"""

import sys
import click
import bz2
from signal import signal, SIGPIPE, SIG_DFL; signal(SIGPIPE, SIG_DFL)


supercats = {}


def scan_super_categories(f):
    with bz2.open(f, 'r') if f.endsWith('.bz2') else open(f, 'r') as fin:
        print('reading wiki docs.', file=sys.stderr)
        k, l = 0, 0
        categories = []
        doc_title = ''
        for line in fin:
            l += 1
            if l % 10000 == 0:
                print('line {}'.format(l),file=sys.stderr)
            line = line.strip()
            if not line:
                # empty line
                continue
            if line.startswith('<page'):
                # a new doc starts
                k += 1
                continue
            if line.startswith('<title'):
                doc_title = line.replace('<title>', '').replace('</title>', '').strip()
                continue
            if line.startswith('</page'):
                if categories and doc_title.lower().startswith('category:'):
                    supercats[doc_title.find(':')+1:] = categories
                doc_title = ''
                categories = []
                continue
            if line.startswith('[[Category:'):
                cat = line.replace('[[Category:', '')
                cats = cat[:cat.find(']]')].split('|')
                for c in cats:
                    categories.append(c.strip().replace(' ', '_'))

    print('read {} lines, {} docs, {} categories.'.format(l, k), file=sys.stderr)


def get_categories(f):
    with bz2.open(f, 'r') if f.endsWith('.bz2') else open(f, 'r') as fin:
        print('reading wiki docs.', file=sys.stderr)
        k, l = 0, 0
        categories = []
        doc_title = ''
        doc_id = ''
        for line in fin:
            l += 1
            if l % 10000 == 0:
                print('line {}'.format(l),file=sys.stderr)
            line = line.strip()
            if not line:
                # empty line
                continue
            if line.startswith('<page'):
                # a new doc starts
                continue
            if line.startswith('<id'):
                doc_id = line.replace('<id>', '').replace('</id>', '').strip()
                continue
            if line.startswith('<title'):
                doc_title = line.replace('<title>', '').replace('</title>', '').strip()
                continue
            if line.startswith('</page'):
                k += 1
                print('{}:{}\t{}\t'.format(doc_id, doc_title, '\t'.join(resolve_supercats(categories))))
                doc_title = ''
                del categories[:]
                continue
            if line.startswith('[[Category:'):
                cat = line.replace('[[Category:', '')
                cats = cat[:cat.find(']]')].split('|')
                for c in cats:
                    categories.append(c.strip().replace(' ', '_'))
    print('read {} lines, {} docs.'.format(l, k), file=sys.stderr);

def resolve_supercats(cats):
    cats_and_supercats = set(cats)

    for cat in cats:
        if cat not in supercats:
            continue
        for supercat in supercats[cat]:
            if supercat not in cats_and_supercats:
                cats.extend(supercat)


@click.command()
@click.option('-f', '--infile', help='Wikipedia page dump documents.', type=click.String, required=True)
@click.option('-s', '--supercats', help='Resolve category hierarchy.', required=False, default=False)
def cli_run(infile, supercats):
    if supercats:
        scan_super_categories(infile)
    get_categories(infile)

if __name__ == '__main__':
    cli_run()
