// App State
let currentTab = 'structured';

// DOM Elements
const tabButtons = document.querySelectorAll('.tab-button');
const tabPanes = document.querySelectorAll('.tab-pane');
const structuredForm = document.getElementById('structured-form');
const textForm = document.getElementById('text-form');
const resultsSection = document.getElementById('results-section');
const stenosisRange = document.getElementById('stenosis');
const rangeValue = document.querySelector('.range-value');
const pfoCheckbox = document.getElementById('pfo');
const venousThrombosisGroup = document.getElementById('venous-thrombosis-group');
const dissectionCheckbox = document.getElementById('dissection');
const dissectionHistoryGroup = document.getElementById('dissection-history-group');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    updateRangeValue();
});

// Event Listeners
function setupEventListeners() {
    // Tab switching
    tabButtons.forEach(button => {
        button.addEventListener('click', () => switchTab(button.dataset.tab));
    });

    // Form submissions
    structuredForm.addEventListener('submit', handleStructuredSubmit);
    textForm.addEventListener('submit', handleTextSubmit);

    // Range input
    if (stenosisRange) {
        stenosisRange.addEventListener('input', updateRangeValue);
    }
}

// Tab Switching
function switchTab(tab) {
    currentTab = tab;
    
    // Update buttons
    tabButtons.forEach(button => {
        button.classList.toggle('active', button.dataset.tab === tab);
    });
    
    // Update panes
    tabPanes.forEach(pane => {
        pane.classList.toggle('active', pane.id === `${tab}-tab`);
    });
}

// Range Value Update
function updateRangeValue() {
    if (stenosisRange && rangeValue) {
        rangeValue.textContent = `${stenosisRange.value}%`;
    }
}

// Form Submissions
async function handleStructuredSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(structuredForm);
    const data = { type: 'structured' };

    // Itera sobre todos os campos do formulário para construir o objeto de dados
    for (const [key, value] of formData.entries()) {
        const element = document.getElementsByName(key)[0];
        
        if (element.type === 'checkbox') {
            // Para checkboxes, o valor só é incluído se estiver marcado.
            // O FormData já faz isso, mas garantimos o tipo booleano.
            data[key] = true;
        } else if (element.type === 'number' || element.type === 'range') {
            // Converte para número, tratando campo vazio como nulo.
            data[key] = value ? parseInt(value, 10) : null;
        } else {
            // Para outros tipos (text, select-one), usa o valor diretamente.
            data[key] = value;
        }
    }

    // Como o FormData só inclui checkboxes marcados, precisamos adicionar os desmarcados como 'false'.
    const checkboxes = structuredForm.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(cb => {
        if (!data.hasOwnProperty(cb.name)) {
            data[cb.name] = false;
        }
    });

    await submitAnalysis(data);
}

async function handleTextSubmit(e) {
    e.preventDefault();
    
    const clinicalText = document.getElementById('clinical-text').value.trim();
    if (!clinicalText) {
        alert('Por favor, insira a descrição clínica do caso.');
        return;
    }
    
    const data = {
        type: 'text',
        text: clinicalText
    };
    
    await submitAnalysis(data);
}

// Submit Analysis
async function submitAnalysis(data) {
    // Show loading state
    showResults();
    showLoading();
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            displayResults(result);
        } else {
            showError(result.error || 'Erro ao processar análise');
        }
    } catch (error) {
        showError('Erro de conexão. Verifique se o servidor está rodando.');
    }
}

