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
    
    // Conditional logic setup
    setupConditionalLogic();
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

// --- Conditional Logic for Form ---

function setupConditionalLogic() {
    const s_infarct_type = document.getElementById('infarct_type');
    const s1_leuko = document.getElementById('s1_lacunar_plus_severe_leuko');
    const s3_leuko = document.getElementById('s3_severe_leuko_isolated');
    
    const c1_pfo = document.getElementById('c1_pfo_pe_dvt');
    const c2_pfo = document.getElementById('c2_pfo_asa');
    const c3_pfo = document.getElementById('c3_pfo_isolated');

    // Listeners
    s_infarct_type?.addEventListener('change', handleInfarctTypeChange);
    s1_leuko?.addEventListener('change', () => handleMutualExclusiveChange(s1_leuko, s3_leuko));
    s3_leuko?.addEventListener('change', () => handleMutualExclusiveChange(s3_leuko, s1_leuko));
    
    c1_pfo?.addEventListener('change', () => handlePFOChange(c1_pfo, [c2_pfo, c3_pfo]));
    c2_pfo?.addEventListener('change', () => handlePFOChange(c2_pfo, [c1_pfo, c3_pfo]));
    c3_pfo?.addEventListener('change', () => handlePFOChange(c3_pfo, [c1_pfo, c2_pfo]));

    // Initial state
    handleInfarctTypeChange();
}

function handleInfarctTypeChange() {
    const infarctType = document.getElementById('infarct_type').value;
    const svdFields = [
        's_has_htn_or_dm', 
        's1_lacunar_infarct_syndrome', 
        's1_lacunar_plus_severe_leuko', 
        's3_severe_leuko_isolated'
    ];
    
    const show = infarctType === 'subcortical_small_lacunar';
    
    svdFields.forEach(fieldName => {
        const field = document.getElementById(fieldName);
        const parent = field?.closest('.form-group');
        if (parent) {
            parent.style.display = show ? '' : 'none';
            if (!show) field.checked = false;
        }
    });
}

function handleMutualExclusiveChange(source, target) {
    if (source.checked) {
        target.checked = false;
        target.disabled = true;
    } else {
        target.disabled = false;
    }
}

function handlePFOChange(source, targets) {
    if (source.checked) {
        targets.forEach(target => {
            if(target) {
                target.checked = false;
                target.disabled = true;
            }
        });
    } else {
        targets.forEach(target => {
            if(target) target.disabled = false;
        });
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
    // Update Badges
    document.getElementById('ascod-badge').textContent = result.ascod_code || 'N/A';
    document.getElementById('toast-badge').textContent = result.toast_code || 'N/A';
    
    // Display ASCOD Justifications
    let ascodHtml = '';
    if (result.ascod) {
        const ascodOrder = ['A', 'S', 'C', 'O', 'D'];
        const ascodNames = { A: 'Aterosclerose', S: 'Pequenos Vasos', C: 'Cardiopatia', O: 'Outras Causas', D: 'Dissecção' };
        
        ascodHtml = ascodOrder.map(key => {
            const item = result.ascod[key];
            if (!item) return '';
            
            // Garante que o grau 0 seja exibido corretamente
            const grade = (item.grade !== null && typeof item.grade !== 'undefined') ? item.grade : 'N/A';

            // Tenta obter a justificativa a partir de várias possíveis chaves que o modelo possa retornar
            const justification = item.justification || item.justificativa || item.raciocinio || item.rationale || item.reason || '';

            return `
                <div class="justification-item">
                    <div class="justification-header">
                        <span class="component-key">${key}</span>
                        <span class="component-grade grade-${grade}">${grade}</span>
                        <span class="component-name">${ascodNames[key]}</span>
                    </div>
                    <p class="justification-text">${justification || 'Justificativa não fornecida.'}</p>
                </div>
            `;
        }).join('');
    } else {
        ascodHtml = '<p>Justificativas ASCOD não disponíveis.</p>';
    }
    document.getElementById('ascod-details').innerHTML = ascodHtml;

    // Display TOAST Justification
    const toastJustification = result.toast?.justification || result.toast?.justificativa || result.toast?.raciocinio || result.toast?.rationale || result.toast?.reason || '';

    let toastHtml = '';
    if (result.toast && toastJustification) {
        toastHtml = `
            <div class="justification-item toast-justification">
                <strong>${result.toast_code || 'TOAST'}</strong>
                <p class="justification-text">${toastJustification}</p>
            </div>
        `;
    } else {
        toastHtml = '<p>Justificativa TOAST não disponível.</p>';
    }
    document.getElementById('toast-details').innerHTML = toastHtml;

    // Display Full Analysis / Sent Text
    const fullAnalysisContent = document.getElementById('full-analysis-content');
    if (result.natural_language_prompt) {
        fullAnalysisContent.innerHTML = `
            <h4>Texto Enviado para Análise</h4>
            <p class="analysis-prompt">${result.natural_language_prompt}</p>
        `;
    } else {
        fullAnalysisContent.innerHTML = `
            <h4>Texto Enviado para Análise</h4>
            <p>N/A</p>
        `;
    }
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
    // Re-apply conditional logic to reset form to a consistent state
    setupConditionalLogic(); 
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Add CSS for component display
const style = document.createElement('style');
style.textContent = `
    .justification-item {
        padding: 0.75rem 1rem;
        background: #f9fafb;
        border-radius: 8px;
        margin-bottom: 0.75rem;
        border-left: 4px solid #dbeafe; /* primary-color-light */
    }
    .justification-item.toast-justification {
        border-left-color: #d1fae5; /* success-color-light */
    }
    .justification-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.5rem;
    }
    .justification-text {
        color: #4b5563; /* gray-600 */
        font-size: 0.9rem;
        line-height: 1.5;
        margin: 0;
    }
    .analysis-prompt {
        font-style: italic;
        color: #6b7280; /* gray-500 */
        background-color: #f9fafb;
        padding: 1rem;
        border-radius: 8px;
    }
    .component-key {
        font-weight: 700;
        color: var(--primary-color);
        font-size: 1.1rem;
    }
    .component-grade {
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        color: white;
        font-size: 0.9rem;
        min-width: 20px;
        text-align: center;
    }
    .grade-0 { background: var(--success-color); }
    .grade-1 { background: var(--danger-color); }
    .grade-2 { background: var(--warning-color); }
    .grade-3 { background: var(--gray-color); }
    .grade-9 { background: var(--dark-color); }
    .component-name {
        flex: 1;
        color: var(--dark-color);
        font-weight: 500;
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
`;
document.head.appendChild(style); 