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

`documents.json` lists the main files and the titles displayed on the index.
Compiled PDFs and `index.html` go to `_site/`; build logs go to `_build/`.
Only the generated PDFs and index are published. The build does not require
Drive or a user latexmk configuration.

The workflow builds pull requests without deploying. Pushes to `master` or
`main` (and manual runs on those branches) publish `_site/` to `gh-pages`.
For the initial setup, select **Settings → Pages → Deploy from a branch**,
then choose **gh-pages / (root)** after the first workflow run creates it.
