# Data

`raw/` holds files downloaded from NCBI GEO at runtime. They are gitignored.

The notebook always fetches these official HTTPS URLs:

- https://ftp.ncbi.nlm.nih.gov/geo/series/GSE171nnn/GSE171405/matrix/GSE171405_series_matrix.txt.gz
- https://ftp.ncbi.nlm.nih.gov/geo/series/GSE171nnn/GSE171405/soft/GSE171405_family.soft.gz
- https://ftp.ncbi.nlm.nih.gov/geo/series/GSE171nnn/GSE171405/suppl/GSE171405_non-normalized.txt.gz

See the project README for what each file contains.
