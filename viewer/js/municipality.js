// Get municipality info from URL parameters
const urlParams = new URLSearchParams(window.location.search);
const municipalityCode = urlParams.get('code');
const municipalityName = urlParams.get('name');

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
    
    // Set page title
    document.getElementById('municipality-name').textContent = `${municipalityName} 市議会議員一覧`;
    document.title = `${municipalityName} 市議会議員一覧`;
    
    // Load data
    await loadCouncillorData();
    
    // Set up event listeners
    setupEventListeners();
}

// Load councillor data from JSON
async function loadCouncillorData() {
    try {
        const response = await fetch(`../data/processed/議員リスト_${municipalityCode}_${municipalityName}.json`);
        if (!response.ok) {
            throw new Error('Data not found');
        }
        
        const data = await response.json();
        councillorsData = data.議員 || [];
        filteredData = [...councillorsData];
        
        // Populate party filter
        populatePartyFilter();
        
        // Initial render
        renderTable();
        updateStats();
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('councillor-tbody').innerHTML = 
            '<tr><td colspan="5" style="text-align: center;">データの読み込みに失敗しました。</td></tr>';
    }
}

// Populate party filter dropdown
function populatePartyFilter() {
    const parties = [...new Set(councillorsData.map(c => c.政党・会派))].sort();
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
            councillor.議員名.toLowerCase().includes(searchTerm) ||
            (councillor.ふりがな && councillor.ふりがな.toLowerCase().includes(searchTerm));
        
        const matchesParty = !selectedParty || councillor['政党・会派'] === selectedParty;
        
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
                aVal = a.議員名;
                bVal = b.議員名;
                break;
            case 'ruby':
                aVal = a.ふりがな || '';
                bVal = b.ふりがな || '';
                break;
            case 'party':
                aVal = a['政党・会派'];
                bVal = b['政党・会派'];
                break;
            case 'x_account':
                aVal = a.x_account || '';
                bVal = b.x_account || '';
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
        const xAccountCell = councillor.x_account 
            ? `<a href="https://x.com/${councillor.x_account}" target="_blank" rel="noopener noreferrer">@${councillor.x_account}</a>`
            : '-';
        
        const profileCell = councillor.profile_url
            ? `<a href="${councillor.profile_url}" target="_blank" rel="noopener noreferrer">プロフィール</a>`
            : '-';
        
        return `
            <tr>
                <td>${councillor.議員名}</td>
                <td>${councillor.ふりがな || '-'}</td>
                <td>${councillor['政党・会派']}</td>
                <td>${xAccountCell}</td>
                <td>${profileCell}</td>
            </tr>
        `;
    }).join('');
}

// Update statistics
function updateStats() {
    const totalCount = filteredData.length;
    const xAccountCount = filteredData.filter(c => c.x_account).length;
    
    document.getElementById('total-count').textContent = `総数: ${totalCount}`;
    document.getElementById('x-account-count').textContent = `X アカウント保有: ${xAccountCount}`;
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initialize);