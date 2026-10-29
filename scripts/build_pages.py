#!/usr/bin/env python3
"""Compile the presentation manifest and create a PDF-only Pages site."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import os
from pathlib import Path
import shutil
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_site'


def build(document):
    output = ROOT / '_build' / document['name']
    if output.exists():
        shutil.rmtree(output)
    # Keep the source tree's depth so ../../images and shared macros still resolve.
    # Build in place in this copy: minted v2 cannot find files in a separate outdir.
    shutil.copytree(ROOT / document['directory'], output)
    env = os.environ.copy()
    env['TEXINPUTS'] = f'.:{ROOT}:{ROOT}/images:' + env.get('TEXINPUTS', '')
    env['BIBINPUTS'] = f'.:{ROOT}:' + env.get('BIBINPUTS', '')
    with (output / 'build.log').open('w') as log:
        result = subprocess.run(
            ['latexmk', '-norc', '-pdf', '-shell-escape', '-interaction=nonstopmode',
             '-halt-on-error', '-file-line-error', document['main']],
            cwd=output, env=env,
            stdout=log, stderr=subprocess.STDOUT, timeout=600,
        )
    if result.returncode:
        log_path = output / 'build.log'
        excerpt = '\n'.join(log_path.read_text(errors='replace').splitlines()[-80:])
        print(f"FAIL {document['name']}: {log_path}\n{excerpt}", flush=True)
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
    documents = []
    for kind in ('slides', 'poster'):
        for source in sorted(ROOT.glob(f'[0-9][0-9][0-9][0-9]_*/{kind}/*-{kind}.tex')):
            name = source.parent.parent.name
            if source.stem != f'{name}-{kind}':
                continue
            documents.append({'name': name, 'directory': str(source.parent.relative_to(ROOT)),
                              'main': source.name})
    if not documents or len({d['name'] for d in documents}) != len(documents):
        raise SystemExit('No presentations found, or multiple presentations share an output name')
    # Start fresh so removed presentations or failed builds cannot publish old PDFs.
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        results = list(executor.map(build, documents))
    if not all(results):
        raise SystemExit(1)
    # Julia's standard Markdown library renders the catalogue maintained in index.md.
    html = subprocess.check_output(
        ['julia', '--startup-file=no', '-e',
         'using Markdown; show(stdout, MIME("text/html"), Markdown.parse(read(ARGS[1], String)))',
         str(ROOT / 'index.md')], text=True,
    )
    class PDFLinks(HTMLParser):
        def handle_starttag(self, tag, attributes):
            if tag != 'a':
                return
            link = urlsplit(dict(attributes).get('href', ''))
            if link.scheme or link.netloc or not link.path.endswith('.pdf'):
                return
            pdf = (SITE / unquote(link.path)).resolve()
            if not pdf.is_relative_to(SITE.resolve()) or not pdf.is_file():
                raise ValueError(f'Catalogue links to a missing PDF: {link.path}')

    PDFLinks().feed(html)
    (SITE / 'index.html').write_text(
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>Sum-of-squares optimization in Julia</title>\n</head>\n<body>\n'
        f'{html}\n</body>\n</html>\n'
    )
    (SITE / '.nojekyll').touch()


if __name__ == '__main__':
    main()
