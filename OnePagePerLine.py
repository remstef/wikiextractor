#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Steffen Remus
"""

import sys
import click
from signal import signal, SIGPIPE, SIG_DFL; signal(SIGPIPE, SIG_DFL)


def one_page_per_line(fin):
    print('Reading wiki docs.', file=sys.stderr)
    k, l = 0, 0
    page_lines = []
    for line in fin:
        l += 1
        if l % 10000 == 0:
            print('line {}'.format(l), file=sys.stderr)
        line = line.lstrip() \
            .replace('\r', '')\
            .replace('\n', '\\n')\
            .replace('\t', '\\t')

        if line.startswith('<page'):
            k += 1
            # a new doc starts
            del page_lines[:]

        page_lines.append(line)

        if line.startswith('</page'):
            # a doc ends
            print(''.join(page_lines), file=sys.stdout)
            del page_lines[:]
            continue

    print('read {} lines into {} page lines.'.format(l, k), file=sys.stderr)


@click.command()
@click.option('-i', '--infile', help='Wikipedia page dump documents. Specify "-" to read from stdin.', type=click.File('r'), required=False, default='-')
def cli_run(infile):
    one_page_per_line(infile)


if __name__ == '__main__':
    cli_run()
