#!/usr/bin/env python3
import json
from pathlib import Path

# X accounts found manually
x_accounts = {
    "佐藤　匡": "https://x.com/qopfrhnh5ukbvtb",
    "古仲　リカ": "https://x.com/konakarika",
    "吉田　賢一": "https://x.com/yoshiken2021",
    "向口　文恵": "https://x.com/d8s4HrZ02NbAFft",
    "安道　佳子": "https://x.com/a5u5ffcpteswum7",
    "末次　正": "https://x.com/suetsugutadashi",
    "永澤　美恵子": "https://x.com/qox4Au",
    "池畠　司": "https://x.com/ikehatatsukasa",
    "町田　健治": "https://x.com/85b9CtFUUo52jSx",
    "細田　智也": "https://x.com/tomoya_hosoda",
    "野口　哲次": "https://x.com/techannogu"
}

# Party affiliations from PDF
party_affiliations = {
    "佐藤　匡": "日本共産党入間市議団",
    "安道　佳子": "日本共産党入間市議団",
    "田山　雅子": "日本共産党入間市議団",
    "町田　健治": "市民の声",
    "山川　さおり": "市民の声",
    "益田　英主": "市民の声",
    "末次　正": "公明党入間市議団",
    "向口　文恵": "公明党入間市議団",
    "吉田　賢一": "自由民主党入間市議団",
    "大野　勉": "自由民主党入間市議団",
    "池畠　司": "自由民主党入間市議団",
    "双木　小百合": "自由民主党入間市議団",
    "細田　智也": "無所属の会",
    "永澤　美恵子": "公明党入間市議団",
    "栗山　英美": "公明党入間市議団",
    "長谷川　渉": "自由民主党入間市議団",
    "古仲　リカ": "自由民主党入間市議団",
    "内村　忠久": "自由民主党入間市議団",
    "野口　哲次": "市民フォーラム",
    "横田　淳一": "自由民主党入間市議団",
    "小島　清人": "自由民主党入間市議団",
    "宮岡　治郎": "自由民主党入間市議団"
}

# Corrected readings from PDF
corrected_readings = {
    "益田　英主": "ますだ　ひでかず",
    "双木　小百合": "なみき　さゆり",
    "古仲　リカ": "ふるなか　りか"
}

def main():
    # Path to Iruma JSON file
    json_path = Path(__file__).parent.parent / "data" / "processed" / "11_埼玉県" / "議員リスト_112259_入間市.json"
    
    # Read current data
    with open(json_path, 'r', encoding='utf-8') as f:
        members = json.load(f)
    
    # Update each member
    for member in members:
        name = member["氏名"]
        
        # Update X account if found
        if name in x_accounts:
            member["X（旧Twitter）"] = x_accounts[name]
        
        # Update party affiliation
        if name in party_affiliations:
            member["所属"] = party_affiliations[name]
        
        # Update reading if correction exists
        if name in corrected_readings:
            member["よみ"] = corrected_readings[name]
    
    # Sort by reading
    members.sort(key=lambda x: x["よみ"])
    
    # Write updated data
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(members, f, ensure_ascii=False, indent=2)
    
    print(f"Updated {json_path}")
    
    # Count statistics
    total = len(members)
    with_x = sum(1 for m in members if m["X（旧Twitter）"])
    print(f"Total members: {total}")
    print(f"Members with X accounts: {with_x} ({with_x/total*100:.1f}%)")
    
    # Count by party
    party_counts = {}
    for member in members:
        party = member["所属"]
        party_counts[party] = party_counts.get(party, 0) + 1
    
    print("\nMembers by party:")
    for party, count in sorted(party_counts.items()):
        print(f"  {party}: {count}")

if __name__ == "__main__":
    main()