"""Download one public $0 itch.io upload by its exact visible upload label.

This follows itch.io's normal "No thanks, just take me to the downloads" flow. It does not bypass
payment or authentication. Unlike download-itch-free-asset.py, the visible itch upload label is allowed
to differ from the resulting archive filename; the newly created local file is detected atomically.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
  let row = label.closest('.upload, .upload_row, .file, li, tr') || label.parentElement;
  for (let depth = 0; depth < 7 && row; depth++, row = row.parentElement) {
    const controls = Array.from(row.querySelectorAll('a,button'));
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
      return {ok:true, label:expected, score:pick.score, href:pick.href, text:pick.text,
              uploadId:pick.uploadId, rowHtml:(row.outerHTML || '').slice(0,2200), url:location.href};
    }
  }
}
return {ok:false, reason:'no-download-control-near-exact-label', url:location.href};
"""


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--purchase-url', required=True)
    p.add_argument('--expected-label', required=True)
    p.add_argument('--download-dir', required=True)
    p.add_argument('--timeout', type=int, default=180)
    return p.parse_args()


def main():
    a = parse_args()
    out = Path(a.download_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    before = {p.resolve() for p in out.iterdir() if p.is_file()}

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
    wait = WebDriverWait(driver, 35)
    try:
        driver.get(a.purchase_url)
        no_thanks = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[self::a or self::button][contains(normalize-space(.), 'No thanks, just take me to the downloads')]"
        )))
        driver.execute_script('arguments[0].click();', no_thanks)
        wait.until(lambda d: d.execute_script(
            "const expected=arguments[0].trim();"
            "function ownText(el){return Array.from(el.childNodes).filter(n=>n.nodeType===3).map(n=>n.textContent).join(' ').trim();}"
            "return Array.from(document.querySelectorAll('body *')).some(el=>ownText(el)===expected);",
            a.expected_label,
        ))
        time.sleep(1.0)
        clicked = driver.execute_script(CLICK_EXACT_UPLOAD_JS, a.expected_label)
        print('ITCH_FREE_UPLOAD_CLICK', clicked)
        if not clicked or not clicked.get('ok'):
            raise RuntimeError(f'could not click exact itch upload row: {clicked!r}')

        deadline = time.time() + a.timeout
        last = None
        last_size = -1
        stable = 0
        while time.time() < deadline:
            partials = list(out.glob('*.crdownload')) + list(out.glob('*.tmp'))
            created = [p for p in out.iterdir() if p.is_file() and p.resolve() not in before and p.suffix != '.crdownload']
            if len(created) == 1 and not partials:
                found = created[0]
                size = found.stat().st_size
                if last == found and size == last_size and size > 0:
                    stable += 1
                else:
                    stable = 0
                last, last_size = found, size
                if stable >= 2:
                    print('ITCH_FREE_UPLOAD_DOWNLOAD', {'file': str(found), 'bytes': size, 'page': driver.current_url})
                    print(str(found))
                    return
            elif len(created) > 1 and not partials:
                raise RuntimeError(f'ambiguous itch download files: {[p.name for p in created]!r}')
            time.sleep(1)
        raise RuntimeError(f'timed out downloading label={a.expected_label!r}; files={[p.name for p in out.iterdir()]!r}')
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
