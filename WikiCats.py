#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Steffen Remus
"""

import sys
import click
from signal import signal, SIGPIPE, SIG_DFL; signal(SIGPIPE, SIG_DFL)


def get_categories(fin):
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
            k += 1
            # a new doc starts
            continue
        if line.startswith('<id'):
            doc_id = line.replace('<id>', '').replace('</id>', '').strip()
            continue
        if line.startswith('<title'):
            doc_title = line.replace('<title>', '').replace('</title>', '').strip()
            continue
        if line.startswith('</page'):
            print('{}:{}\t{}\t'.format(doc_id, doc_title, '\t'.join(categories)))
            doc_title = ''
            del categories[:]
            continue
        if '[[Category:' in line:
            li = line[line.find('[[Category:'):]
            cat = li.replace('[[Category:', '')
            cats = cat[:cat.find(']]')].split('|')
            for c in cats:
                c_ = c.strip().replace(' ', '_')
                if c_:
                    categories.append(c_)
    print('read {} lines, {} docs.'.format(l, k), file=sys.stderr)


@click.command()
@click.option('-i', '--infile', help='Wikipedia page dump documents. Specify "-" to read from stdin.', type=click.File('r'), required=False, default='-')
def cli_run(infile):
    get_categories(infile)


if __name__ == '__main__':
    cli_run()
