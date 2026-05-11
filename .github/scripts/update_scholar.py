#!/usr/bin/env python3
"""
Scholar metrics updater using the Semantic Scholar API.
No scraping, no bot detection — free official API with retry logic.
"""
import os
import json
import sys
import time
import requests
from datetime import datetime

GOOGLE_SCHOLAR_ID = os.getenv('GOOGLE_SCHOLAR_ID', 'jIFv3pIAAAAJ')
# Semantic Scholar author ID — faster and unambiguous vs name search
S2_AUTHOR_ID = os.getenv('S2_AUTHOR_ID', '2326969007')
AUTHOR_NAME_QUERY = os.getenv('SCHOLAR_NAME', 'Arun Vignesh Malarkkan')

S2_BASE = 'https://api.semanticscholar.org/graph/v1'
HEADERS = {'User-Agent': 'scholar-updater/1.0 (academic-website; contact: github-actions)'}
API_KEY = os.getenv('SEMANTIC_SCHOLAR_API_KEY', '')
if API_KEY:
    HEADERS['x-api-key'] = API_KEY


def s2_get(url: str, params: dict = None, retries: int = 5) -> dict:
    """GET with exponential-backoff retry for 429/5xx."""
    delay = 5
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=45)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 429 or resp.status_code >= 500:
                wait = delay * (2 ** attempt)
                print(f"HTTP {resp.status_code} — retrying in {wait}s (attempt {attempt+1}/{retries})")
                time.sleep(wait)
                continue
            resp.raise_for_status()
        except requests.exceptions.Timeout:
            wait = delay * (2 ** attempt)
            print(f"Timeout — retrying in {wait}s (attempt {attempt+1}/{retries})")
            time.sleep(wait)
    raise RuntimeError(f"Failed after {retries} attempts: {url}")


def get_author_by_id(s2_author_id: str) -> dict:
    """Fetch author metrics directly by Semantic Scholar author ID."""
    url = f'{S2_BASE}/author/{s2_author_id}'
    params = {'fields': 'authorId,name,affiliations,citationCount,hIndex,paperCount,externalIds'}
    return s2_get(url, params)


def find_author_by_name(name_query: str, google_scholar_id: str) -> dict:
    """Search by name when no S2 author ID is configured."""
    url = f'{S2_BASE}/author/search'
    params = {
        'query': name_query,
        'fields': 'authorId,name,affiliations,citationCount,hIndex,paperCount,externalIds',
        'limit': 10,
    }
    data = s2_get(url, params)
    results = data.get('data', [])

    for author in results:
        ext = author.get('externalIds') or {}
        if ext.get('GoogleScholar') == google_scholar_id:
            return author

    if results:
        return results[0]
    raise RuntimeError(f"No author found for query: {name_query}")


def get_papers(s2_author_id: str) -> list:
    """Fetch all papers for the author."""
    url = f'{S2_BASE}/author/{s2_author_id}/papers'
    params = {
        'fields': 'title,year,authors,venue,citationCount,externalIds,openAccessPdf',
        'limit': 1000,
    }
    return s2_get(url, params).get('data', [])


def calc_i10_index(papers: list) -> int:
    return sum(1 for p in papers if (p.get('citationCount') or 0) >= 10)


def write_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  wrote {path}")


def main() -> bool:
    print(f"Starting Scholar update — Google Scholar ID: {GOOGLE_SCHOLAR_ID}")

    # Prefer direct S2 author ID lookup over name search
    if S2_AUTHOR_ID:
        print(f"Fetching author directly by S2 author ID: {S2_AUTHOR_ID}")
        author = get_author_by_id(S2_AUTHOR_ID)
    else:
        print(f"Searching for author by name: {AUTHOR_NAME_QUERY}")
        author = find_author_by_name(AUTHOR_NAME_QUERY, GOOGLE_SCHOLAR_ID)

    s2_id = author['authorId']
    print(f"Author: {author.get('name')} (S2 ID: {s2_id})")

    papers = get_papers(s2_id)
    print(f"Papers fetched: {len(papers)}")

    total_citations = author.get('citationCount') or 0
    h_index = author.get('hIndex') or 0
    paper_count = author.get('paperCount') or len(papers)
    i10_index = calc_i10_index(papers)

    print(f"Citations: {total_citations}  H-index: {h_index}  "
          f"i10-index: {i10_index}  Papers: {paper_count}")

    now = datetime.utcnow().isoformat()

    metrics = {
        'total_citations': total_citations,
        'h_index': h_index,
        'i10_index': i10_index,
        'publications_count': paper_count,
        'last_updated': now,
        'scholar_url': f'https://scholar.google.com/citations?user={GOOGLE_SCHOLAR_ID}',
    }

    pub_list = [
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
    ]

    write_json('scholar_data.json', metrics)
    write_json('_data/scholar.json', {'metrics': metrics, 'publications': pub_list, 'last_updated': now})
    write_json('_data/stats.json', {
        'total_citations': total_citations,
        'h_index': h_index,
        'i10_index': i10_index,
        'publications_count': paper_count,
        'last_updated': now,
    })

    print("All data files updated successfully.")
    return True


if __name__ == '__main__':
    try:
        sys.exit(0 if main() else 1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
