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


def xpath_literal(text: str) -> str:
    if "'" not in text:
        return f"'{text}'"
    if '"' not in text:
        return f'"{text}"'
    parts = text.split("'")
    return "concat(" + ", \"'\", ".join(f"'{p}'" for p in parts) + ")"


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

        literal = xpath_literal(a.expected_file)
        exact_nodes = wait.until(lambda d: d.find_elements(
            By.XPATH,
            f"//*[normalize-space(text())={literal}]"
        ))
        if not exact_nodes:
            raise RuntimeError(f'itch.io did not expose exact filename {a.expected_file!r}')

        candidates = []
        for file_text in exact_nodes:
            # Current itch layouts wrap each file in an upload row/card. Search outward until a row
            # containing a link/button is found, then prefer actual download/file hrefs.
            for ancestor_xpath in (
                "./ancestor::*[contains(concat(' ', normalize-space(@class), ' '), ' upload ')][1]",
                "./ancestor::*[self::div or self::li or self::tr][.//a or .//button][1]",
            ):
                try:
                    row = file_text.find_element(By.XPATH, ancestor_xpath)
                except Exception:
                    continue
                links = row.find_elements(By.XPATH, ".//*[self::a or self::button]")
                ranked = []
                for el in links:
                    href = (el.get_attribute('href') or '').lower()
                    text = (el.text or el.get_attribute('aria-label') or el.get_attribute('title') or '').lower()
                    score = 0
                    if 'download' in href or '/file/' in href: score += 5
                    if 'download' in text: score += 4
                    if el.tag_name.lower() == 'a' and href: score += 1
                    ranked.append((score, el, href, text))
                ranked.sort(key=lambda item: item[0], reverse=True)
                candidates.extend([item[1] for item in ranked if item[0] > 0])
                if candidates:
                    break
            if candidates:
                break

        if not candidates:
            # Diagnostic fallback: exact file labels sometimes live inside a sibling of the button.
            file_text = exact_nodes[0]
            nearby = file_text.find_elements(
                By.XPATH,
                "./following::*[self::a or self::button][@href or @data-upload_id or contains(normalize-space(.), 'Download')][position() <= 8]"
            )
            candidates.extend(nearby)

        if not candidates:
            snippets = []
            for node in exact_nodes[:3]:
                try:
                    snippets.append(node.find_element(By.XPATH, './ancestor::*[self::div or self::li or self::tr][1]').get_attribute('outerHTML')[:1500])
                except Exception:
                    pass
            raise RuntimeError(
                f'itch.io exposed {a.expected_file!r}, but no matching download control was found; '
                f'nearby_html={snippets!r}'
            )

        driver.execute_script('arguments[0].scrollIntoView({block:"center"});', candidates[0])
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
                    print('ITCH_FREE_DOWNLOAD', {'file': str(found), 'bytes': size, 'page': driver.current_url})
                    return
            time.sleep(1)
        raise RuntimeError(f'timed out downloading {a.expected_file!r}; files={sorted(p.name for p in out.iterdir())}')
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
