// State variables
let allCouncillorsData = [];
let filteredData = [];
let currentSort = { field: 'municipality', ascending: true };
let selectedPrefecture = '';
let municipalityMap = {};

// Initialize the page
function initializePrefecture() {
    setupPrefectureSelector();
}

// Setup prefecture selector
function setupPrefectureSelector() {
    const select = document.getElementById('prefecture-select');
    select.addEventListener('change', (e) => {
        selectedPrefecture = e.target.value;
        if (selectedPrefecture) {
            loadPrefectureData(selectedPrefecture);
        } else {
            document.getElementById('content-area').style.display = 'none';
        }
    });
}

// Load all municipality data for selected prefecture
async function loadPrefectureData(prefecture) {
    const contentArea = document.getElementById('content-area');
    const loading = document.getElementById('loading');
    const tbody = document.getElementById('councillor-tbody');
    
    // Show loading
    contentArea.style.display = 'block';
    loading.style.display = 'block';
    tbody.innerHTML = '';
    
    // Reset data
    allCouncillorsData = [];
    filteredData = [];
    municipalityMap = {};
    
    // Get municipalities for this prefecture
    const municipalities = Object.entries(municipalityData)
        .filter(([code, data]) => data.prefecture === prefecture)
        .sort(([codeA], [codeB]) => codeA.localeCompare(codeB));
    
    // Update page title
    const prefectureName = prefecture.split('_')[1];
    document.getElementById('prefecture-name').textContent = `${prefectureName} 議員一覧`;
    document.title = `${prefectureName} 議員一覧`;
    
    // Load data from each municipality
    let loadedCount = 0;
    const totalMunicipalities = municipalities.length;
    
    for (const [code, data] of municipalities) {
        try {
            await loadMunicipalityData(code, data.name);
            loadedCount++;
        } catch (error) {
            console.error(`Failed to load data for ${data.name}:`, error);
        }
    }
    
    // Hide loading
    loading.style.display = 'none';
    
    if (loadedCount === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">データの読み込みに失敗しました。</td></tr>';
        return;
    }
    
    // Setup filters and render
    filteredData = [...allCouncillorsData];
    populateMunicipalityFilter();
    populatePartyFilter();
    renderTable();
    updateStats();
    setupEventListeners();
}

// Load individual municipality data
function loadMunicipalityData(code, municipalityName) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        const version = new Date().getTime();
        script.src = `js/municipalities/${code}.js?v=${version}`;
        
        script.onload = function() {
            const memberVariable = `municipalityMembers_${code}`;
            if (window[memberVariable]) {
                const members = window[memberVariable];
                // Add municipality name to each member
                members.forEach(member => {
                    allCouncillorsData.push({
                        ...member,
                        municipality: municipalityName,
                        municipalityCode: code
                    });
                });
                municipalityMap[municipalityName] = true;
                resolve();
            } else {
                reject(new Error(`Variable ${memberVariable} not found`));
            }
        };
        
        script.onerror = function() {
            reject(new Error(`Failed to load script for ${code}`));
        };
        
        document.head.appendChild(script);
    });
}

// Populate municipality filter dropdown
function populateMunicipalityFilter() {
    const municipalities = Object.keys(municipalityMap).sort();
    const select = document.getElementById('municipality-filter');
    
    select.innerHTML = '<option value="">すべて</option>';
    municipalities.forEach(municipality => {
        const option = document.createElement('option');
        option.value = municipality;
        option.textContent = municipality;
        select.appendChild(option);
    });
}

// Populate party filter dropdown
function populatePartyFilter() {
    const parties = [...new Set(allCouncillorsData.map(c => c['所属']))].sort();
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
    // Remove existing listeners
    const searchInput = document.getElementById('search-input');
    const municipalityFilter = document.getElementById('municipality-filter');
    const partyFilter = document.getElementById('party-filter');
    const sortHeaders = document.querySelectorAll('th.sortable');
    
    // Clone and replace to remove listeners
    const newSearchInput = searchInput.cloneNode(true);
    searchInput.parentNode.replaceChild(newSearchInput, searchInput);
    
    const newMunicipalityFilter = municipalityFilter.cloneNode(true);
    municipalityFilter.parentNode.replaceChild(newMunicipalityFilter, municipalityFilter);
    
    const newPartyFilter = partyFilter.cloneNode(true);
    partyFilter.parentNode.replaceChild(newPartyFilter, partyFilter);
    
    // Add new listeners
    document.getElementById('search-input').addEventListener('input', filterData);
    document.getElementById('municipality-filter').addEventListener('change', filterData);
    document.getElementById('party-filter').addEventListener('change', filterData);
    
    sortHeaders.forEach(th => {
        const newTh = th.cloneNode(true);
        th.parentNode.replaceChild(newTh, th);
    });
    
    document.querySelectorAll('th.sortable').forEach(th => {
        th.addEventListener('click', () => {
            const field = th.dataset.sort;
            sortData(field);
        });
    });
}

// Filter data based on search and filters
function filterData() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const selectedMunicipality = document.getElementById('municipality-filter').value;
    const selectedParty = document.getElementById('party-filter').value;
    
    filteredData = allCouncillorsData.filter(councillor => {
        const matchesSearch = !searchTerm || 
            councillor['氏名'].toLowerCase().includes(searchTerm) ||
            (councillor['よみ'] && councillor['よみ'].toLowerCase().includes(searchTerm));
        
        const matchesMunicipality = !selectedMunicipality || councillor.municipality === selectedMunicipality;
        const matchesParty = !selectedParty || councillor['所属'] === selectedParty;
        
        return matchesSearch && matchesMunicipality && matchesParty;
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
            case 'municipality':
                aVal = a.municipality;
                bVal = b.municipality;
                break;
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
                <td>${councillor.municipality}</td>
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