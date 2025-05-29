// Municipality data with codes
const municipalities = [
    { code: '132012', name: '八王子市' },
    { code: '132021', name: '立川市' },
    { code: '132039', name: '武蔵野市' },
    { code: '132047', name: '三鷹市' },
    { code: '132055', name: '青梅市' },
    { code: '132063', name: '府中市' },
    { code: '132071', name: '昭島市' },
    { code: '132080', name: '調布市' },
    { code: '132098', name: '町田市' },
    { code: '132101', name: '小金井市' },
    { code: '132110', name: '小平市' },
    { code: '132128', name: '日野市' },
    { code: '132136', name: '東村山市' },
    { code: '132209', name: '東大和市' },
    { code: '132217', name: '清瀬市' },
    { code: '132225', name: '東久留米市' },
    { code: '132233', name: '武蔵村山市' }
];

// Load municipality data and create cards
async function loadMunicipalities() {
    const container = document.getElementById('municipality-list');
    container.innerHTML = '<div class="loading"></div>';
    
    const cards = [];
    
    for (const municipality of municipalities) {
        try {
            // Load JSON data for each municipality
            const response = await fetch(`../data/processed/議員リスト_${municipality.code}_${municipality.name}.json`);
            if (response.ok) {
                const data = await response.json();
                const councillorCount = data.議員.length;
                
                cards.push({
                    ...municipality,
                    count: councillorCount
                });
            }
        } catch (error) {
            console.error(`Error loading data for ${municipality.name}:`, error);
            cards.push({
                ...municipality,
                count: 0
            });
        }
    }
    
    // Sort municipalities by name
    cards.sort((a, b) => a.name.localeCompare(b.name, 'ja'));
    
    // Create HTML for cards
    container.innerHTML = cards.map(municipality => `
        <a href="municipality.html?code=${municipality.code}&name=${encodeURIComponent(municipality.name)}" class="municipality-card">
            <h3>${municipality.name}</h3>
            <div class="councillor-count">議員数: ${municipality.count}名</div>
        </a>
    `).join('');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', loadMunicipalities);