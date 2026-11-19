#!/usr/bin/env bash
# Re-run every analysis and rebuild both pages. Needs ./fetch_sources.sh to have been run
# (with --images if the page crops and measure plates are to be remade; otherwise the committed
# ones in report/img are used). Takes about fifty minutes on four cores. Scripts are run with `python -I` because they read
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
$PY src/a08_more_controls.py
$PY src/a09_predictive_scoring.py
$PY src/a10_second_transliteration.py
$PY src/a11_corrections_and_duplicates.py
$PY src/build_dossier.py
VIEWER="${VOYNICH_SOURCES:-sources}/writtenbyalina/voynichviewer/data"
if [ -d "$VIEWER/panels" ]; then
  $PY src/make_thumbs.py "$VIEWER/panels"
  $PY src/make_story_images.py "$VIEWER/panels"
  $PY src/a12_story_tables.py "$VIEWER/panels"
  $PY src/make_measure_plates.py "$VIEWER"
else
  $PY src/a12_story_tables.py
fi
$PY src/build_story.py
