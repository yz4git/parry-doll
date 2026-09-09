#!/usr/bin/env bash
set -euo pipefail

grep -q "Hair v3.1" visual-src/hair.js

pushd visual-src >/dev/null
npm ci
npm run build
popd >/dev/null

node --check dist/visual-engine.js
git diff --check

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add visual-src/hair.js dist/visual-engine.js dist/visual-engine.js.LEGAL.txt
if git diff --cached --quiet; then
  echo "Hair v3 build already current"
  exit 0
fi
git commit -m "fix: close Hair v3 crown coverage"
git push origin main
