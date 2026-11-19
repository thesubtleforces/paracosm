#!/usr/bin/env bash
# Re-run every analysis and rebuild the report page. Needs ./fetch_sources.sh to have been run.
# Takes about ten minutes on four cores. Scripts are run with `python -I` because they read
# downloaded files; nothing is executed from the downloaded directories.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python3} -I"
$PY src/a01_build_corpus.py
$PY src/a02_baselines.py
$PY src/a03_line_effects.py
$PY src/a04_local_similarity.py
$PY src/a04b_vertical_geometry.py
$PY src/a06_bifolio_order.py
$PY src/a05_sections_scribes.py
$PY src/a07_labels.py
$PY src/build_dossier.py
