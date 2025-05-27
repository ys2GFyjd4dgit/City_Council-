#!/usr/bin/env python3
import re
import json

def parse_members():
    members = []
    
    with open('source_utf8.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 議員情報を抽出するパターン
    pattern = r"<a href='g07_giinlistS\.asp\?SrchID=\d+'>([^<]+)</a>　\(([^)]+)\)<br />　<span class='giinname'>議席番号：　</span>(\d+)<br />　<span class='giinname'>所属会派：　</span>([^<]+)<br />"
    
    matches = re.findall(pattern, content)
    
    for match in matches:
        name = match[0].strip()
        reading = match[1].strip()
        seat_num = match[2]
        faction = match[3].strip()
        
        # 会派名の整理（代表などの表記を削除）
        faction = re.sub(r'[\s　]+\(代表\)', '', faction)
        faction = re.sub(r'[\s　]+', '', faction)
        
        member = {
            "氏名": name,
            "登録名": name,
            "よみ": reading,
            "X（旧Twitter）": None,
            "所属": faction
        }
        members.append(member)
    
    # 議席番号順にソート
    members.sort(key=lambda x: int(re.search(r'\d+', x['氏名']).group() if re.search(r'\d+', x['氏名']) else '0'))
    
    return members

if __name__ == "__main__":
    members = parse_members()
    
    # JSONファイルに保存
    with open('議員リスト_132098_町田市.json', 'w', encoding='utf-8') as f:
        json.dump(members, f, ensure_ascii=False, indent=2)
    
    print(f"町田市議員数: {len(members)}名")
    for member in members:
        print(f"{member['氏名']} ({member['よみ']}) - {member['所属']}")