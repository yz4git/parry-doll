"""Download a public BlendSwap asset using the page's current signed download URL.

Used only in GitHub Actions for the CC0 hair donor.  The signed URL is intentionally resolved at build
time rather than checked into the repository because BlendSwap rotates it.
"""
from __future__ import annotations

import argparse
import html
import http.cookiejar
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--page", required=True)
    p.add_argument("--output", required=True)
    return p.parse_args()


def main():
    a = parse_args()
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    opener.addheaders = [
        ("User-Agent", "Mozilla/5.0 ParryDollHairAuthoring/18.1"),
        ("Accept-Language", "en-US,en;q=0.8"),
    ]

    with opener.open(a.page, timeout=60) as response:
        page = response.read().decode("utf-8", errors="replace")
    matches = re.findall(r'href=["\']([^"\']*/download/[^"\']+)["\']', page, re.I)
    if not matches:
        # Rails may HTML-escape an absolute signed URL.
        matches = re.findall(r'(https?://[^"\'<>\s]+/download/[^"\'<>\s]+)', page, re.I)
    if not matches:
        raise RuntimeError("BlendSwap page did not expose a current download URL")

    url = urllib.parse.urljoin(a.page, html.unescape(matches[0]))
    req = urllib.request.Request(url, headers={"Referer": a.page})
    with opener.open(req, timeout=120) as response:
        data = response.read()
        ctype = response.headers.get("Content-Type", "")
        disposition = response.headers.get("Content-Disposition", "")
        final_url = response.geturl()

    # A Blender file begins with BLENDER.  BlendSwap may instead return a zip containing the blend.
    if not (data.startswith(b"BLENDER") or data.startswith(b"PK\x03\x04")):
        preview = data[:200].decode("utf-8", errors="replace")
        raise RuntimeError(
            f"unexpected BlendSwap download payload type={ctype!r} final={final_url!r} "
            f"disposition={disposition!r} preview={preview!r}"
        )
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print("BLENDSWAP_DOWNLOAD", {
        "bytes": len(data),
        "content_type": ctype,
        "content_disposition": disposition,
        "final_url": final_url,
        "zip": data.startswith(b"PK\x03\x04"),
    })


if __name__ == "__main__":
    main()
