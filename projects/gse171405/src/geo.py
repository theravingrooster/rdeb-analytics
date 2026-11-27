"""Download and parse GSE171405 files from NCBI GEO (HTTPS FTP)."""

from __future__ import annotations

import gzip
import urllib.request
from io import StringIO
from pathlib import Path

import pandas as pd

# Official, stable HTTPS URLs on NCBI's GEO FTP. These work with wget/curl/pandas.
# There is no NCBI-generated RNA-seq count matrix for this series: it is a
# microarray experiment (Illumina HumanHT-12 v4), not RNA-seq.
GEO_URLS = {
    "series_matrix": (
        "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE171nnn/GSE171405/matrix/"
        "GSE171405_series_matrix.txt.gz"
    ),
    "family_soft": (
        "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE171nnn/GSE171405/soft/"
        "GSE171405_family.soft.gz"
    ),
    "nonnormalized": (
        "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE171nnn/GSE171405/suppl/"
        "GSE171405_non-normalized.txt.gz"
    ),
    "raw_idat_tar": (
        "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE171nnn/GSE171405/suppl/"
        "GSE171405_RAW.tar"
    ),
    "filelist": (
        "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE171nnn/GSE171405/suppl/"
        "filelist.txt"
    ),
}

GEO_PAGE = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE171405"


def download_file(url: str, dest: Path, timeout: int = 120) -> Path:
    """Download url to dest, skipping the transfer if the file already exists."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    # A simple User-Agent keeps some NCBI endpoints happier.
    request = urllib.request.Request(url, headers={"User-Agent": "rdeb-gse171405/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response, dest.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
    return dest


def assign_group(tissue: str) -> str:
    """Map GEO tissue labels to the paper's group names: EBw, EBn, HC."""
    tissue = (tissue or "").strip().lower()
    if tissue == "wounded skin":
        return "EBw"
    if tissue == "normal skin":
        return "EBn"
    if tissue == "control skin":
        return "HC"
    return "unknown"


def _strip_quotes(value: str) -> str:
    return value.strip().strip('"')


def parse_series_matrix_metadata(path: Path) -> tuple[pd.DataFrame, dict]:
    """Parse the header of a GEO series matrix into a sample table + series info."""
    series_info: dict[str, str] = {}
    sample_columns: dict[str, list[str]] = {}
    characteristic_rows: list[list[str]] = []
    description_rows: list[list[str]] = []

    open_fn = gzip.open if str(path).endswith(".gz") else open
    with open_fn(path, "rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("!series_matrix_table_begin"):
                break
            if not line.startswith("!"):
                continue
            parts = line.rstrip("\n").split("\t")
            key = parts[0]
            values = [_strip_quotes(v) for v in parts[1:]]
            if key.startswith("!Series_") and values:
                # Keep the first value; contributors can repeat the key.
                series_info.setdefault(key.replace("!Series_", ""), values[0])
                if key == "!Series_contributor":
                    series_info.setdefault("contributors", [])
                    if isinstance(series_info["contributors"], list):
                        series_info["contributors"].append(values[0])
            elif key.startswith("!Sample_characteristics"):
                characteristic_rows.append(values)
            elif key == "!Sample_description":
                description_rows.append(values)
            elif key.startswith("!Sample_") and values:
                sample_columns[key.replace("!Sample_", "")] = values

    accessions = sample_columns.get("geo_accession", [])
    samples = pd.DataFrame({"sample_id": accessions})
    samples["title"] = sample_columns.get("title", [""] * len(samples))
    samples["source_name"] = sample_columns.get("source_name_ch1", [""] * len(samples))
    samples["platform_id"] = sample_columns.get("platform_id", [""] * len(samples))

    for row in characteristic_rows:
        parsed = []
        field_name = "characteristic"
        for item in row:
            if ":" in item:
                name, value = item.split(":", 1)
                field_name = name.strip()
                parsed.append(value.strip())
            else:
                parsed.append(item)
        samples[field_name] = parsed

    if len(description_rows) >= 1:
        samples["array_label"] = [v.strip() for v in description_rows[0]]
    if len(description_rows) >= 2:
        samples["sample_label"] = [v.strip() for v in description_rows[1]]

    if "tissue" in samples.columns:
        samples["group"] = samples["tissue"].map(assign_group)
    else:
        samples["group"] = "unknown"

    if "donor" in samples.columns:
        samples["donor"] = samples["donor"].astype(str).str.strip()

    preferred = [
        "sample_id",
        "sample_label",
        "group",
        "donor",
        "diagnosis",
        "tissue",
        "title",
        "source_name",
        "array_label",
        "platform_id",
    ]
    ordered = [c for c in preferred if c in samples.columns] + [
        c for c in samples.columns if c not in preferred
    ]
    return samples[ordered], series_info


def load_series_matrix_expression(path: Path) -> pd.DataFrame:
    """Load the VALUE table from a GEO series matrix (probes x samples)."""
    lines: list[str] = []
    open_fn = gzip.open if str(path).endswith(".gz") else open
    with open_fn(path, "rt", encoding="utf-8", errors="replace") as handle:
        in_table = False
        for line in handle:
            if line.startswith("!series_matrix_table_begin"):
                in_table = True
                continue
            if line.startswith("!series_matrix_table_end"):
                break
            if in_table:
                lines.append(line)
    expr = pd.read_csv(StringIO("".join(lines)), sep="\t", index_col=0)
    expr.index = expr.index.astype(str)
    expr.columns = [str(c).strip().strip('"') for c in expr.columns]
    expr = expr.apply(pd.to_numeric, errors="coerce")
    return expr


def load_platform_annotation_from_soft(path: Path) -> pd.DataFrame:
    """Read the platform table (Array_Address_Id, gene symbol) from a family SOFT file."""
    lines: list[str] = []
    open_fn = gzip.open if str(path).endswith(".gz") else open
    with open_fn(path, "rt", encoding="utf-8", errors="replace") as handle:
        in_table = False
        for line in handle:
            if line.startswith("!platform_table_begin"):
                in_table = True
                continue
            if line.startswith("!platform_table_end"):
                break
            if in_table:
                lines.append(line)
    annot = pd.read_csv(StringIO("".join(lines)), sep="\t")
    # Official GPL28270 columns are ID (Array_Address_Id) and ORF (gene symbol).
    rename = {}
    if "ID" in annot.columns:
        rename["ID"] = "array_address_id"
    if "ORF" in annot.columns:
        rename["ORF"] = "gene_symbol"
    annot = annot.rename(columns=rename)
    if "array_address_id" in annot.columns:
        annot["array_address_id"] = annot["array_address_id"].astype(str)
    return annot


def load_nonnormalized(path: Path) -> pd.DataFrame:
    """Load submitter-provided non-normalized Illumina intensities (probes x arrays)."""
    # Read probe IDs as strings. The file includes control probes with IDs like
    # "1820564.1"; if pandas infers a float column, official IDs become "5270161.0"
    # and no longer match the series matrix.
    table = pd.read_csv(
        path,
        sep="\t",
        dtype={0: str},
        compression="gzip" if str(path).endswith(".gz") else None,
    )
    first = table.columns[0]
    table = table.rename(columns={first: "array_address_id"})
    table["array_address_id"] = table["array_address_id"].astype(str)
    table = table.set_index("array_address_id")
    table.columns = [str(c).strip() for c in table.columns]
    return table.apply(pd.to_numeric, errors="coerce")
