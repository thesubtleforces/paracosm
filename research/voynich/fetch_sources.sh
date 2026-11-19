#!/usr/bin/env bash
# Fetch the third-party material the analyses read, at the exact versions used for the committed results.
# Everything lands under ./sources (git-ignored). The transliterations themselves are already in
# data/transliterations/ and need no network.
#
#   ./fetch_sources.sh            # controls + word boxes + page metadata (about 400 MB)
#   ./fetch_sources.sh --images   # also the 236 page photographs in two sizes (about 135 MB more)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)/sources"
WANT_IMAGES="${1:-}"
mkdir -p "$ROOT"

fetch() {   # owner repo commit [sparse paths...]
  local owner=$1 repo=$2 sha=$3; shift 3
  local dest="$ROOT/$owner/$repo"
  if [ "$(git -C "$dest" rev-parse HEAD 2>/dev/null || true)" = "$sha" ]; then
    # already at the pinned commit: re-apply the path list, so that a later --images run adds the photographs
    if [ $# -gt 0 ]; then GIT_LFS_SKIP_SMUDGE=1 git -C "$dest" sparse-checkout set --no-cone "$@"; fi
    echo "ok   $owner/$repo"; return
  fi
  rm -rf "$dest"; mkdir -p "$dest"
  git -C "$dest" init -q
  git -C "$dest" remote add origin "https://github.com/$owner/$repo"
  if [ $# -gt 0 ]; then
    git -C "$dest" config extensions.partialClone origin
    git -C "$dest" config remote.origin.promisor true
    git -C "$dest" config remote.origin.partialclonefilter blob:none
    git -C "$dest" sparse-checkout set --no-cone "$@"
    GIT_LFS_SKIP_SMUDGE=1 git -C "$dest" fetch -q --depth 1 --filter=blob:none origin "$sha"
  else
    GIT_LFS_SKIP_SMUDGE=1 git -C "$dest" fetch -q --depth 1 origin "$sha"
  fi
  GIT_LFS_SKIP_SMUDGE=1 git -C "$dest" checkout -q FETCH_HEAD
  echo "got  $owner/$repo @ ${sha:0:10}"
}

# controls: natural-language texts, Naibbe ciphertext, self-citation output
fetch lrozanova voynich-units 956a7c4fc39981f4d116fa3f4edfccce6d065571
fetch TorstenTimm SelfCitationTextgenerator a6ede2202dd7ad6285ce2c007bf22c2a0e7709b7
fetch danielgaskell voynich d076a7d081f35098fa405928239595afd2e75927
fetch chirila Voynich-public decc4caaa6515b86e42a219d1da8d81114736f2e \
      '/Corpora/Historical_texts/' '/Corpora/Voynich_texts/' '/Corpora/*.csv' '/R code/Voynich_texts/' '/R code/Gibberish_texts/' '/README.md'
fetch mzattera v4j f3387f112402c3f724d1264aae24c69336c7daca \
      '/eclipse/io.github.mzattera.v4j/src/main/resources/Transcriptions/' '/resources/' '/README.md' '/LICENSE'
# upstream mirror of the transliterations (the copies in data/transliterations/ came from here)
fetch noah-chelednik voynich-data ecd4c8145524d90373535ea3d1617d8190dc8208

# validation round: verse, calendars, lists and recipes with native units (Tesserae), and 21 Latin
# manuscripts of the 11th-15th centuries transcribed line by line (CREMMA Medieval LAT; text files only)
fetch tesserae tesserae 5e0ae3043c0a5b0be6ab194df58518e48ee87547 \
      '/texts/la/vergil.georgics.tess' '/texts/la/vergil.aeneid.tess' '/texts/la/lucretius.de_rerum_natura.tess' \
      '/texts/la/ovid.fasti.tess' '/texts/la/walafrid_strabo.de_cultu_hortorum_carmen.tess' \
      '/texts/la/wandalbertus.martyrologium.tess' '/texts/la/cato_the_elder.de_agricultura.tess' \
      '/texts/la/jerome.vulgate/jerome.vulgate.part.4.numbers.tess' \
      '/texts/la/jerome.vulgate/jerome.vulgate.part.12.1_chronicles.tess' \
      '/texts/la/jerome.vulgate/jerome.vulgate.part.21.psalms.tess' '/README*' '/LICENSE*'
fetch HTR-United CREMMA-Medieval-LAT 292525969ad98380b398e6606a9c2a36d51913ae '/README.md' '/data-registry.csv' '/htr-united.yml' '/data/**/*.txt'

# Gaskell & Bowern's human gibberish and comparison texts ship as zip files
mkdir -p "$ROOT/_controls/gaskell_gibberish" "$ROOT/_controls/gaskell_meaningful"
unzip -q -o "$ROOT/danielgaskell/voynich/data/gibberish_transcriptions.zip" -d "$ROOT/_controls/gaskell_gibberish"
unzip -q -o "$ROOT/danielgaskell/voynich/data/meaningful.zip" -d "$ROOT/_controls/gaskell_meaningful"

# word boxes, collation and scribe table; page photographs only on request
if [ "$WANT_IMAGES" = "--images" ]; then
  fetch writtenbyalina voynichviewer c4117bb3f243716d151905423b7c3377c32aad7a '/README.md' '/data/'
else
  fetch writtenbyalina voynichviewer c4117bb3f243716d151905423b7c3377c32aad7a '/README.md' '/data/*.json' '/data/text/'
fi

(cd "$(dirname "$0")/data/transliterations" && sha256sum -c SHA256SUMS)
echo "sources ready under $ROOT"
