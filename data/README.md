# Data sources

All data used in SRLens is open-access and pre-consented. No IRB required.

## PISA 2022
- **Source:** https://www.oecd.org/en/data/datasets/pisa-2022-database.html
- **Files needed:** Student questionnaire data (motivation, self-efficacy, metacognition scales)
- **Format:** SPSS / SAS — use `pyreadstat` to load in Python
- **License:** Public / OECD terms of use

## KU Leuven clickstream
- **Source:** https://www.nature.com/articles/s41597-026-06821-3
- **Repository:** KU Leuven Research Data Repository (Dataverse)
- **Covers:** First-year bachelor students, Accountancy + Global Economics, 2018–2021
- **License:** CC BY 4.0
- **Note:** Download from the Data Availability section of the paper

## PISA 2025
- **Expected:** Late 2026
- **Key feature:** First PISA cycle with SRL process data (motivation + emotion regulation measures)
- **Source:** https://www.oecd.org/pisa
- **Status:** Analysis pipeline ready — swap in when data drops

## Processing scripts
See `/notebooks/` (coming soon) for Python scripts that process raw data into
the JSON files used by the visualizations.
