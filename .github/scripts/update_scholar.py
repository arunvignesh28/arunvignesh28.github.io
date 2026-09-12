#!/usr/bin/env python3
"""
Scholar metrics updater.

Primary source: the public Google Scholar profile — the numbers the site actually
claims to show. Fallback: Semantic Scholar, derived from the per-paper list rather
than the author-level aggregate (that aggregate lags its own paper data).

The fallback is advisory only: because S2 has thinner coverage than Google Scholar,
a fallback run may never lower a value that came from Google Scholar. Without that
rule the two sources flap against each other week to week.
"""
import os
import re
import json
import sys
import time
import html as html_lib
import requests
from datetime import datetime, timezone

GOOGLE_SCHOLAR_ID = os.getenv('GOOGLE_SCHOLAR_ID', 'jIFv3pIAAAAJ')
S2_AUTHOR_ID = os.getenv('S2_AUTHOR_ID', '2326969007')
AUTHOR_NAME_QUERY = os.getenv('SCHOLAR_NAME', 'Arun Vignesh Malarkkan')

GS_BASE = 'https://scholar.google.com/citations'
S2_BASE = 'https://api.semanticscholar.org/graph/v1'

BROWSER_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
S2_HEADERS = {'User-Agent': 'scholar-updater/2.0 (academic-website; contact: github-actions)'}
API_KEY = os.getenv('SEMANTIC_SCHOLAR_API_KEY', '')
if API_KEY:
    S2_HEADERS['x-api-key'] = API_KEY

SOURCE_GOOGLE = 'google_scholar'
SOURCE_S2 = 'semantic_scholar'

# A run that would cut citations by more than this fraction is treated as a bad
# read rather than a real drop, and nothing is written.
MAX_CITATION_DROP = 0.20


def http_get(url: str, params: dict = None, headers: dict = None, retries: int = 5):
    """GET with exponential-backoff retry for 429/5xx and any transport error."""
    delay = 5
    last_error = None
    for attempt in range(retries):
        wait = delay * (2 ** attempt)
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=45)
            if resp.status_code == 200:
                return resp
            if resp.status_code == 429 or resp.status_code >= 500:
                last_error = f'HTTP {resp.status_code}'
                print(f'  {last_error} — retrying in {wait}s (attempt {attempt + 1}/{retries})')
                time.sleep(wait)
                continue
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            last_error = type(e).__name__
            print(f'  {last_error} — retrying in {wait}s (attempt {attempt + 1}/{retries})')
            time.sleep(wait)
    raise RuntimeError(f'Failed after {retries} attempts ({last_error}): {url}')


# ---------------------------------------------------------------- Google Scholar

def strip_tags(fragment: str) -> str:
    text = html_lib.unescape(re.sub(r'<[^>]+>', '', fragment))
    # Scholar pads truncated venue names with a non-breaking space before the ellipsis.
    return text.replace(' ', ' ').strip()


def parse_metrics_table(page: str) -> dict:
    """Pull Citations / h-index / i10-index out of the profile's summary table.

    Parsed by row label rather than by position, so a layout change surfaces as a
    missing key instead of a silently wrong number.
    """
    table = re.search(r'id="gsc_rsb_st".*?</table>', page, re.S)
    if not table:
        return {}

    metrics = {}
    for row in re.findall(r'<tr>(.*?)</tr>', table.group(0), re.S):
        label = re.search(r'class="gsc_rsb_sc1"[^>]*>(.*?)</td>', row, re.S)
        values = re.findall(r'class="gsc_rsb_std"[^>]*>(\d+)</td>', row)
        if not label or not values:
            continue
        # First value column is "All"; the second is "Since <year>".
        metrics[strip_tags(label.group(1)).lower()] = int(values[0])
    return metrics


