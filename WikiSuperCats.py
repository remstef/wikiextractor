#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Steffen Remus
"""

import sys
import click
import bz2
from concurrent.futures import ThreadPoolExecutor
from signal import signal, SIGPIPE, SIG_DFL; signal(SIGPIPE, SIG_DFL)


supercats = {}


def scan_super_categories(f):
    with bz2.BZ2File(f, 'r') if f.endswith('.bz2') else open(f, 'r') as fin:
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
                    cat_name = doc_title[doc_title.find(':')+1:].strip().replace(' ', '_')
                    supercats[cat_name] = categories
                doc_title = ''
                categories = []
                continue
            if '[[Category:' in line:
                li = line[line.find('[[Category:'):]
                cat = li.replace('[[Category:', '')
                cats = cat[:cat.find(']]')].split('|')
                for c in cats:
                    c_ = c.strip().replace(' ', '_')
                    if c_:
                        categories.append(c_)

    print('read {} lines, {} docs, {} categories.'.format(l, k, len(supercats)), file=sys.stderr)


def get_categories(f, parallel_threads):
    with ThreadPoolExecutor(max_workers=parallel_threads) as executor:
        with bz2.BZ2File(f, 'r') if f.endswith('.bz2') else open(f, 'r') as fin:
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

                    future = executor.submit(resolve_supercats_and_print_result, doc_id, doc_title, categories)
                    # print('{}:{}\t{}\t'.format(doc_id, doc_title, '\t'.join(resolve_supercats(categories))))
                    # print(future.result())
                    # future.result()

                    doc_title = ''
                    categories = []
                    continue
                if '[[Category:' in line:
                    li = line[line.find('[[Category:'):]
                    cat = li.replace('[[Category:', '')
                    cats = cat[:cat.find(']]')].split('|')
                    for c in cats:
                        c_ = c.strip().replace(' ', '_')
                        if c_:
                            categories.append(c_)
    print('read {} lines, {} docs.'.format(l, k), file=sys.stderr);


def resolve_supercats(cats):
    cats_and_supercats = set(cats)
    for cat in cats:
        if cat not in supercats:
            continue
        for supercat in supercats[cat]:
            if supercat not in cats_and_supercats and supercat:
                cats.append(supercat)
                cats_and_supercats.add(supercat)
    return cats_and_supercats


def resolve_supercats_and_print_result(doc_id, doc_title, categories):
    cats_resolved = resolve_supercats(categories)
    if "Foods" in cats_resolved:
        print('{}:{}\t{}\t'.format(doc_id, doc_title, '\t'.join(cats_resolved)))


@click.command()
@click.option('-i', '--infile', help='Wikipedia page dump documents.', required=True)
@click.option('-s', '--supercats', help='Resolve category hierarchy.', is_flag=True, required=False, default=False)
@click.option('-p', '--parallel', help='Set parallelism for resolving category hierarchies.', required=False, default=1)
def cli_run(infile, supercats, parallel):
    if supercats:
        scan_super_categories(infile)
    get_categories(infile, parallel)

if __name__ == '__main__':
    cli_run()
