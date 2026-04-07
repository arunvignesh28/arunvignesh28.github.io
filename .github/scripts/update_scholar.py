#!/usr/bin/env python3
"""
Scholar metrics updater using the Semantic Scholar API.
No scraping, no bot detection — free official API.
"""
import os
import json
import sys
import requests
from datetime import datetime

SCHOLAR_ID = os.getenv('GOOGLE_SCHOLAR_ID', 'jIFv3pIAAAAJ')
AUTHOR_NAME_QUERY = os.getenv('SCHOLAR_NAME', 'Arun Vignesh Malarkkan')
S2_BASE = 'https://api.semanticscholar.org/graph/v1'
HEADERS = {
    'User-Agent': 'scholar-updater/1.0 (academic-website auto-update; contact: github-actions)',
}
# Optional: set SEMANTIC_SCHOLAR_API_KEY env var for higher rate limits
API_KEY = os.getenv('SEMANTIC_SCHOLAR_API_KEY', '')
if API_KEY:
    HEADERS['x-api-key'] = API_KEY


def find_author(google_scholar_id: str, name_query: str) -> dict | None:
    """
    Search Semantic Scholar for an author matching the given Google Scholar ID.
    Falls back to the first name match if the ID is not found in externalIds.
    """
    url = f'{S2_BASE}/author/search'
    params = {
        'query': name_query,
        'fields': 'authorId,name,affiliations,citationCount,hIndex,paperCount,externalIds',
        'limit': 10,
    }
    resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    results = resp.json().get('data', [])

    # Prefer exact Google Scholar ID match
    for author in results:
        ext = author.get('externalIds') or {}
        if ext.get('GoogleScholar') == google_scholar_id:
            print(f"Matched author by Google Scholar ID: {author['name']}")
            return author

    # Fallback: first result
    if results:
        print(f"No exact Scholar ID match; using first result: {results[0]['name']}")
        return results[0]

    return None


def get_papers(s2_author_id: str) -> list[dict]:
    """Fetch all papers for the given Semantic Scholar author ID."""
    url = f'{S2_BASE}/author/{s2_author_id}/papers'
    params = {
        'fields': 'title,year,authors,venue,citationCount,externalIds,openAccessPdf',
        'limit': 1000,
    }
    resp = requests.get(url, params=params, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    return resp.json().get('data', [])


def calc_i10_index(papers: list[dict]) -> int:
    return sum(1 for p in papers if (p.get('citationCount') or 0) >= 10)


def write_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Updated {path}")


def main() -> bool:
    print(f"Starting Scholar update for ID: {SCHOLAR_ID}")

    author = find_author(SCHOLAR_ID, AUTHOR_NAME_QUERY)
    if not author:
        print("Error: Could not find author on Semantic Scholar.")
        return False

    s2_id = author['authorId']
    print(f"Semantic Scholar author ID: {s2_id}")

    papers = get_papers(s2_id)
    print(f"Fetched {len(papers)} papers")

    total_citations = author.get('citationCount') or 0
    h_index = author.get('hIndex') or 0
    paper_count = author.get('paperCount') or len(papers)
    i10_index = calc_i10_index(papers)

    print(f"Citations: {total_citations} | H-index: {h_index} | "
          f"i10-index: {i10_index} | Papers: {paper_count}")

    now = datetime.utcnow().isoformat()

    # Root-level file fetched by the live JS widget
    metrics = {
        'total_citations': total_citations,
        'h_index': h_index,
        'i10_index': i10_index,
        'publications_count': paper_count,
        'last_updated': now,
        'scholar_url': f'https://scholar.google.com/citations?user={SCHOLAR_ID}',
    }
    write_json('scholar_data.json', metrics)

    # Full publication list for future use
    pub_list = []
    for p in papers:
        pub_list.append({
            'title': p.get('title', ''),
            'year': p.get('year') or '',
            'authors': ', '.join(
                a.get('name', '') for a in (p.get('authors') or [])
            ),
            'venue': p.get('venue', ''),
            'citations': p.get('citationCount') or 0,
            'pdf_url': (p.get('openAccessPdf') or {}).get('url', ''),
            'doi': (p.get('externalIds') or {}).get('DOI', ''),
        })

    write_json('_data/scholar.json', {
        'metrics': metrics,
        'publications': pub_list,
        'last_updated': now,
    })
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
    sys.exit(0 if main() else 1)
