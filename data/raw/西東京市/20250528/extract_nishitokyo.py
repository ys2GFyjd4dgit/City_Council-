#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time

def extract_council_members():
    """Extract Nishitokyo city council member information."""
    
    # Read the main HTML file
    with open('source.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all council member links
    member_links = soup.find_all('a', href=re.compile(r'/sigikai/giin_meibo/meibo/[^/]+\.html'))
    
    members = []
    base_url = "https://www.city.nishitokyo.lg.jp"
    
    for link in member_links:
        member_url = base_url + link['href']
        member_name_text = link.text.strip()
        
        # Extract name and reading
        match = re.match(r'(.+?)（(.+?)）議員', member_name_text)
        if match:
            name = match.group(1).strip()
            reading = match.group(2).strip()
            
            # Try to fetch the member's page to get party affiliation
            try:
                print(f"Fetching info for {name}...")
                response = requests.get(member_url, timeout=10)
                response.encoding = 'utf-8'
                member_soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for party affiliation
                party = ""
                
                # Try to find party info in table
                tables = member_soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['th', 'td'])
                        if len(cells) >= 2:
                            header = cells[0].text.strip()
                            if '会派' in header or '所属' in header:
                                party = cells[1].text.strip()
                                break
                    if party:
                        break
                
                # If not found in table, look for specific patterns
                if not party:
                    content = member_soup.get_text()
                    party_match = re.search(r'(?:会派|所属)[:：]\s*([^、。\n]+)', content)
                    if party_match:
                        party = party_match.group(1).strip()
                
                members.append({
                    "氏名": name,
                    "よみがな": reading,
                    "所属会派": party
                })
                
                # Small delay to be polite
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error fetching {member_url}: {e}")
                # Add with empty party if fetch fails
                members.append({
                    "氏名": name,
                    "よみがな": reading,
                    "所属会派": ""
                })
    
    # Sort by reading
    members.sort(key=lambda x: x['よみがな'])
    
    # Save to JSON
    output_path = '/Users/yasuyoshi/my-claude-test-project/City_Council-/data/processed/議員リスト_132292_西東京市.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(members, f, ensure_ascii=False, indent=2)
    
    print(f"\nExtracted {len(members)} council members")
    print(f"Saved to: {output_path}")
    
    return members

if __name__ == "__main__":
    extract_council_members()