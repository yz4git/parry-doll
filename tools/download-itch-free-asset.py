"""Download a public $0 / Donate itch.io asset through its normal 'No thanks' flow.

This is browser automation for a public, no-login free download. It does not bypass a paywall or use
private endpoints. The caller supplies the exact expected filename so we never click unrelated uploads.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--purchase-url', required=True)
    p.add_argument('--expected-file', required=True)
    p.add_argument('--download-dir', required=True)
    p.add_argument('--timeout', type=int, default=120)
    return p.parse_args()


def newest_matching(root: Path, expected: str):
    exact = root / expected
    if exact.exists() and exact.is_file():
        return exact
    stem = Path(expected).stem.lower()
    suffix = Path(expected).suffix.lower()
    matches = [
        p for p in root.iterdir()
        if p.is_file() and stem in p.stem.lower() and (not suffix or p.suffix.lower() == suffix)
    ]
    return max(matches, key=lambda p: p.stat().st_mtime) if matches else None


CLICK_EXACT_UPLOAD_JS = r"""
const expected = arguments[0].trim();
function ownText(el) {
  return Array.from(el.childNodes)
    .filter(n => n.nodeType === Node.TEXT_NODE)
    .map(n => n.textContent)
    .join(' ')
    .trim();
}
const exact = Array.from(document.querySelectorAll('body *')).filter(el => ownText(el) === expected);
if (!exact.length) return {ok:false, reason:'exact-label-not-found', url:location.href};
for (const label of exact) {
  let row = label.closest('.upload, .upload_row, .file, li, tr');
  if (!row) row = label.parentElement;
  for (let depth = 0; depth < 6 && row; depth++, row = row.parentElement) {
    const controls = Array.from(row.querySelectorAll('a,button'));
    if (!controls.length) continue;
    const ranked = controls.map(el => {
      const href = (el.getAttribute('href') || '').toLowerCase();
      const text = ((el.innerText || '') + ' ' + (el.getAttribute('aria-label') || '') + ' ' + (el.getAttribute('title') || '')).toLowerCase();
      const uploadId = el.getAttribute('data-upload_id') || el.getAttribute('data-upload-id') || '';
      let score = 0;
      if (href.includes('/file/') || href.includes('download')) score += 8;
      if (text.includes('download')) score += 6;
      if (uploadId) score += 5;
      if (el.tagName === 'A' && href) score += 1;
      return {el, score, href, text, uploadId};
    }).sort((a,b) => b.score - a.score);
    if (ranked.length && ranked[0].score > 0) {
      const pick = ranked[0];
      pick.el.scrollIntoView({block:'center'});
      pick.el.click();
      return {
        ok:true,
        label:expected,
        score:pick.score,
        href:pick.href,
        text:pick.text,
        uploadId:pick.uploadId,
        rowClass:row.className || '',
        rowHtml:(row.outerHTML || '').slice(0,1800),
        url:location.href
      };
    }
  }
}
return {
  ok:false,
  reason:'no-download-control-near-exact-label',
  url:location.href,
  labels:exact.slice(0,3).map(el => (el.parentElement?.outerHTML || el.outerHTML || '').slice(0,1500))
};
"""


def main():
    a = parse_args()
    out = Path(a.download_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1280,1000')
    options.add_experimental_option('prefs', {
        'download.default_directory': str(out),
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True,
    })

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)
    try:
        driver.get(a.purchase_url)
        no_thanks = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[self::a or self::button][contains(normalize-space(.), 'No thanks, just take me to the downloads')]"
        )))
        driver.execute_script('arguments[0].click();', no_thanks)

        # Wait until the exact filename has appeared, but do not retain a WebElement: itch.io can
        # re-render upload rows while the page settles, which makes stored Selenium elements stale.
        wait.until(lambda d: d.execute_script(
            "return Array.from(document.querySelectorAll('body *')).some(el => "
            "Array.from(el.childNodes).filter(n=>n.nodeType===3).map(n=>n.textContent).join(' ').trim() === arguments[0]);",
            a.expected_file,
        ))
        time.sleep(1.0)
        clicked = driver.execute_script(CLICK_EXACT_UPLOAD_JS, a.expected_file)
        print('ITCH_FREE_CLICK', clicked)
        if not clicked or not clicked.get('ok'):
            raise RuntimeError(f'could not click exact itch upload row: {clicked!r}')

        deadline = time.time() + a.timeout
        last_size = -1
        stable = 0
        while time.time() < deadline:
            partials = list(out.glob('*.crdownload')) + list(out.glob('*.tmp'))
            found = newest_matching(out, a.expected_file)
            if found and not partials:
                size = found.stat().st_size
                if size > 0 and size == last_size:
                    stable += 1
                else:
                    stable = 0
                last_size = size
                if stable >= 2:
                    print('ITCH_FREE_DOWNLOAD', {'file': str(found), 'bytes': size, 'page': driver.current_url})
                    return
            time.sleep(1)
        raise RuntimeError(f'timed out downloading {a.expected_file!r}; files={sorted(p.name for p in out.iterdir())}')
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
