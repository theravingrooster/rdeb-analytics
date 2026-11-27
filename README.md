# RDEB Analytics

Public, reproducible computational analyses of recessive dystrophic epidermolysis bullosa (RDEB), by Ryan Kern (Stanford).

**Website:** https://theravingrooster.github.io/rdeb-analytics/

Each analysis uses a public dataset only. The repository does not contain patient data or protected health information. Notebooks download public files from GEO when they run, and those raw files stay gitignored.

## Projects

| Project | Question | Status |
| --- | --- | --- |
| [GSE171405](projects/gse171405/) | RDEB wounds vs intact RDEB skin vs healthy skin | Data loading and QC. [Project page](https://theravingrooster.github.io/rdeb-analytics/projects/gse171405.html) |

## Repository layout

```text
README.md
docs/                          # static site (GitHub Pages, main branch, /docs)
  index.html                   # home
  about.html
  projects/gse171405.html
  projects/template.html       # copy for the next project page
  css/style.css
  assets/                      # figures shown on the site
projects/
  gse171405/                   # first analysis
    notebooks/01_download_and_load.ipynb
    src/geo.py
    figures/
    results/
    data/raw/                  # gitignored GEO downloads
```

## Adding a project

1. Create `projects/<project-id>/` with a README, code, and a `.gitignore` that excludes downloaded raw data.
2. Copy `docs/projects/template.html` to `docs/projects/<project-id>.html`. Replace the bracketed placeholders, remove the template banner and the `noindex` tag, and set the canonical URL. The HTML comment at the top of the template lists each step.
3. Copy any figure the page should show into `docs/assets/<project-id>/`. GitHub Pages serves only `docs/`, so a figure left under `projects/` is not on the website until it is copied there.
4. Add a project card in the Projects section of `docs/index.html`. A comment in that file marks the spot.
5. Add the new URL to `docs/sitemap.xml`.

Write down only dataset facts that have been checked, and only analyses the notebooks have run.

## GitHub Pages

The site is plain HTML and CSS in `docs/`. No build step and no paid host. GitHub Pages should serve the `main` branch from the `/docs` folder.

If the site is not up, that is one setting: open **Settings → Pages**, and under **Build and deployment** set **Source** to **Deploy from a branch**, branch **main**, folder **/docs**, then save.

## Local preview

From the repository root:

```bash
python3 -m http.server -d docs 8080
```

Open http://127.0.0.1:8080/ . Pages in `docs/projects/` use relative links, so preview the site from the `docs/` root rather than opening an HTML file directly.
