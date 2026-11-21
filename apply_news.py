#!/usr/bin/env python3
"""Safely insert the 2026 Baqing news entry into the existing index.html News list.

Usage: python apply_news.py [path/to/index.html]
Run from the same directory as NEWS_entry.html, or keep both files together.
Does not touch other news or site assets. Makes an .html.bak backup on change.
"""
from pathlib import Path
import re
import sys
import shutil

HERE = Path(__file__).resolve().parent
INDEX = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE / 'index.html'
SNIPPET = HERE / 'NEWS_entry.html'
MARKER = 'id="baqing-2026-news"'
ANCHOR = '10/2023 Co-organizing'


def main():
    if not INDEX.is_file():
        raise SystemExit(f"ERROR: index.html not found: {INDEX}\nCopy apply_news.py and NEWS_entry.html to your website repository root, then rerun.")
    html = INDEX.read_text(encoding='utf-8')
    if MARKER in html or '<!-- BEGIN: BAQING-2026 NEWS' in html:
        print('Already present. No change made.')
        return
    anchor_at = html.find(ANCHOR)
    if anchor_at < 0:
        raise SystemExit('ERROR: News anchor not found ("10/2023 Co-organizing"). The source file may have changed. No changes made; insert NEWS_entry.html manually inside the News list.')
    # Locate the actual opening <li> of the old news item. Refuse to patch if uncertain.
    prefix = html[:anchor_at]
    opening = list(re.finditer(r'<li\b[^>]*>', prefix, flags=re.I))
    if not opening:
        raise SystemExit('ERROR: News content does not seem to use <li> items. No changes made; use NEWS_entry.html manually with a matching wrapper.')
    li_start = opening[-1].start()
    if prefix.rfind('</li>') > li_start:
        raise SystemExit('ERROR: Could not safely locate an enclosing news <li>. No changes made.')
    # Confirm this item is in a list, rather than an unrelated portion of the page.
    list_open = max(prefix.rfind('<ul'), prefix.rfind('<ol'))
    list_close = max(prefix.rfind('</ul>'), prefix.rfind('</ol>'))
    if list_open < 0 or list_close > list_open:
        raise SystemExit('ERROR: News anchor is not within a visible HTML list. No changes made.')
    snippet = SNIPPET.read_text(encoding='utf-8').strip()
    updated = html[:li_start] + snippet + '\n' + html[li_start:]
    backup = INDEX.with_suffix(INDEX.suffix + '.bak')
    if backup.exists():
        raise SystemExit(f'ERROR: Backup already exists: {backup}. No changes made; move the old backup first.')
    shutil.copy2(INDEX, backup)
    INDEX.write_text(updated, encoding='utf-8')
    print(f'Updated: {INDEX}')
    print(f'Original backed up: {backup}')
    print('Review the News section locally before committing.')


if __name__ == '__main__':
    main()
