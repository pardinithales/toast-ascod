import { GoogleGenerativeAI } from '@google/generative-ai';
import readline from 'readline';

// Configuração da API
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || 'AIzaSyDxgqx1FeA-vK7rxkfcBhTOV0yy5kCjhrg');

// Prompt completo do sistema ASCOD
const ASCOD_SYSTEM_INSTRUCTION = `### **Prompt para Classificação de AVC Isquêmico com base no Fenótipo ASCOD**

**## Persona e Objetivo**

Você é um assistente de IA especializado em neurologia vascular, treinado especificamente para atuar como um sistema de suporte à decisão clínica. Seu objetivo é classificar o subtipo de acidente vascular cerebral (AVC) isquêmico de um paciente com base nos critérios rigorosos do fenótipo ASCOD (Aterosclerose, Doença de Pequenos Vasos, Cardiopatia, Outras causas, Dissecção). Você deve analisar as informações clínicas e de exames fornecidas e atribuir um grau de causalidade para cada uma das cinco categorias.

**## Base de Conhecimento (Fonte da Verdade)**

Para esta tarefa, você deve utilizar **EXCLUSIVAMENTE** a tabela de critérios ASCOD fornecida abaixo. Não utilize nenhum conhecimento prévio ou externo. A sua análise e classificação devem ser estritamente baseadas nas definições contidas nesta tabela.

### **Tabela de Critérios de Causalidade ASCOD**

**A - Aterosclerose**
- **A1**: Estenose ≥50% (NASCET) ou oclusão aterosclerótica em artéria intracraniana ou extracraniana clinicamente relacionada, na ausência de dissecção aguda
- **A2**: Estenose <50% (NASCET) em artéria intracraniana ou extracraniana clinicamente relacionada OU placas móveis no arco aórtico OU placas no arco aórtico ≥4mm sem estenose OU estenose ≥50% em artéria clinicamente não relacionada OU história de infarto do miocárdio, angioplastia coronária ou doença arterial periférica
- **A3**: Nenhuma aterosclerose, mas presença de ≥2 fatores de risco vascular entre: hipertensão, diabetes mellitus, tabagismo atual, dislipidemia
- **A0**: Nenhuma aterosclerose e menos de 2 fatores de risco vascular
- **A9**: Avaliação incompleta ou inadequada

**S - Doença de Pequenos Vasos (Small vessel disease)**
- **S1**: Combinação de infarto lacunar profundo recente E pelo menos UM dos seguintes: [doença de pequenos vasos definida em RM] OU [apenas um infarto lacunar recente e presença conhecida de DM ou HAS] OU [infartos múltiplos, confinados ao território de perfurantes profundos, presentes em pelo menos 3 territórios, com pelo menos 2 infartos com aspecto de idade diferente]
- **S2**: Infarto lacunar, mas múltiplas pequenas DWI agudas espalhadas em um hemisfério, ou infarto subcortical único (diâmetro no plano axial < 20mm) em território de perfurante profundo na ausência de doença de pequenos vasos definida em RM
- **S3**: Presença de leucoaraiose (definida como alterações confluentes bilaterais da substância branca com hiperintensidade em T2) sem infarto lacunar, mas com infarto visível de outro tipo
- **S0**: Ausência de infarto lacunar, leucoaraiose ou qualquer marcador de doença de pequenos vasos
- **S9**: Avaliação incompleta ou inadequada

**C - Cardiopatia**
- **C1**: Presença de uma fonte cardioembólica de alto risco detectada: fibrilação atrial, flutter atrial, prótese valvar mecânica, estenose mitral, infarto do miocárdio recente (<4 semanas), fração de ejeção ventricular esquerda <35%, trombo atrial ou ventricular, cardiomiopatia dilatada, endocardite infecciosa
- **C2**: Presença de FOP isolado com trombo venoso concomitante (ou suspeita clínica de embolia paradoxal) OU aneurisma de septo interatrial OU endocardite não bacteriana OU miocardiopatia hipertrófica com FA OU fração de ejeção ventricular esquerda >35% e <50%
- **C3**: Presença de FOP, ASA ou strands valvulares sem evidência de trombo venoso
- **C0**: Ausência de qualquer fonte cardíaca de embolia após avaliação mínima cardíaca
- **C9**: Avaliação incompleta ou inadequada

**O - Outras causas**
- **O1**: Presença de qualquer causa específica de AVC demonstrada por técnicas diagnósticas apropriadas: dissecção arterial cervical, vasculite arterial, trombofilia com trombose venosa demonstrada, doença falciforme, etc.
- **O2**: Evidência de uma causa específica provável, mas diagnóstico não definitivo
- **O0**: Ausência de outras causas específicas
- **O9**: Avaliação incompleta ou inadequada

**D - Dissecção**
- **D1**: Presença de mural hematoma, "intimal flap", duplo lúmen, oclusão arterial, estenose pseudoaneurismática ou estenose longa e afilada (>20mm) de uma artéria cervical clinicamente relacionada
- **D2**: Apenas história sugestiva de dissecção (dor cervical ipsilateral, síndrome de Horner, história de trauma cervical nas últimas 48h)
- **D0**: Ausência de dissecção arterial
- **D9**: Avaliação incompleta ou inadequada

**## Estrutura de Resposta**

Forneça uma resposta estruturada contendo:

1. **Classificação ASCOD**: No formato A[0-3,9]-S[0-3,9]-C[0-3,9]-O[0-2,9]-D[0-2,9]
2. **Justificativa detalhada**: Para cada categoria, explique o grau atribuído com base nos critérios da tabela
3. **Etiologia mais provável**: Com base na classificação, indique qual(is) etiologia(s) são consideradas causalmente relacionadas ao AVC (graus 1 ou 2)
4. **Recomendações**: Sugira investigações adicionais se houver categorias com grau 9 (avaliação incompleta)

**## Exemplo de Uso**

**Entrada:**
"Paciente de 72 anos, hipertenso e diabético, com AVC isquêmico. RM mostra infarto lacunar de 12mm em cápsula interna. Ecodoppler carotídeo com estenose de 30% em carótida direita. ECG em ritmo sinusal. Ecocardiograma normal."

**Saída esperada:**
- Classificação: A3-S1-C0-O0-D0
- Justificativas: [detalhamento baseado nos critérios]
- Etiologia mais provável: Doença de pequenos vasos (S1)
- Recomendações: Considerar avaliação para outras causas se evolução atípica

---

**Importante**: Sempre se atenha estritamente aos critérios da tabela. Não faça inferências além do que está explicitamente definido nos critérios ASCOD.`;

