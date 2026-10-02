#!/usr/bin/env bash
# Run an OOXML document through headless LibreOffice and collect comparison evidence.
#
#   runners/libreoffice/convert.sh INPUT OUTDIR
#
# Produces in OUTDIR:
#   libreoffice-output.<ext>   round-tripped OOXML (shows what LibreOffice writes back)
#   libreoffice-render.pdf     rendered pages
#   libreoffice-render.txt     text layout of the PDF (list labels, table text, ...)
#   libreoffice.png            first page as an image (needs pdftoppm; optional)
#   VERSION                    LibreOffice version string
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: $0 INPUT OUTDIR" >&2
  exit 2
fi
input="$1"
outdir="$2"
[ -f "$input" ] || { echo "not a file: $input" >&2; exit 2; }
command -v soffice >/dev/null || { echo "soffice not found; install LibreOffice" >&2; exit 2; }

mkdir -p "$outdir"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
ext="${input##*.}"
cp "$input" "$work/original.$ext"
profile="file://$work/profile"   # isolated profile: no state shared between runs

case "$ext" in
  docx) filter="MS Word 2007 XML" ;;
  xlsx) filter="Calc MS Excel 2007 XML" ;;
  pptx) filter="Impress MS PowerPoint 2007 XML" ;;
  *) echo "unsupported extension: $ext" >&2; exit 2 ;;
esac

mkdir "$work/roundtrip"
soffice -env:UserInstallation="$profile" --headless --convert-to "$ext:$filter" \
  --outdir "$work/roundtrip" "$work/original.$ext" >/dev/null 2>&1
soffice -env:UserInstallation="$profile" --headless --convert-to pdf \
  --outdir "$work" "$work/original.$ext" >/dev/null 2>&1

cp "$work/roundtrip/original.$ext" "$outdir/libreoffice-output.$ext"
cp "$work/original.pdf" "$outdir/libreoffice-render.pdf"
soffice --version 2>/dev/null | head -n 1 | sed 's/ *$//' > "$outdir/VERSION"
if command -v pdftotext >/dev/null; then
  pdftotext -layout "$work/original.pdf" "$outdir/libreoffice-render.txt"
fi
if command -v pdftoppm >/dev/null; then
  pdftoppm -png -r 80 -f 1 -l 1 -singlefile "$work/original.pdf" "$work/page"
  cp "$work/page.png" "$outdir/libreoffice.png"
fi
echo "wrote evidence to $outdir ($(cat "$outdir/VERSION"))"
