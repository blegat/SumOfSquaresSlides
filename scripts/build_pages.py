#!/usr/bin/env python3
"""Compile the presentation manifest and create a PDF-only Pages site."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from html import escape
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_site'


def build(document):
    output = ROOT / '_build' / document['name']
    output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env['TEXINPUTS'] = f'.:{ROOT}:{ROOT}/images:' + env.get('TEXINPUTS', '')
    env['BIBINPUTS'] = f'.:{ROOT}:' + env.get('BIBINPUTS', '')
    with (output / 'build.log').open('w') as log:
        result = subprocess.run(
            ['latexmk', '-norc', '-pdf', '-shell-escape', '-interaction=nonstopmode',
             '-halt-on-error', '-file-line-error', f'-outdir={output}', document['main']],
            cwd=ROOT / document['directory'], env=env,
            stdout=log, stderr=subprocess.STDOUT, timeout=600,
        )
    if result.returncode:
        print(f"FAIL {document['name']}: {output / 'build.log'}", flush=True)
        return False
    pdf = output / Path(document['main']).with_suffix('.pdf')
    shutil.copyfile(pdf, SITE / (document['name'] + '.pdf'))
    print(f"OK {document['name']}.pdf", flush=True)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobs', type=int, default=2)
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error('--jobs must be positive')
    documents = json.loads((ROOT / 'documents.json').read_text())
    # Start fresh so removed presentations or failed builds cannot publish old PDFs.
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        results = list(executor.map(build, documents))
    if not all(results):
        raise SystemExit(1)
    links = '\n'.join(
        f'<li><a href="{escape(d["name"])}.pdf">{escape(d["name"])}: '
        f'{escape(d["title"])}</a></li>'
        for d in sorted(documents, key=lambda d: d['name'], reverse=True)
    )
    (SITE / 'index.html').write_text(
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>Sum-of-squares optimization in Julia</title>\n</head>\n<body>\n'
        '<h1>Sum-of-squares optimization in Julia</h1>\n'
        '<p>Slides and posters about SumOfSquares.jl, JuMP, and polynomial optimization.</p>\n'
        f'<ul>\n{links}\n</ul>\n'
        '<p><a href="https://github.com/blegat/SumOfSquaresSlides">Presentation sources</a></p>\n'
        '</body>\n</html>\n'
    )
    (SITE / '.nojekyll').touch()


if __name__ == '__main__':
    main()