// Classe para gerenciar o classificador
class ASCODClassifier {
    constructor() {
        this.model = genAI.getGenerativeModel({
            model: 'gemini-2.0-flash-exp',
            systemInstruction: ASCOD_SYSTEM_INSTRUCTION,
            generationConfig: {
                temperature: 0.2,
                topK: 20,
                topP: 0.8,
                maxOutputTokens: 2048,
            },
        });
        
        this.rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
    }

    // Calcula classificação ASCOD baseada em dados estruturados
    calculateASCOD(data) {
        let ascod = { A: {}, S: {}, C: {}, O: {}, D: {} };

        // A - Aterosclerose
        if (data.stenosis >= 50) {
            ascod.A = { grade: 1, reason: 'A1: Estenose ≥50% em artéria clinicamente relacionada' };
        } else if (data.stenosis > 0 && data.stenosis < 50) {
            ascod.A = { grade: 2, reason: 'A2: Estenose <50% em artéria clinicamente relacionada' };
        } else if ((data.htn + data.dm + data.dlp + data.smoker) >= 2) {
            ascod.A = { grade: 3, reason: 'A3: ≥2 fatores de risco vascular presentes' };
        } else {
            ascod.A = { grade: 0, reason: 'A0: Sem aterosclerose e <2 fatores de risco' };
        }

        // S - Doença de Pequenos Vasos
        if (data.lacunarInfarct && (data.htn || data.dm)) {
            ascod.S = { grade: 1, reason: 'S1: Infarto lacunar com HAS ou DM' };
        } else if (data.lacunarInfarct) {
            ascod.S = { grade: 2, reason: 'S2: Infarto lacunar sem critérios completos para S1' };
        } else if (data.leukoaraiosis) {
            ascod.S = { grade: 3, reason: 'S3: Leucoaraiose sem infarto lacunar' };
        } else {
            ascod.S = { grade: 0, reason: 'S0: Sem marcadores de doença de pequenos vasos' };
        }

        // C - Cardiopatia
        if (data.afib || data.mechValve || data.recentMI || data.lvef < 35 || data.thrombus || data.endocarditis) {
            ascod.C = { grade: 1, reason: 'C1: Fonte cardioembólica de alto risco presente' };
        } else if (data.pfo && data.venousThrombosis) {
            ascod.C = { grade: 2, reason: 'C2: FOP com trombo venoso concomitante' };
        } else if (data.pfo) {
            ascod.C = { grade: 3, reason: 'C3: FOP isolado sem evidência de trombo venoso' };
        } else {
            ascod.C = { grade: 0, reason: 'C0: Sem fonte cardíaca de embolia' };
        }

        // O - Outras causas
        if (data.vasculitis || data.thrombophilia || data.otherDefiniteCause) {
            ascod.O = { grade: 1, reason: 'O1: Causa específica demonstrada' };
        } else if (data.otherProbableCause) {
            ascod.O = { grade: 2, reason: 'O2: Causa específica provável' };
        } else {
            ascod.O = { grade: 0, reason: 'O0: Sem outras causas específicas' };
        }

        // D - Dissecção
        if (data.dissection) {
            ascod.D = { grade: 1, reason: 'D1: Sinais de dissecção arterial presente' };
        } else if (data.dissectionHistory) {
            ascod.D = { grade: 2, reason: 'D2: História sugestiva de dissecção' };
        } else {
            ascod.D = { grade: 0, reason: 'D0: Sem evidência de dissecção' };
        }

        return ascod;
    }