def parse_publications(page: str) -> list:
    """Parse one page of the publication table."""
    pubs = []
    for row in re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', page, re.S):
        title = re.search(r'class="gsc_a_at"[^>]*>(.*?)</a>', row, re.S)
        grays = re.findall(r'<div class="gs_gray">(.*?)</div>', row, re.S)
        cites = re.search(r'class="gsc_a_ac[^"]*"[^>]*>(\d*)<', row)
        year = re.search(r'class="gsc_a_h[^"]*"[^>]*>(\d*)<', row)

        # The venue div carries the year in a trailing <span class="gs_oph">.
        venue = ''
        if len(grays) > 1:
            venue = strip_tags(re.sub(r'<span class="gs_oph">.*?</span>', '', grays[1], flags=re.S))

        pubs.append({
            'title': strip_tags(title.group(1)) if title else '',
            'year': int(year.group(1)) if year and year.group(1) else '',
            'authors': strip_tags(grays[0]) if grays else '',
            'venue': venue,
            'citations': int(cites.group(1)) if cites and cites.group(1) else 0,
        })
    return pubs


def scrape_google_scholar(scholar_id: str) -> dict:
    """Read metrics and the publication list off the public profile page."""
    page_size = 100
    headers = {
        'User-Agent': BROWSER_UA,
        'Accept-Language': 'en-US,en;q=0.9',
    }

    resp = http_get(GS_BASE, {'user': scholar_id, 'hl': 'en', 'cstart': 0,
                              'pagesize': page_size}, headers)
    resp.encoding = 'utf-8'
    page = resp.text

    if 'gs_captcha' in page or 'unusual traffic' in page.lower():
        raise RuntimeError('Google Scholar returned a CAPTCHA challenge')

    metrics = parse_metrics_table(page)
    if 'citations' not in metrics:
        raise RuntimeError('Could not find the metrics table on the profile page')

    publications = parse_publications(page)
    cstart = len(publications)
    while publications and len(publications) % page_size == 0:
        resp = http_get(GS_BASE, {'user': scholar_id, 'hl': 'en', 'cstart': cstart,
                                  'pagesize': page_size}, headers)
        resp.encoding = 'utf-8'
        more = parse_publications(resp.text)
        if not more:
            break
        publications.extend(more)
        cstart += len(more)

    return {
        'source': SOURCE_GOOGLE,
        'total_citations': metrics.get('citations', 0),
        'h_index': metrics.get('h-index', 0),
        'i10_index': metrics.get('i10-index', 0),
        'publications_count': len(publications),
        'publications': publications,
    }


# ------------------------------------------------------------- Semantic Scholar

def s2_get(url: str, params: dict = None) -> dict:
    return http_get(url, params, S2_HEADERS).json()


def find_s2_author_by_name(name_query: str, google_scholar_id: str) -> str:
    """Search by name when no S2 author ID is configured."""
    data = s2_get(f'{S2_BASE}/author/search', {
        'query': name_query,
        'fields': 'authorId,name,externalIds',
        'limit': 10,
    })
    results = data.get('data', [])
    for author in results:
        ext = author.get('externalIds') or {}
        if ext.get('GoogleScholar') == google_scholar_id:
            return author['authorId']
    if results:
        return results[0]['authorId']
    raise RuntimeError(f'No Semantic Scholar author found for query: {name_query}')


def calc_h_index(citation_counts: list) -> int:
    h = 0
    for i, c in enumerate(sorted(citation_counts, reverse=True), start=1):
        if c >= i:
            h = i
    return h


def fetch_semantic_scholar() -> dict:
    """Fallback metrics, derived from the paper list.

    S2's author-level citationCount/hIndex lag the per-paper data it serves from
    the same API, so everything here is computed from the papers themselves.
    """
    author_id = S2_AUTHOR_ID or find_s2_author_by_name(AUTHOR_NAME_QUERY, GOOGLE_SCHOLAR_ID)
    papers = s2_get(f'{S2_BASE}/author/{author_id}/papers', {
        'fields': 'title,year,authors,venue,citationCount,externalIds,openAccessPdf',
        'limit': 1000,
    }).get('data', [])

    counts = [(p.get('citationCount') or 0) for p in papers]
    return {
        'source': SOURCE_S2,
        'total_citations': sum(counts),
        'h_index': calc_h_index(counts),
        'i10_index': sum(1 for c in counts if c >= 10),
        'publications_count': len(papers),
        'publications': [
            {
                'title': p.get('title', ''),
                'year': p.get('year') or '',
                'authors': ', '.join(a.get('name', '') for a in (p.get('authors') or [])),
                'venue': p.get('venue', ''),
                'citations': p.get('citationCount') or 0,
                'pdf_url': (p.get('openAccessPdf') or {}).get('url', ''),
                'doi': (p.get('externalIds') or {}).get('DOI', ''),
            }
            for p in papers
        ],
    }


