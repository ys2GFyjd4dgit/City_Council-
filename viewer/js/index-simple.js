// シンプルな静的データ表示版
function displayMunicipalities() {
    const container = document.getElementById('municipality-list');
    
    // データを配列に変換
    const municipalities = Object.entries(municipalityData).map(([code, data]) => ({
        code,
        ...data
    }));
    
    // 都道府県別にグループ化
    const grouped = {
        '東京都': municipalities.filter(m => m.prefecture === '13_東京都'),
        '埼玉県': municipalities.filter(m => m.prefecture === '11_埼玉県')
    };
    
    // HTML生成
    let html = '';
    
    for (const [prefName, munis] of Object.entries(grouped)) {
        if (munis.length > 0) {
            html += `<h3 style="grid-column: 1 / -1; margin-top: 20px;">${prefName}</h3>`;
            
            // 自治体名でソート
            munis.sort((a, b) => a.name.localeCompare(b.name, 'ja'));
            
            html += munis.map(m => {
                const percentage = m.count > 0 ? Math.round(m.xCount / m.count * 100) : 0;
                return `
                    <a href="municipality.html?code=${m.code}&name=${encodeURIComponent(m.name)}&prefecture=${encodeURIComponent(m.prefecture)}" class="municipality-card">
                        <h4>${m.name}</h4>
                        <div class="councillor-count">議員数: ${m.count}名</div>
                        <div class="x-count">X登録: ${m.xCount}名 (${percentage}%)</div>
                    </a>
                `;
            }).join('');
        }
    }
    
    container.innerHTML = html;
}

// ページ読み込み時に実行
document.addEventListener('DOMContentLoaded', displayMunicipalities);