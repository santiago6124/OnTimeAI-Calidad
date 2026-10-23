#!/usr/bin/env bash
# Genera informe/INFORME.pdf desde informe/INFORME.md.
#
# pandoc convierte el Markdown a HTML con el CSS de al lado; Chrome en modo
# headless lo imprime a PDF. Se eligió esto y no LaTeX porque no hay TeX
# instalado y el informe lleva tablas anchas que se ven mejor con CSS.
set -euo pipefail
cd "$(dirname "$0")"
pandoc INFORME.md --from gfm --to html5 --standalone --css informe.css \
  --metadata title="OnTimeAI: TP Integrador de Calidad de Software" \
  --metadata lang=es -o INFORME.html
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
command -v google-chrome >/dev/null 2>&1 && CHROME=google-chrome
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$PWD/INFORME.pdf" "file://$PWD/INFORME.html" 2>/dev/null
echo "INFORME.pdf: $(du -h INFORME.pdf | cut -f1)"