# ------------------------------------------------------------------- persistence

METRIC_KEYS = ('total_citations', 'h_index', 'i10_index', 'publications_count')


def load_existing(path: str) -> dict:
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    # newline pinned so a local run on Windows and a CI run on Linux write the
    # same bytes, instead of churning the diff with line-ending flips.
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f'  wrote {path}')


def sanity_check(new: dict, prev: dict) -> None:
    """Refuse to publish a result that looks like a broken read rather than news."""
    prev_citations = prev.get('total_citations', 0)
    if not prev_citations:
        return
    if new['total_citations'] < prev_citations * (1 - MAX_CITATION_DROP):
        raise RuntimeError(
            f"Refusing to write: citations fell from {prev_citations} to "
            f"{new['total_citations']} (more than {int(MAX_CITATION_DROP * 100)}%) — "
            f"treating this as a bad read from {new['source']}")
    if new['h_index'] < prev.get('h_index', 0) - 1:
        raise RuntimeError(
            f"Refusing to write: h-index fell from {prev.get('h_index')} to "
            f"{new['h_index']} — treating this as a bad read from {new['source']}")
    if not new['publications_count'] and prev.get('publications_count'):
        raise RuntimeError(
            f"Refusing to write: no publications parsed, but {prev['publications_count']} "
            f"were stored — treating this as a bad read from {new['source']}")


def apply_fallback_floor(new: dict, prev: dict) -> dict:
    """Never let a thinner source lower numbers that came from a richer one.

    Only applies when the incoming source differs from the stored one. Same-source
    runs write whatever the source says, so real corrections still land.
    """
    prev_source = prev.get('source')
    if not prev_source or prev_source == new['source']:
        return new
    if new['source'] == SOURCE_GOOGLE:
        return new  # Google Scholar is authoritative; let it correct the fallback.

    floored = dict(new)
    for key in METRIC_KEYS:
        floored[key] = max(new[key], prev.get(key, 0))
    if any(floored[k] != new[k] for k in METRIC_KEYS):
        print(f'  {new["source"]} is thinner than stored {prev_source} data — '
              f'holding previous values where they were higher')
    return floored


def main() -> int:
    print(f'Starting Scholar update — Google Scholar ID: {GOOGLE_SCHOLAR_ID}')
    prev = load_existing('scholar_data.json')

    try:
        print('Reading Google Scholar profile...')
        result = scrape_google_scholar(GOOGLE_SCHOLAR_ID)
    except Exception as e:
        print(f'Google Scholar unavailable ({e}); falling back to Semantic Scholar')
        result = fetch_semantic_scholar()

    print(f'Source: {result["source"]}  Citations: {result["total_citations"]}  '
          f'H-index: {result["h_index"]}  i10-index: {result["i10_index"]}  '
          f'Publications: {result["publications_count"]}')

    sanity_check(result, prev)
    result = apply_fallback_floor(result, prev)

    # Judged on the metrics alone: a fallback run that only re-states the stored
    # numbers should not rewrite the file just to relabel its source.
    if all(prev.get(k) == result[k] for k in METRIC_KEYS):
        print('No change since last run — leaving files untouched.')
        return 0

    for key in METRIC_KEYS:
        if prev.get(key) != result[key]:
            print(f'  {key}: {prev.get(key, "—")} -> {result[key]}')

    now = datetime.now(timezone.utc).isoformat()
    metrics = {
        'total_citations': result['total_citations'],
        'h_index': result['h_index'],
        'i10_index': result['i10_index'],
        'publications_count': result['publications_count'],
        'last_updated': now,
        'source': result['source'],
        'scholar_url': f'https://scholar.google.com/citations?user={GOOGLE_SCHOLAR_ID}',
    }

    write_json('scholar_data.json', metrics)
    write_json('_data/scholar.json', {
        'metrics': metrics,
        'publications': result['publications'],
        'last_updated': now,
    })
    write_json('_data/stats.json', {**{k: metrics[k] for k in METRIC_KEYS},
                                    'last_updated': now, 'source': result['source']})

    print('All data files updated successfully.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f'Fatal error: {e}')
        sys.exit(1)
