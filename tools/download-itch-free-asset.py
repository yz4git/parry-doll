"""Download a public $0 / Donate itch.io asset through its normal 'No thanks' flow.

This is browser automation for a public, no-login free download. It does not bypass a paywall or use
private endpoints. The caller supplies the exact expected filename so we never click unrelated uploads.
"""
from __future__ import annotations

import argparse
import os
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
    matches = [p for p in root.iterdir() if p.is_file() and expected.lower() in p.name.lower()]
    return max(matches, key=lambda p: p.stat().st_mtime) if matches else None


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
            "//*[contains(normalize-space(.), 'No thanks, just take me to the downloads')]"
        )))
        driver.execute_script('arguments[0].click();', no_thanks)

        # itch.io reveals the upload rows after the public free-download choice. Locate the row that
        # explicitly names the requested file, then click a Download control within/adjacent to it.
        file_text = wait.until(EC.presence_of_element_located((
            By.XPATH,
            f"//*[contains(normalize-space(.), {a.expected_file!r})]"
        )))
        candidates = []
        for xpath in (
            ".//ancestor::*[self::div or self::li][.//*[contains(normalize-space(.), 'Download')]][1]//*[self::a or self::button][contains(normalize-space(.), 'Download')]",
            "./following::*[self::a or self::button][contains(normalize-space(.), 'Download')][1]",
            "./ancestor::*[self::div or self::li][1]//*[self::a or self::button][1]",
        ):
            try:
                candidates.extend(file_text.find_elements(By.XPATH, xpath))
            except Exception:
                pass
        if not candidates:
            # Fallback: choose the first Download button whose nearest row contains the expected name.
            for el in driver.find_elements(By.XPATH, "//*[self::a or self::button][contains(normalize-space(.), 'Download')]"):
                try:
                    text = el.find_element(By.XPATH, './ancestor::*[self::div or self::li][1]').text
                except Exception:
                    text = ''
                if a.expected_file.lower() in text.lower():
                    candidates.append(el)
                    break
        if not candidates:
            raise RuntimeError(f'itch.io exposed {a.expected_file!r}, but no matching Download control was found')
        driver.execute_script('arguments[0].click();', candidates[0])

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
                    print('ITCH_FREE_DOWNLOAD', {'file': str(found), 'bytes': size})
                    return
            time.sleep(1)
        raise RuntimeError(f'timed out downloading {a.expected_file!r}; files={sorted(p.name for p in out.iterdir())}')
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
