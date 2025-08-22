#!/usr/bin/env python3
"""
Google Scholar Citation Update Script
This script fetches citation data from Google Scholar and updates the website data files.
"""

import os
import json
import yaml
import requests
from datetime import datetime
import time
import re

try:
    from scholarly import scholarly, ProxyGenerator
except ImportError:
    print("Installing required packages...")
    os.system("pip install scholarly")
    from scholarly import scholarly, ProxyGenerator

class ScholarUpdater:
    def __init__(self, scholar_id):
        self.scholar_id = scholar_id
        self.setup_proxy()
        
    def setup_proxy(self):
        """Setup proxy to avoid rate limiting"""
        try:
            pg = ProxyGenerator()
            pg.FreeProxies()
            scholarly.use_proxy(pg)
        except Exception as e:
            print(f"Warning: Could not setup proxy: {e}")
            print("Continuing without proxy...")

    def get_author_data(self):
        """Fetch author data from Google Scholar"""
        try:
            print(f"Fetching data for Scholar ID: {self.scholar_id}")
            
            # Search for author by ID
            author = scholarly.search_author_id(self.scholar_id)
            author_filled = scholarly.fill(author)
            
            return author_filled
        except Exception as e:
            print(f"Error fetching author data: {e}")
            return None

    def extract_metrics(self, author_data):
        """Extract citation metrics from author data"""
        if not author_data:
            return {}
            
        try:
            citations = author_data.get('citedby', 0)
            h_index = author_data.get('hindex', 0)
            i10_index = author_data.get('i10index', 0)
            
            # Extract yearly citation data
            yearly_citations = []
            if 'cites_per_year' in author_data:
                for year, count in author_data['cites_per_year'].items():
                    yearly_citations.append({'year': int(year), 'count': count})
            
            return {
                'total_citations': citations,
                'h_index': h_index,
                'i10_index': i10_index,
                'yearly_citations': sorted(yearly_citations, key=lambda x: x['year']),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error extracting metrics: {e}")
            return {}

    def get_publications(self, author_data):
        """Extract publication data"""
        if not author_data:
            return []
            
        publications = []
        try:
            for pub in author_data.get('publications', []):
                # Fill publication details
                try:
                    pub_filled = scholarly.fill(pub)
                    
                    # Extract publication info
                    pub_data = {
                        'title': pub_filled.get('bib', {}).get('title', 'Unknown Title'),
                        'authors': pub_filled.get('bib', {}).get('author', 'Unknown Authors'),
                        'venue': pub_filled.get('bib', {}).get('venue', 'Unknown Venue'),
                        'year': pub_filled.get('bib', {}).get('pub_year', 'Unknown'),
                        'citations': pub_filled.get('num_citations', 0),
                        'scholar_url': pub_filled.get('pub_url', ''),
                        'eprint_url': pub_filled.get('eprint_url', ''),
                        'abstract': pub_filled.get('bib', {}).get('abstract', '')[:500] + '...' if pub_filled.get('bib', {}).get('abstract', '') else ''
                    }
                    
                    publications.append(pub_data)
                    
                    # Add delay to avoid rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error processing publication: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error getting publications: {e}")
            
        return publications

    def update_data_files(self, metrics, publications):
        """Update the website data files"""
        try:
            # Update scholar data JSON
            scholar_data = {
                'metrics': metrics,
                'publications': publications,
                'last_updated': datetime.now().isoformat()
            }
            
            # Create _data directory if it doesn't exist
            os.makedirs('_data', exist_ok=True)
            
            # Write scholar data
            with open('_data/scholar.json', 'w') as f:
                json.dump(scholar_data, f, indent=2)
            
            print("Updated _data/scholar.json")
            
            # Update publications.yml if it exists
            if os.path.exists('_data/publications.yml'):
                self.update_publications_yml(publications)
            
            return True
            
        except Exception as e:
            print(f"Error updating data files: {e}")
            return False

    def update_publications_yml(self, scholar_publications):
        """Update citations in existing publications.yml"""
        try:
            with open('_data/publications.yml', 'r') as f:
                existing_pubs = yaml.safe_load(f) or []
            
            # Update citation counts for matching publications
            for existing_pub in existing_pubs:
                title = existing_pub.get('title', '').lower()
                
                # Find matching publication from scholar data
                for scholar_pub in scholar_publications:
                    scholar_title = scholar_pub.get('title', '').lower()
                    
                    # Simple title matching (you might want to improve this)
                    if self.titles_match(title, scholar_title):
                        existing_pub['citations'] = scholar_pub.get('citations', 0)
                        existing_pub['scholar_url'] = scholar_pub.get('scholar_url', '')
                        break
            
            # Write updated data back
            with open('_data/publications.yml', 'w') as f:
                yaml.dump(existing_pubs, f, default_flow_style=False, allow_unicode=True)
            
            print("Updated _data/publications.yml")
            
        except Exception as e:
            print(f"Error updating publications.yml: {e}")

    def titles_match(self, title1, title2):
        """Simple title matching function"""
        # Remove common words and punctuation for better matching
        def clean_title(title):
            # Remove punctuation and convert to lowercase
            clean = re.sub(r'[^\w\s]', '', title.lower())
            # Remove common words
            common_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            words = [word for word in clean.split() if word not in common_words]
            return ' '.join(words)
        
        clean1 = clean_title(title1)
        clean2 = clean_title(title2)
        
        # Check if titles are similar (at least 80% of words match)
        words1 = set(clean1.split())
        words2 = set(clean2.split())
        
        if not words1 or not words2:
            return False
            
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        similarity = intersection / union if union > 0 else 0
        return similarity > 0.8

    def generate_summary_stats(self, metrics):
        """Generate summary statistics for the website"""
        try:
            stats = {
                'total_citations': metrics.get('total_citations', 0),
                'h_index': metrics.get('h_index', 0),
                'i10_index': metrics.get('i10_index', 0),
                'publications_count': len(metrics.get('publications', [])),
                'last_updated': metrics.get('last_updated', '')
            }
            
            with open('_data/stats.json', 'w') as f:
                json.dump(stats, f, indent=2)
            
            print("Generated _data/stats.json")
            
        except Exception as e:
            print(f"Error generating summary stats: {e}")

def main():
    """Main function"""
    scholar_id = os.getenv('GOOGLE_SCHOLAR_ID')
    
    if not scholar_id:
        # Use hardcoded Scholar ID as fallback
        scholar_id = 'jIFv3pIAAAAJ'  # Arun's actual Scholar ID
        print(f"Warning: GOOGLE_SCHOLAR_ID environment variable not set")
        print(f"Using hardcoded Scholar ID: {scholar_id}")
    
    if not scholar_id:
        print("Error: No Google Scholar ID available")
        return False
    
    print(f"Starting Scholar update for ID: {scholar_id}")
    
    updater = ScholarUpdater(scholar_id)
    
    # Fetch author data
    author_data = updater.get_author_data()
    if not author_data:
        print("Failed to fetch author data")
        return False
    
    print(f"Successfully fetched data for: {author_data.get('name', 'Unknown')}")
    
    # Extract metrics and publications
    metrics = updater.extract_metrics(author_data)
    publications = updater.get_publications(author_data)
    
    print(f"Extracted {len(publications)} publications")
    print(f"Total citations: {metrics.get('total_citations', 0)}")
    print(f"H-index: {metrics.get('h_index', 0)}")
    
    # Update data files
    if updater.update_data_files(metrics, publications):
        updater.generate_summary_stats(metrics)
        print("Successfully updated all data files")
        return True
    else:
        print("Failed to update data files")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)