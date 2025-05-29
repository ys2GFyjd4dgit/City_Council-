// Get municipality info from URL parameters
const urlParams = new URLSearchParams(window.location.search);
const municipalityCode = urlParams.get('code');
const municipalityName = urlParams.get('name');
const prefecture = urlParams.get('prefecture');

// State variables
let councillorsData = [];
let filteredData = [];
let currentSort = { field: 'name', ascending: true };

// Initialize the page
async function initialize() {
    if (!municipalityCode || !municipalityName) {
        window.location.href = 'index.html';
        return;
    }
    
    console.log('Initializing municipality page:', {
        code: municipalityCode,
        name: municipalityName,
        prefecture: prefecture
    });
    
    // Set page title
    document.getElementById('municipality-name').textContent = `${municipalityName} 議会議員一覧`;
    document.title = `${municipalityName} 議会議員一覧`;
    
    // Load static data
    loadStaticData();
}

// Load councillor data from static JS file
function loadStaticData() {
    // 静的データファイルを動的に読み込む
    const script = document.createElement('script');
    script.src = `js/municipalities/${municipalityCode}.js`;
    
    console.log('Loading script:', script.src);
    
    script.onload = function() {
        console.log('Script loaded successfully');
        
        // グローバル変数から議員データを取得
        const memberVariable = `municipalityMembers_${municipalityCode}`;
        console.log('Looking for variable:', memberVariable);
        console.log('Available in window:', Object.keys(window).filter(key => key.startsWith('municipalityMembers_')));
        
        if (window[memberVariable]) {
            councillorsData = window[memberVariable];
            filteredData = [...councillorsData];
            
            console.log('Data loaded:', councillorsData.length, 'members');
            
            // Populate party filter
            populatePartyFilter();
            
            // Initial render
            renderTable();
            updateStats();
            
            // Set up event listeners
            setupEventListeners();
        } else {
            console.error('Variable not found:', memberVariable);
            showError();
        }
    };
    
    script.onerror = function(error) {
        console.error('Failed to load script:', error);
        showError();
    };
    
    document.head.appendChild(script);
}

function showError() {
    document.getElementById('councillor-tbody').innerHTML = 
        '<tr><td colspan="4" style="text-align: center;">データの読み込みに失敗しました。</td></tr>';
}

// Populate party filter dropdown
function populatePartyFilter() {
    const parties = [...new Set(councillorsData.map(c => c['所属']))].sort();
    const select = document.getElementById('party-filter');
    
    select.innerHTML = '<option value="">すべて</option>';
    parties.forEach(party => {
        const option = document.createElement('option');
        option.value = party;
        option.textContent = party;
        select.appendChild(option);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Search input
    document.getElementById('search-input').addEventListener('input', filterData);
    
    // Party filter
    document.getElementById('party-filter').addEventListener('change', filterData);
    
    // Sort headers
    document.querySelectorAll('th.sortable').forEach(th => {
        th.addEventListener('click', () => {
            const field = th.dataset.sort;
            sortData(field);
        });
    });
}

// Filter data based on search and party selection
function filterData() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const selectedParty = document.getElementById('party-filter').value;
    
    filteredData = councillorsData.filter(councillor => {
        const matchesSearch = !searchTerm || 
            councillor['氏名'].toLowerCase().includes(searchTerm) ||
            (councillor['よみ'] && councillor['よみ'].toLowerCase().includes(searchTerm));
        
        const matchesParty = !selectedParty || councillor['所属'] === selectedParty;
        
        return matchesSearch && matchesParty;
    });
    
    renderTable();
    updateStats();
}

// Sort data by field
function sortData(field) {
    // Toggle sort direction if same field
    if (currentSort.field === field) {
        currentSort.ascending = !currentSort.ascending;
    } else {
        currentSort.field = field;
        currentSort.ascending = true;
    }
    
    // Update sort icons
    document.querySelectorAll('th.sortable').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
        if (th.dataset.sort === field) {
            th.classList.add(currentSort.ascending ? 'sort-asc' : 'sort-desc');
        }
    });
    
    // Sort the data
    filteredData.sort((a, b) => {
        let aVal, bVal;
        
        switch(field) {
            case 'name':
                aVal = a['氏名'];
                bVal = b['氏名'];
                break;
            case 'ruby':
                aVal = a['よみ'] || '';
                bVal = b['よみ'] || '';
                break;
            case 'party':
                aVal = a['所属'];
                bVal = b['所属'];
                break;
            case 'x_account':
                aVal = a['X（旧Twitter）'] ? '1' : '0';
                bVal = b['X（旧Twitter）'] ? '1' : '0';
                break;
        }
        
        if (aVal < bVal) return currentSort.ascending ? -1 : 1;
        if (aVal > bVal) return currentSort.ascending ? 1 : -1;
        return 0;
    });
    
    renderTable();
}

// Render the table
function renderTable() {
    const tbody = document.getElementById('councillor-tbody');
    const noResults = document.getElementById('no-results');
    
    if (filteredData.length === 0) {
        tbody.innerHTML = '';
        noResults.style.display = 'block';
        return;
    }
    
    noResults.style.display = 'none';
    
    tbody.innerHTML = filteredData.map(councillor => {
        const xAccountCell = councillor['X（旧Twitter）'] 
            ? `<a href="${councillor['X（旧Twitter）']}" target="_blank" rel="noopener noreferrer">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
               </a>`
            : '-';
        
        return `
            <tr>
                <td>${councillor['氏名']}</td>
                <td>${councillor['よみ'] || '-'}</td>
                <td>${councillor['所属']}</td>
                <td class="x-cell">${xAccountCell}</td>
            </tr>
        `;
    }).join('');
}

// Update statistics
function updateStats() {
    const totalCount = filteredData.length;
    const xAccountCount = filteredData.filter(c => c['X（旧Twitter）']).length;
    
    document.getElementById('total-count').textContent = `総数: ${totalCount}名`;
    document.getElementById('x-account-count').textContent = `X保有: ${xAccountCount}名`;
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initialize);