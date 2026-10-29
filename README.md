Sum-of-squares optimization in Julia
====================================

Slides for the different presentations on [SumOfSquares.jl](https://github.com/jump-dev/SumOfSquares.jl).

The presentations are published at
[blegat.github.io/SumOfSquaresSlides](https://blegat.github.io/SumOfSquaresSlides/).
Each PDF has a stable URL such as `2019_JCON.pdf` or `2018_NCAG.pdf`.

To build every presentation locally, install the LaTeX packages listed in
`.github/workflows/pages.yml` and run:

```sh
python3 scripts/build_pages.py
```

`index.md` contains the presentation catalogue. Main files named
`<year>_<event>-slides.tex` or `<year>_<event>-poster.tex` are compiled
automatically from the corresponding `slides/` or `poster/` directory.
Julia is required to render the Markdown catalogue.
Compiled PDFs and `index.html` go to `_site/`; build logs go to `_build/`.
Presentations compile in copies under `_build/` so both minted v2 and v3
can find their generated highlighting files.
Only the generated PDFs and index are published. The build does not require
Drive or a user latexmk configuration.

The workflow builds pull requests without deploying. Pushes to `master` or
`main` (and manual runs on those branches) publish `_site/` to `gh-pages`.
For the initial setup, select **Settings → Pages → Deploy from a branch**,
then choose **gh-pages / (root)** after the first workflow run creates it.
