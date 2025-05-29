#!/usr/bin/env python3
import json
import os
from collections import defaultdict
from datetime import datetime

def extract_members_without_x():
    # Dictionary to store members by prefecture and municipality
    members_by_location = defaultdict(lambda: defaultdict(list))
    
    # Statistics
    total_members = 0
    no_x_members = 0
    
    # Base directory
    base_dir = "/Users/yasuyoshi/my-claude-test-project/City_Council-/data/processed"
    
    # Process all JSON files
    for root, dirs, files in os.walk(base_dir):
        for filename in files:
            if filename.endswith('.json') and not filename.endswith('_discovery_urls.csv'):
                filepath = os.path.join(root, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Extract prefecture and municipality info
                    if 'prefecture' in data and 'municipal' in data and 'members' in data:
                        prefecture = data['prefecture']['name']
                        municipality = data['municipal']['name']
                        
                        # Process each member
                        for member in data['members']:
                            total_members += 1
                            
                            # Check if member has X account
                            x_account = member.get('x_account', None)
                            if not x_account or x_account.strip() == '':
                                no_x_members += 1
                                
                                # Extract member info
                                name = member.get('name', '不明')
                                reading = member.get('reading', '')
                                party = member.get('party_affiliation', '無所属')
                                
                                # Format member info
                                if reading:
                                    member_info = f"{name} ({reading}) - {party}"
                                else:
                                    member_info = f"{name} - {party}"
                                
                                members_by_location[prefecture][municipality].append(member_info)
                
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    # Generate output
    output_lines = []
    
    # Header with statistics
    output_lines.append("X（旧Twitter）アカウント未登録議員一覧")
    output_lines.append("=" * 60)
    output_lines.append(f"生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    output_lines.append(f"総議員数: {total_members:,}名")
    output_lines.append(f"X未登録議員数: {no_x_members:,}名")
    output_lines.append(f"未登録率: {(no_x_members/total_members*100):.1f}%")
    output_lines.append("=" * 60)
    output_lines.append("")
    
    # List members by prefecture and municipality
    for prefecture in sorted(members_by_location.keys()):
        output_lines.append(f"【{prefecture}】")
        output_lines.append("-" * 40)
        
        for municipality in sorted(members_by_location[prefecture].keys()):
            members = members_by_location[prefecture][municipality]
            output_lines.append(f"\n■ {municipality} ({len(members)}名)")
            
            for member in sorted(members):
                output_lines.append(f"  ・{member}")
        
        output_lines.append("")
    
    # Write to file
    output_path = "/Users/yasuyoshi/my-claude-test-project/City_Council-/manual_search/x未登録議員一覧.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"File created: {output_path}")
    print(f"Total members without X accounts: {no_x_members}/{total_members}")

if __name__ == "__main__":
    extract_members_without_x()