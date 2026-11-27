# RDEB wound transcriptome proof of concept (GSE171405)

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/theravingrooster/rdeb-analytics/blob/main/projects/gse171405/notebooks/01_download_and_load.ipynb)

A small, reproducible project using **public** gene-expression data from people with recessive dystrophic epidermolysis bullosa (RDEB). The aim is to practice a clean analysis — differential expression, pathway enrichment, and a simple drug-repurposing / signature-reversal step — and share it on GitHub.

Portfolio page: <https://theravingrooster.github.io/rdeb-analytics/projects/gse171405.html>

**Status:** notebook 01 (download, load, and QC) is complete. Differential expression, pathway enrichment, and signature reversal are planned and have not been run.

This repo uses **public GEO data only**. It does not use, and should never be given, real identifiable patient data.

## Project goal

Start from GEO series [GSE171405](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE171405): skin from the edge of chronic RDEB wounds (EBw), matched intact RDEB skin from the same donors (EBn), and matched healthy control skin (HC). Reproduce a compact, well-documented analysis that:

1. Loads the official expression matrix and a clean sample table.
2. Finds differentially expressed genes between the groups.
3. Looks at pathways that matter in this disease (inflammation, fibrosis, JAK-STAT, extracellular matrix, cytokine signaling).
4. Tries a simple reverse-transcriptomics / candidate-drug ranking step against LINCS/CMap-style signatures.

The work is meant to be a 1–2 week proof of concept, written in Python, and runnable in **Google Colab**.

## Important: this is a microarray, not RNA-seq

GSE171405 is **Illumina HumanHT-12 v4.0 Expression BeadChip** data (`Expression profiling by array`, platform [GPL28270](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL28270)). NCBI's RNA-seq count pipeline does **not** apply here, and these files do **not** exist for this series:

- `GSE171405_raw_counts_GRCh38.p13_NCBI.tsv.gz`
- `GSE171405_FPKM_...` / `GSE171405_TPM_...`
- the matching `Human.GRCh38.p13.annot.tsv.gz` counts annotation

The official processed values are **quantile-normalized intensities** (in practice, on a log-like scale), not integer counts. Later differential-expression work should use a microarray-appropriate method (for example a limma-style linear model on these intensities), not DESeq2 / pyDESeq2, which expect RNA-seq counts.

## Data source and citation

Please cite both the paper and the GEO accession if you use these data.

Onoufriadis A, Proudfoot LE, Ainali C, Torre D, Papanikolaou M, Rayinda T, Rashidghamat E, Danarti R, Mellerio JE, Ma'ayan A, McGrath JA. Transcriptomic profiling of recessive dystrophic epidermolysis bullosa wounded skin highlights drug repurposing opportunities to improve wound healing. *Experimental Dermatology*. 2022;31(3):420–426. doi:[10.1111/exd.14481](https://doi.org/10.1111/exd.14481). PMID:[34694680](https://pubmed.ncbi.nlm.nih.gov/34694680/).

- GEO series: [GSE171405](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE171405) (public 30 Dec 2021)
- Platform: [GPL28270](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL28270) — Illumina HumanHT-12 v4, IDs are Array_Address_Id
- BioProject: [PRJNA719399](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA719399)

**Design (18 samples):** 6 RDEB donors (EB1–EB6), each with a wound-edge biopsy (EBw) and an intact-skin biopsy (EBn), plus 6 matched healthy controls (C1–C6, group HC).

## Direct download URLs

These HTTPS links on NCBI's public FTP can be fetched with `wget`, `curl`, or `pandas` / `urllib` in Colab. Prefer this FTP host over `www.ncbi.nlm.nih.gov/geo/download/`, which can interstitially block automated clients.

| File | What it is | URL |
| --- | --- | --- |
| Series matrix (4.4 MB) | Quantile-normalized expression (47,323 probes × 18 samples) **plus** the sample metadata used to build the group/donor table | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE171nnn/GSE171405/matrix/GSE171405_series_matrix.txt.gz |
| Family SOFT (7.5 MB) | Same series, plus the GPL28270 probe annotation (`ID` = Array_Address_Id, `ORF` = gene symbol) | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE171nnn/GSE171405/soft/GSE171405_family.soft.gz |
| Non-normalized intensities (4.8 MB) | Submitter raw-ish intensity table; useful as a microarray stand-in for “library size” QC. Includes some extra control probes | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE171nnn/GSE171405/suppl/GSE171405_non-normalized.txt.gz |
| RAW IDAT archive (29 MB) | Illumina IDAT files (not needed for notebook 01) | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE171nnn/GSE171405/suppl/GSE171405_RAW.tar |
| File list | Inventory of the RAW tar | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE171nnn/GSE171405/suppl/filelist.txt |

Example:

```bash
wget -O GSE171405_series_matrix.txt.gz \
  "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE171nnn/GSE171405/matrix/GSE171405_series_matrix.txt.gz"
```

pandas can also stream a `.gz` table (the series matrix still needs a small parser for its `!`-prefixed header; see `src/geo.py`).

## Packages needed to parse the files

For notebook 01, from `requirements.txt` or in a Colab cell:

```text
pandas numpy matplotlib seaborn
```

```python
%pip install -q pandas numpy matplotlib seaborn
```

No GEO-specific parser is required. The files are gzip-compressed text; `src/geo.py` (and the first notebook) reads them with pandas. Later notebooks may add `gseapy`, `statsmodels`, and/or `scipy`.

## How to open in Google Colab

The first notebook is written to run top-to-bottom in Colab. It installs the packages above, downloads the official files, and does not depend on a local clone.

**Option A — upload the notebook**

1. Open [Google Colab](https://colab.research.google.com/).
2. File → Upload notebook → choose `notebooks/01_download_and_load.ipynb`.
3. Runtime → Run all.

**Option B — from GitHub**

Use the **Open in Colab** badge at the top of this file. It opens:

```text
https://colab.research.google.com/github/theravingrooster/rdeb-analytics/blob/main/projects/gse171405/notebooks/01_download_and_load.ipynb
```

**Option C — clone in a Colab cell**

```python
!git clone https://github.com/theravingrooster/rdeb-analytics.git
%cd rdeb-analytics/projects/gse171405
```

No GPU is needed. Files downloaded in Colab are written under `/content/`.

To run the same notebook on your own machine:

```bash
cd projects/gse171405
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# plus jupyter / ipykernel if you want the notebook UI
jupyter nbconvert --to notebook --execute notebooks/01_download_and_load.ipynb --inplace
```

## Planned steps

| Step | Notebook | What we will do |
| --- | --- | --- |
| 1. Download and load | `notebooks/01_download_and_load.ipynb` | Fetch the official GEO files, build the sample table (group, donor), and run sanity checks |
| 2. Differential expression | planned | Compare EBw vs EBn, EBw vs HC, and EBn vs HC with a microarray-appropriate model |
| 3. Pathway enrichment | planned | Inflammation, fibrosis, JAK-STAT, ECM, and cytokine signaling (e.g. gseapy) |
| 4. Signature reversal | planned | Rank candidate compounds whose signatures oppose the RDEB-wound expression pattern (LINCS/CMap-style) |
| 5. Figures and writeup | planned | Publication-style figures, tables, and a short plain-language interpretation |

## Repository layout

```text
projects/gse171405/
  README.md
  requirements.txt
  notebooks/01_download_and_load.ipynb
  src/geo.py              # download + parse helpers for later notebooks
  figures/                # plots written by the notebooks
  results/                # clean tables written by the notebooks
  data/raw/               # downloaded GEO files (gitignored)
```
