#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Steffen Remus
"""

import sys
import click
from signal import signal, SIGPIPE, SIG_DFL; signal(SIGPIPE, SIG_DFL)


def one_doc_per_line(fin):
    print('reading wiki docs.', file=sys.stderr)
    d, k, l = 0, 0, 0
    doc = ''
    for line in fin:
        l += 1
        if l % 10000 == 0:
            print('line {}'.format(l),file=sys.stderr)
        line = line.strip()

        if line.startswith('<doc'):
            # a new doc starts
            # line format: <doc id="2" url="http://simple.wikipedia.org/wiki?curid=2" title="August">
            # TODO: add id!
            doc = line[line.find('title="')+7:line.rfind('"')] + '\t'
            d += 1
            continue
        if line.startswith('</doc'):
            if len(doc) > 20:
                k += 1
                print(doc)
            doc = ''
            continue

        doc += '\\n' + line.replace('\t', '\\t')

    if doc and len(doc) > 20:
        k += 1
        print(doc)

    print('Read {} lines and {} docs, printed {} docs, skipped {} docs that did not meet requirements.'.format(l, d, k, d-k), file=sys.stderr);


@click.command()
@click.option('-f', '--infile', help='File wikipedia documents in the form "<doc id=..." extracted by WikiExtractor.py. Specify "-" to read from stdin.', type=click.File('r'), required=False, default='-')
def cli_run(infile):
    one_doc_per_line(infile)

if __name__ == '__main__':
    cli_run()