    // Calcula classificação TOAST baseada no ASCOD
    calculateTOAST(ascod) {
        const potentialCauses = [];
        if (ascod.A.grade === 1) potentialCauses.push('Aterosclerose de Grandes Artérias');
        if (ascod.C.grade === 1) potentialCauses.push('Cardioembólico');
        if (ascod.S.grade === 1) potentialCauses.push('Oclusão de Pequenas Artérias');
        if (ascod.O.grade === 1 || ascod.D.grade === 1) potentialCauses.push('Outras Causas Determinadas');

        if (potentialCauses.length >= 2) {
            return { grade: 'TOAST 5a', reason: 'Duas ou mais causas potenciais identificadas', causes: potentialCauses };
        }
        
        if (ascod.O.grade === 1 || ascod.D.grade === 1) {
            return { grade: 'TOAST 4', reason: 'AVC de outra etiologia determinada' };
        }

        if (ascod.A.grade === 1) {
            return { grade: 'TOAST 1', reason: 'Aterosclerose de Grandes Artérias' };
        }

        if (ascod.C.grade === 1) {
            return { grade: 'TOAST 2', reason: 'Cardioembólico' };
        }

        if (ascod.S.grade === 1) {
            return { grade: 'TOAST 3', reason: 'Oclusão de Pequenas Artérias (Lacunar)' };
        }
        
        return { grade: 'TOAST 5b', reason: 'Criptogênico - nenhuma etiologia identificada' };
    }

    // Análise usando IA do Gemini
    async analyzeWithAI(clinicalDescription) {
        try {
            console.log('\n🤖 Analisando com IA...\n');
            
            const prompt = `Analise o seguinte caso clínico e forneça a classificação ASCOD completa:\n\n${clinicalDescription}`;
            
            const result = await this.model.generateContent(prompt);
            const response = await result.response;
            const text = response.text();
            
            return text;
        } catch (error) {
            console.error('Erro ao analisar com IA:', error);
            return null;
        }
    }

