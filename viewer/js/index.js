// Municipality data - 東京都
const tokyoMunicipalities = [
    { code: '132012', name: '八王子市', prefecture: '13_東京都' },
    { code: '132021', name: '立川市', prefecture: '13_東京都' },
    { code: '132039', name: '武蔵野市', prefecture: '13_東京都' },
    { code: '132047', name: '三鷹市', prefecture: '13_東京都' },
    { code: '132055', name: '青梅市', prefecture: '13_東京都' },
    { code: '132063', name: '府中市', prefecture: '13_東京都' },
    { code: '132071', name: '昭島市', prefecture: '13_東京都' },
    { code: '132080', name: '調布市', prefecture: '13_東京都' },
    { code: '132098', name: '町田市', prefecture: '13_東京都' },
    { code: '132101', name: '小金井市', prefecture: '13_東京都' },
    { code: '132110', name: '小平市', prefecture: '13_東京都' },
    { code: '132128', name: '日野市', prefecture: '13_東京都' },
    { code: '132136', name: '東村山市', prefecture: '13_東京都' },
    { code: '132144', name: '国分寺市', prefecture: '13_東京都' },
    { code: '132152', name: '国立市', prefecture: '13_東京都' },
    { code: '132187', name: '福生市', prefecture: '13_東京都' },
    { code: '132195', name: '狛江市', prefecture: '13_東京都' },
    { code: '132209', name: '東大和市', prefecture: '13_東京都' },
    { code: '132217', name: '清瀬市', prefecture: '13_東京都' },
    { code: '132225', name: '東久留米市', prefecture: '13_東京都' },
    { code: '132233', name: '武蔵村山市', prefecture: '13_東京都' },
    { code: '132241', name: '多摩市', prefecture: '13_東京都' },
    { code: '132250', name: '稲城市', prefecture: '13_東京都' },
    { code: '132276', name: '羽村市', prefecture: '13_東京都' },
    { code: '132284', name: 'あきる野市', prefecture: '13_東京都' },
    { code: '132292', name: '西東京市', prefecture: '13_東京都' }
];

// 東京都町村
const tokyoTowns = [
    { code: '133035', name: '瑞穂町', prefecture: '13_東京都' },
    { code: '133051', name: '日の出町', prefecture: '13_東京都' },
    { code: '133078', name: '檜原村', prefecture: '13_東京都' },
    { code: '133086', name: '奥多摩町', prefecture: '13_東京都' },
    { code: '133612', name: '大島町', prefecture: '13_東京都' },
    { code: '133621', name: '利島村', prefecture: '13_東京都' },
    { code: '133639', name: '新島村', prefecture: '13_東京都' },
    { code: '133647', name: '神津島村', prefecture: '13_東京都' },
    { code: '133817', name: '三宅村', prefecture: '13_東京都' },
    { code: '133825', name: '御蔵島村', prefecture: '13_東京都' },
    { code: '134015', name: '八丈町', prefecture: '13_東京都' },
    { code: '134023', name: '青ヶ島村', prefecture: '13_東京都' },
    { code: '134210', name: '小笠原村', prefecture: '13_東京都' }
];

// 埼玉県
const saitamaMunicipalities = [
    { code: '112089', name: '所沢市', prefecture: '11_埼玉県' },
    { code: '112259', name: '入間市', prefecture: '11_埼玉県' }
];

// Load municipality data and create cards
async function loadMunicipalities() {
    const container = document.getElementById('municipality-list');
    container.innerHTML = '<div class="loading">データを読み込み中...</div>';
    
    const allMunicipalities = [
        ...tokyoMunicipalities,
        ...tokyoTowns,
        ...saitamaMunicipalities
    ];
    
    const cards = [];
    
    for (const municipality of allMunicipalities) {
        try {
            // Load JSON data for each municipality
            const response = await fetch(`../data/processed/${municipality.prefecture}/議員リスト_${municipality.code}_${municipality.name}.json`);
            if (response.ok) {
                const data = await response.json();
                const councillorCount = data.length; // JSONは配列形式
                const xAccountCount = data.filter(member => member['X（旧Twitter）'] && member['X（旧Twitter）'] !== null).length;
                
                cards.push({
                    ...municipality,
                    count: councillorCount,
                    xCount: xAccountCount
                });
            }
        } catch (error) {
            console.error(`Error loading data for ${municipality.name}:`, error);
        }
    }
    
    // Group by prefecture
    const grouped = {
        '東京都': cards.filter(m => m.prefecture === '13_東京都'),
        '埼玉県': cards.filter(m => m.prefecture === '11_埼玉県')
    };
    
    // Create HTML for cards
    let html = '';
    for (const [prefName, municipalities] of Object.entries(grouped)) {
        if (municipalities.length > 0) {
            html += `<h3 style="grid-column: 1 / -1; margin-top: 20px;">${prefName}</h3>`;
            html += municipalities.map(municipality => `
                <a href="municipality.html?code=${municipality.code}&name=${encodeURIComponent(municipality.name)}&prefecture=${encodeURIComponent(municipality.prefecture)}" class="municipality-card">
                    <h4>${municipality.name}</h4>
                    <div class="councillor-count">議員数: ${municipality.count}名</div>
                    <div class="x-count">X登録: ${municipality.xCount}名 (${municipality.count > 0 ? Math.round(municipality.xCount / municipality.count * 100) : 0}%)</div>
                </a>
            `).join('');
        }
    }
    
    container.innerHTML = html || '<p>データが見つかりません</p>';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', loadMunicipalities);