// Display Functions
function showResults() {
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function showLoading() {
    document.getElementById('ascod-details').innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            Processando...
        </div>
    `;
    document.getElementById('toast-details').innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            Processando...
        </div>
    `;
    document.getElementById('ascod-badge').textContent = '-';
    document.getElementById('toast-badge').textContent = '-';
    document.getElementById('full-analysis-content').innerHTML = '';
}

function displayResults(result) {
    // Extract ASCOD components
    const ascodMatch = result.ascod_code ? result.ascod_code.match(/A(\d)-S(\d)-C(\d)-O(\d)-D(\d)/) : null;
    
    // Update ASCOD Badge
    document.getElementById('ascod-badge').textContent = result.ascod_code || 'N/A';
    
    // Update TOAST Badge
    document.getElementById('toast-badge').textContent = result.toast_code || 'N/A';
    
    // Parse and display ASCOD details
    if (ascodMatch) {
        const ascodComponents = {
            A: { grade: ascodMatch[1], name: 'Aterosclerose' },
            S: { grade: ascodMatch[2], name: 'Doença de Pequenos Vasos' },
            C: { grade: ascodMatch[3], name: 'Cardiopatia' },
            O: { grade: ascodMatch[4], name: 'Outras Causas' },
            D: { grade: ascodMatch[5], name: 'Dissecção' }
        };
        
        const ascodHtml = Object.entries(ascodComponents).map(([key, value]) => `
            <div class="ascod-component">
                <span class="component-key">${key}:</span>
                <span class="component-grade grade-${value.grade}">${value.grade}</span>
                <span class="component-name">${value.name}</span>
            </div>
        `).join('');
        
        document.getElementById('ascod-details').innerHTML = ascodHtml;
    } else {
        document.getElementById('ascod-details').innerHTML = '<p>Não foi possível extrair os componentes ASCOD</p>';
    }
    
    // Parse and display TOAST details
    const toastHtml = `
        <div class="toast-classification">
            <p><strong>Classificação:</strong> ${result.toast_code || 'N/A'}</p>
            <p class="toast-description">${getToastDescription(result.toast_code)}</p>
        </div>
    `;
    document.getElementById('toast-details').innerHTML = toastHtml;
    
    // Display full analysis
    document.getElementById('full-analysis-content').innerHTML = formatAnalysis(result.result);
}

function getToastDescription(toastCode) {
    const descriptions = {
        'TOAST 1': 'Aterosclerose de Grandes Artérias',
        'TOAST 2': 'Cardioembólico',
        'TOAST 3': 'Oclusão de Pequenas Artérias',
        'TOAST 4': 'Outra Etiologia Determinada',
        'TOAST 5a': 'Duas ou mais causas identificadas',
        'TOAST 5b': 'Criptogênico (avaliação negativa)',
        'TOAST 5c': 'Avaliação incompleta'
    };
    
    return descriptions[toastCode] || 'Classificação não reconhecida';
}

function formatAnalysis(text) {
    if (!text) return 'Análise não disponível';
    
    // Format the analysis text for better readability
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>')
        .replace(/---/g, '<hr>');
}

function showError(message) {
    const errorHtml = `<p class="error-message"><i class="fas fa-exclamation-circle"></i> ${message}</p>`;
    document.getElementById('ascod-details').innerHTML = errorHtml;
    document.getElementById('toast-details').innerHTML = errorHtml;
    document.getElementById('full-analysis-content').innerHTML = errorHtml;
}

// Reset Analysis
function resetAnalysis() {
    resultsSection.style.display = 'none';
    structuredForm.reset();
    document.getElementById('clinical-text').value = '';
    updateRangeValue();
    toggleVenousThrombosis();
    toggleDissectionHistory();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Add CSS for component display
const style = document.createElement('style');
style.textContent = `
    .ascod-component {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        background: #f9fafb;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    
    .component-key {
        font-weight: 700;
        color: var(--primary-color);
        font-size: 1.25rem;
    }
    
    .component-grade {
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        color: white;
    }
    
    .grade-0 { background: var(--success-color); }
    .grade-1 { background: var(--danger-color); }
    .grade-2 { background: var(--warning-color); }
    .grade-3 { background: var(--gray-color); }
    .grade-9 { background: var(--dark-color); }
    
    .component-name {
        flex: 1;
        color: var(--dark-color);
    }
    
    .toast-classification {
        padding: 1rem;
        background: #f9fafb;
        border-radius: 8px;
    }
    
    .toast-description {
        margin-top: 0.5rem;
        color: var(--gray-color);
        font-style: italic;
    }
    
    .error-message {
        color: var(--danger-color);
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem;
        background: #fef2f2;
        border-radius: 8px;
    }
    
    .analysis-content strong {
        color: var(--primary-color);
    }
    
    .analysis-content hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1px solid #e5e7eb;
    }
`;
document.head.appendChild(style); 