    // Interface de linha de comando
    async runCLI() {
        console.log('=== Classificador ASCOD/TOAST de AVC ===\n');
        console.log('Escolha uma opção:');
        console.log('1. Entrada estruturada (formulário)');
        console.log('2. Análise por texto com IA');
        console.log('3. Sair\n');

        this.rl.question('Opção: ', async (option) => {
            switch(option) {
                case '1':
                    await this.structuredInput();
                    break;
                case '2':
                    await this.aiInput();
                    break;
                case '3':
                    console.log('Encerrando...');
                    this.rl.close();
                    break;
                default:
                    console.log('Opção inválida!');
                    this.runCLI();
            }
        });
    }

    // Entrada estruturada
    async structuredInput() {
        console.log('\n--- Entrada de Dados Estruturada ---\n');
        
        const data = {
            // Fatores de risco
            htn: false,
            dm: false,
            dlp: false,
            smoker: false,
            // Achados de imagem
            stenosis: 0,
            lacunarInfarct: false,
            leukoaraiosis: false,
            // Achados cardíacos
            afib: false,
            mechValve: false,
            recentMI: false,
            lvef: 100,
            thrombus: false,
            endocarditis: false,
            pfo: false,
            venousThrombosis: false,
            // Outras causas
            vasculitis: false,
            thrombophilia: false,
            otherDefiniteCause: false,
            otherProbableCause: false,
            // Dissecção
            dissection: false,
            dissectionHistory: false
        };

        // Coleta dados via perguntas
        const questions = [
            { key: 'htn', text: 'Hipertensão? (s/n): ' },
            { key: 'dm', text: 'Diabetes? (s/n): ' },
            { key: 'dlp', text: 'Dislipidemia? (s/n): ' },
            { key: 'smoker', text: 'Tabagismo? (s/n): ' },
            { key: 'stenosis', text: 'Grau de estenose arterial ipsilateral (0-100): ', type: 'number' },
            { key: 'lacunarInfarct', text: 'Infarto lacunar presente? (s/n): ' },
            { key: 'leukoaraiosis', text: 'Leucoaraiose presente? (s/n): ' },
            { key: 'afib', text: 'Fibrilação atrial? (s/n): ' },
            { key: 'pfo', text: 'Forame oval patente? (s/n): ' },
        ];

        for (const q of questions) {
            await new Promise(resolve => {
                this.rl.question(q.text, (answer) => {
                    if (q.type === 'number') {
                        data[q.key] = parseInt(answer) || 0;
                    } else {
                        data[q.key] = answer.toLowerCase() === 's';
                    }
                    resolve();
                });
            });
        }

        // Calcula classificações
        const ascod = this.calculateASCOD(data);
        const toast = this.calculateTOAST(ascod);

        // Exibe resultados
        console.log('\n=== RESULTADOS ===\n');
        console.log(`Classificação ASCOD: A${ascod.A.grade}-S${ascod.S.grade}-C${ascod.C.grade}-O${ascod.O.grade}-D${ascod.D.grade}`);
        console.log('\nDetalhamento:');
        Object.entries(ascod).forEach(([key, value]) => {
            console.log(`  ${key}: ${value.reason}`);
        });
        
        console.log(`\nClassificação TOAST: ${toast.grade}`);
        console.log(`  Razão: ${toast.reason}`);
        if (toast.causes) {
            console.log(`  Causas competindo: ${toast.causes.join(', ')}`);
        }

        console.log('\n');
        this.runCLI();
    }

    // Entrada via IA
    async aiInput() {
        console.log('\n--- Análise por Texto com IA ---');
        console.log('Descreva o caso clínico (digite END em nova linha para finalizar):\n');

        let description = '';
        const collectInput = () => {
            this.rl.question('', (line) => {
                if (line.toUpperCase() === 'END') {
                    this.processAIInput(description);
                } else {
                    description += line + '\n';
                    collectInput();
                }
            });
        };
        
        collectInput();
    }

    async processAIInput(description) {
        const result = await this.analyzeWithAI(description);
        
        if (result) {
            console.log('\n=== Análise da IA ===\n');
            console.log(result);
        }
        
        console.log('\n');
        this.runCLI();
    }
}

// Inicializa e executa
async function main() {
    console.clear();
    const classifier = new ASCODClassifier();
    await classifier.runCLI();
}

// Executa o programa
main().catch(console.error); 