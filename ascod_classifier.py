#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classificador Etiológico de AVC com IA - ASCOD e TOAST
Versão Python com integração Google Gemini
"""

import os
import sys
import json
import requests
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum

# Configuração da API Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyDxgqx1FeA-vK7rxkfcBhTOV0yy5kCjhrg')
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"

# Prompt do sistema ASCOD
ASCOD_SYSTEM_INSTRUCTION = """### **Prompt para Classificação de AVC Isquêmico com base no Fenótipo ASCOD**

**## Persona e Objetivo**

Você é um assistente de IA especializado em neurologia vascular, treinado especificamente para atuar como um sistema de suporte à decisão clínica. Seu objetivo é classificar o subtipo de acidente vascular cerebral (AVC) isquêmico de um paciente com base nos critérios rigorosos do fenótipo ASCOD (Aterosclerose, Doença de Pequenos Vasos, Cardiopatia, Outras causas, Dissecção). Você deve analisar as informações clínicas e de exames fornecidas e atribuir um grau de causalidade para cada uma das cinco categorias.

**## Base de Conhecimento (Fonte da Verdade)**

Para esta tarefa, você deve utilizar **EXCLUSIVAMENTE** a tabela de critérios ASCOD fornecida abaixo. Não utilize nenhum conhecimento prévio ou externo. A sua análise e classificação devem ser estritamente baseadas nas definições contidas nesta tabela.

---

### **Tabela de Critérios de Causalidade ASCOD**

#### **A - Aterosclerose**

* **Grau 1 (Potencialmente Causal):**
    * (1) Estenose ≥50% de uma artéria intracraniana ou extracraniana ipsilateral que supre a área do infarto cerebral.
    * (2) Estenose <50% de uma artéria intracraniana ou extracraniana ipsilateral com trombo luminal ou placa ulcerada.
    * (3) Placa aórtica complexa (≥4 mm de espessura, ulcerada ou móvel) no arco aórtico ascendente ou proximal, na ausência de outra causa definida.
    * (4) Infarto do miocárdio recente (≤1 mês) com evidência de trombo mural no ventrículo esquerdo (VE) ou acinesia/discinesia regional.
    * (5) História de infarto do miocárdio, revascularização coronária ou doença arterial periférica, mais um padrão de infarto embólico (infarto cortical ou cerebelar >1,5 cm, ou múltiplos infartos em diferentes territórios arteriais) na ausência de outra fonte embólica.

* **Grau 2 (Ligação Causal Incerta):**
    * (1) Estenose <50% de uma artéria intracraniana ou extracraniana ipsilateral.
    * (2) Placa aórtica (espessura <4 mm) no arco aórtico ascendente ou proximal.
    * (3) Quaisquer achados de aterosclerose nos graus A1 ou A2 em uma artéria contralateral ou não relacionada.
    * (4) Doença arterial coronariana ou periférica sem um padrão de infarto embólico.

* **Grau 3 (Ligação Causal Improvável, mas Doença Presente):**
    * (1) Fatores de risco vascular (hipertensão, diabetes, tabagismo, dislipidemia, etc.) na ausência de aterosclerose documentada nos graus A1 ou A2.

* **Grau 0 (Doença Ausente):**
    * (1) Ausência de qualquer um dos achados acima após a realização dos seguintes diagnósticos: ultrassom (US), angiotomografia (Angio-TC), angiorressonância (Angio-RM) ou angiografia por subtração digital (DSA) das artérias cervicais e intracranianas; e ecocardiograma transesofágico (ETE) para o arco aórtico.

* **Grau 9 (Avaliação Incompleta):**
    * (1) A investigação diagnóstica mínima (pelo menos US ou Angio-TC ou Angio-RM das artérias cervicais e US transcraniano (DTC) ou Angio-TC/Angio-RM das artérias intracranianas; mais avaliação do arco aórtico por ETE) não foi realizada.

---

#### **S - Doença de Pequenos Vasos (Small-Vessel Disease)**

* **Grau 1 (Potencialmente Causal):**
    * (1) Combinação de: (a) um síndrome lacunar clássico e (b) um infarto recente subcortical ou do tronco cerebral <20 mm (em RM com DWI) ou <15 mm (em TC) em uma área de artéria perfurante, na ausência de outras causas potenciais de infarto lacunar.
    * (2) Um único infarto subcortical ou do tronco cerebral <20 mm em RM com DWI, isolado (isto é, sem lesão cortical), em um paciente com história de hipertensão ou diabetes mellitus.

* **Grau 2 (Ligação Causal Incerta):**
    * (1) Apenas um infarto subcortical ou do tronco cerebral clinicamente silencioso, <20 mm em RM ou <15 mm em TC.
    * (2) Apenas leucoaraiose (hiperintensidades da substância branca periventricular ou subcortical).

* **Grau 3 (Ligação Causal Improvável, mas Doença Presente):**
    * (1) Apenas espaços perivasculares alargados.
    * (2) Apenas micro-hemorragias cerebrais em RM (T2* ou SWI) em localizações típicas para angiopatia hipertensiva (gânglios da base, tálamo, tronco cerebral, cerebelo).
    * (3) Leucoaraiose grave bilateral (grau 3 de Fazekas) ou lacunas múltiplas (≥3) em pacientes sem história de hipertensão ou diabetes, ou com um padrão de infarto que não seja compatível com doença de pequenos vasos.

* **Grau 0 (Doença Ausente):**
    * (1) Ausência de qualquer um dos achados acima em RM ou TC.

* **Grau 9 (Avaliação Incompleta):**
    * (1) TC ou RM não realizada.

---

#### **C - Cardiopatia (Cardiac Pathology)**

* **Grau 1 (Potencialmente Causal):**
    * Uma ou mais das seguintes fontes cardíacas de alto risco na ausência de outra causa:
    * (1) Fibrilação atrial (FA) ou flutter atrial (permanente, persistente ou paroxístico).
    * (2) Trombo no átrio esquerdo (AE) ou ventrículo esquerdo (VE).
    * (3) Doença do nó sinusal ou bloqueio atrioventricular de 2º ou 3º grau.
    * (4) Prótese valvar mecânica.
    * (5) Estenose mitral reumática.
    * (6) Infarto do miocárdio recente (<3 meses).
    * (7) Cardiomiopatia dilatada.
    * (8) Mixoma atrial ou fibroelastoma papilar.
    * (9) Endocardite infecciosa.
    * (10) Fração de ejeção do VE <30%.
    * (11) Combinação de um padrão de infarto embólico (infarto cortical ou cerebelar >1,5 cm, ou múltiplos infartos em diferentes territórios arteriais) com uma fonte cardíaca de risco menor (ver grau C2).

* **Grau 2 (Ligação Causal Incerta):**
    * Uma ou mais das seguintes fontes cardíacas de risco menor, na ausência de fontes de alto risco (Grau C1):
    * (1) Forame oval patente (FOP) ou aneurisma do septo atrial (ASA), ou ambos.
    * (2) Fumaça ou contraste espontâneo no AE.
    * (3) Calcificação do anel mitral.
    * (4) Prolapso da valva mitral.
    * (5) Infarto do miocárdio antigo (>3 meses, <1 ano).
    * (6) Hipocinesia regional do VE.
    * (7) Prótese valvar biológica.
    * (8) Insuficiência cardíaca congestiva.

* **Grau 3 (Ligação Causal Improvável, mas Doença Presente):**
    * (1) Características ecocardiográficas sugestivas de embolia paradoxal (passagem de contraste da direita para a esquerda, espontânea ou com manobra de Valsalva) sem um evento embólico documentado.
    * (2) Características morfológicas do FOP associadas a risco embólico (FOP longo, ASA hipermóvel).
    * (3) Outras anormalidades cardíacas sem potencial embólico claro.

* **Grau 0 (Doença Ausente):**
    * (1) Ausência de qualquer anormalidade nos graus C1, C2 ou C3, após ECG, monitoramento Holter e ecocardiograma (transtorácico e/ou transesofágico).

* **Grau 9 (Avaliação Incompleta):**
    * (1) ECG, monitoramento Holter e ecocardiograma não realizados.

---

#### **O - Outra Causa (Other Cause)**

* **Grau 1 (Potencialmente Causal):**
    * Qualquer causa incomum de AVC com evidência sobreposta. Por exemplo:
    * (1) Vasculite do SNC com achados anormais no LCR e/ou angiografia.
    * (2) Vasculopatia não aterosclerótica (Moyamoya, Fabry, MELAS, etc.).
    * (3) Trombofilia (anticoagulante lúpico, deficiência de proteína C/S, etc.) com trombo venoso ou arterial.
    * (4) Doença hematológica (policitemia vera, trombocitemia essencial, etc.).
    * (5) Vasoespasmo cerebral.

* **Grau 2 (Ligação Causal Incerta):**
    * (1) Causa incomum com evidência incompleta ou conflitante.
    * (2) Enxaqueca com aura, em paciente com história de enxaqueca, mas o AVC não ocorreu durante uma crise de enxaqueca.

* **Grau 3 (Ligação Causal Improvável, mas Doença Presente):**
    * (1) Estado protrombótico (hiper-homocisteinemia, fator V de Leiden) sem trombose ou embolia pulmonar.
    * (2) Câncer ativo.

* **Grau 0 (Doença Ausente):**
    * (1) Ausência de outras causas após exames negativos (hemograma completo, exames de coagulação, avaliação de trombofilia, etc., com base na suspeita clínica).

* **Grau 9 (Avaliação Incompleta):**
    * (1) Avaliação incompleta com base na suspeita clínica para excluir outras causas.

---

#### **D - Dissecção (Dissection)**

* **Grau 1 (Potencialmente Causal):**
    * (1) Dissecção (espontânea ou traumática) de uma artéria cervical ou intracraniana que supre a área isquêmica, com ou sem aneurisma dissecante.
    * (2) Hematoma intramural ou retalho intimal visto na RM, Angio-TC, Angio-RM ou ultrassom.
    * (3) Estenose longa e afilada ("sinal do barbante") ou oclusão na angiografia em um paciente jovem sem aterosclerose.
    * (4) Sinal de dupla luz na angiografia.
    * (5) Aneurisma dissecante.

* **Grau 2 (Ligação Causal Incerta):**
    * (1) Displasia fibromuscular com AVC isquêmico sem dissecção arterial ou trombo documentado.
    * (2) História de trauma cervical ou dor de cabeça/pescoço sem evidência radiológica de dissecção.

* **Grau 3 (Ligação Causal Improvável, mas Doença Presente):**
    * (1) Conectivopatias (Marfan, Ehlers-Danlos tipo IV) ou outros fatores de risco para dissecção, mas sem dissecção documentada.

* **Grau 0 (Doença Ausente):**
    * (1) Ausência de dissecção após avaliação com Angio-RM/Angio-TC de pescoço e crânio ou angiografia convencional.

* **Grau 9 (Avaliação Incompleta):**
    * (1) Avaliação mínima das artérias cervicais e intracranianas (conforme definido em A9) não realizada.

---

**## Formato de Entrada do Usuário**

O usuário (médico) fornecerá as informações do paciente de forma estruturada, cobrindo os seguintes domínios. Você deve solicitar informações adicionais se os dados forem insuficientes.

*   **História Clínica:** Idade, sexo, fatores de risco vascular (HAS, DM, DLP, tabagismo), história de cardiopatia, enxaqueca, trauma recente, neoplasia, doenças do tecido conjuntivo.
*   **Apresentação Clínica:** Descrição do déficit neurológico (ex: hemiparesia, afasia), modo de instalação (súbito, progressivo).
*   **Imagem Cerebral (TC/RM):** Localização e tamanho do(s) infarto(s) (cortical, subcortical, >1,5 cm, <1,5 cm, lacunar), presença de leucoaraiose, micro-hemorragias.
*   **Avaliação Vascular (Doppler de carótidas/vertebrais, DTC, Angio-TC, Angio-RM):** Grau de estenose em artérias extracranianas e intracranianas, presença de placas (ulceradas, complexas), sinais de dissecção (hematoma intramural, flap intimal), achados no arco aórtico.
*   **Avaliação Cardíaca (ECG, Holter 24h, Ecocardiograma Transtorácico/Transesofágico):** Ritmo cardíaco (sinusal, FA), função e dimensões de câmaras cardíacas, presença de trombo intracavitário, FOP, ASA, doença valvar.
*   **Exames Laboratoriais:** Hemograma, coagulograma, perfil de trombofilia (se realizado).

**## Instruções da Tarefa e Formato de Saída**

1.  Analise rigorosamente os dados do paciente fornecidos.
2.  Para cada categoria (A, S, C, O, D), atribua um grau (1, 2, 3, 0 ou 9) com base estrita nos critérios da tabela.
3.  Se as informações forem insuficientes para avaliar uma categoria de forma conclusiva, atribua o grau 9 e especifique qual exame ou informação está faltando para completar a avaliação.
4.  Apresente o resultado no seguinte formato **EXATO**:

**Classificação ASCOD Final:** A[nota]-S[nota]-C[nota]-O[nota]-D[nota]

**Justificativa Detalhada:**

*   **A (Aterosclerose): Grau [nota]**
    *   **Critério(s) Atendido(s):** [Cite o número e a descrição exata do critério da tabela que justifica a nota. Ex: "A1(1): Estenose ≥50% de uma artéria..."]
    *   **Raciocínio:** [Breve explicação de como os dados do paciente se encaixam no critério. Ex: "A angio-TC de vasos cervicais demonstrou estenose de 70% na origem da artéria carótida interna esquerda, ipsilateral ao infarto em território de ACM."].

*   **S (Doença de Pequenos Vasos): Grau [nota]**
    *   **Critério(s) Atendido(s):** [Cite o critério.]
    *   **Raciocínio:** [Explique a lógica.]

*   **C (Cardiopatia): Grau [nota]**
    *   **Critério(s) Atendido(s):** [Cite o critério.]
    *   **Raciocínio:** [Explique a lógica.]

*   **O (Outra Causa): Grau [nota]**
    *   **Critério(s) Atendido(s):** [Cite o critério.]
    *   **Raciocínio:** [Explique a lógica.]

*   **D (Dissecção): Grau [nota]**
    *   **Critério(s) Atendido(s):** [Cite o critério.]
    *   **Raciocínio:** [Explique a lógica.]

--- CLASSIFICAÇÃO TOAST ---

Classificação Final: TOAST [nota] – [Nome da classificação]

Raciocínio Detalhado:

Critérios de Inclusão Atendidos: [Cite o critério.]
Critérios de Exclusão Verificados: [Cite o critério.]
Conclusão: [Breve explicação de como os dados do paciente se encaixam no critério.]

**Importante**: Sempre se atenha estritamente aos critérios da tabela. Não faça inferências além do que está explicitamente definido nos critérios ASCOD.
--- Base de Conhecimento 2: Critérios TOAST
TOAST 1 – Aterosclerose de Grandes Artérias (LAA)
Critérios de Inclusão: AVC causado por aterotrombose ou tromboembolismo artéria-artéria, evidenciado por:
Estenose significativa (>50%) ou oclusão de uma artéria relevante extra ou intracraniana.
Lesão cortical ou lesão subcortical com diâmetro > 1,5 cm na imagem cerebral (TC/RM).
Critérios de Exclusão: Presença de uma fonte cardioembólica potencial de alto risco.
TOAST 2 – Cardioembólico (CE)
Critérios de Inclusão: AVC presumivelmente causado por um êmbolo de origem cardíaca. Requer:
Identificação de pelo menos uma fonte cardioembólica de alto ou médio risco.
Fontes de alto risco: Fibrilação atrial (FA), prótese valvar mecânica, trombo no átrio/ventrículo esquerdo, mixoma atrial, endocardite infecciosa recente.
Múltiplos infartos em diferentes territórios vasculares reforçam o diagnóstico.
Critérios de Exclusão: Presença de estenose >50% em artéria extra/intracraniana relevante.
TOAST 3 – Oclusão de Pequenas Artérias / Doença de Pequenos Vasos (SVD)
Critérios de Inclusão: AVC lacunar causado por lipo-hialinose de uma artéria perfurante. Requer:
Síndrome lacunar clássica na clínica.
Presença de fatores de risco vascular tradicionais (hipertensão, diabetes).
Lesão subcortical ou em tronco cerebral com diâmetro < 1,5 cm na imagem (TC/RM).
Leucoaraiose pode estar presente.
Critérios de Exclusão: Presença de estenose >50% em artéria relevante ou fonte cardioembólica potencial. Infarto hemisférico.
TOAST 4 – AVC de Outra Etiologia Determinada
Critérios de Inclusão: AVC causado por uma condição rara ou incomum, que deve ser diagnosticada. Exemplos:
Vasculites, vasculopatias não inflamatórias (Moyamoya, Fabry), microangiopatias genéticas.
Distúrbios hematológicos (policitemia vera, trombofilia com trombose ativa).
Embolia paradoxal (requer FOP + trombo venoso comprovado).
Causas iatrogênicas, embolia gordurosa/aérea, hipoperfusão sistêmica.
TOAST 5 – AVC de Etiologia Indeterminada
Classifica-se aqui se uma das seguintes condições for atendida:
(5a) Duas ou mais causas identificadas: Duas ou mais causas potenciais foram encontradas (ex: Fibrilação Atrial e estenose carotídea >50% ipsilateral).
(5b) Avaliação negativa (Criptogênico): Nenhuma etiologia foi identificada apesar de uma extensa e completa avaliação diagnóstica.
(5c) Avaliação incompleta: A investigação diagnóstica não foi totalmente realizada, impedindo a determinação da causa.
"""
# Fim do ASCOD_SYSTEM_INSTRUCTION


@dataclass
class PatientData:
    """Estrutura de dados do paciente"""
    # Fatores de risco
    htn: bool = False
    dm: bool = False
    dlp: bool = False
    smoker: bool = False
    
    # Achados de imagem
    stenosis: int = 0
    infarct_type: str = "none" # 'none', 'cortical_large', 'subcortical_small_lacunar', 'subcortical_other_size'
    leukoaraiosis: bool = False
    
    # Achados cardíacos
    afib: bool = False
    mech_valve: bool = False
    recent_mi: bool = False # Infarto do miocárdio recente (<3 meses)
    lvef: Optional[int] = None # Fração de ejeção do VE, pode ser None se não avaliado
    thrombus: bool = False # Trombo no AE/VE
    endocarditis: bool = False
    pfo: bool = False
    venous_thrombosis: bool = False # Trombose venosa concomitante ao FOP
    
    # Outras causas
    vasculitis: bool = False
    thrombophilia: bool = False
    other_definite_cause: bool = False # Ex: Moyamoya, Fabry, etc.
    other_probable_cause: bool = False # Ex: Enxaqueca com aura (sem AVC durante a crise)
    
    # Dissecção
    dissection: bool = False # Hematoma intramural, retalho intimal, sinal do barbante
    dissection_history: bool = False # História sugestiva (dor cervical/cefaleia/trauma)

    def to_natural_language(self) -> str:
        description_parts = []

        # Fatores de Risco Vascular
        risk_factors = []
        if self.htn: risk_factors.append("Hipertensão (HAS)")
        if self.dm: risk_factors.append("Diabetes Mellitus (DM)")
        if self.dlp: risk_factors.append("Dislipidemia (DLP)")
        if self.smoker: risk_factors.append("Tabagismo")
        description_parts.append(f"Fatores de risco vascular: {', '.join(risk_factors) if risk_factors else 'Nenhum fator de risco vascular identificado'}.")

        # Imagem Cerebral
        infarct_text = ""
        if self.infarct_type == 'cortical_large':
            infarct_text = "Infarto cortical ou maior que 1.5 cm"
        elif self.infarct_type == 'subcortical_small_lacunar':
            infarct_text = "Infarto subcortical lacunar (menor que 1.5 cm ou 2.0 cm em DWI)"
        elif self.infarct_type == 'subcortical_other_size':
            infarct_text = "Infarto subcortical de tamanho não lacunar"
        else:
            infarct_text = "Não especificado"
        
        leukoaraiosis_text = "Leucoaraiose presente" if self.leukoaraiosis else "Leucoaraiose ausente"
        description_parts.append(f"Imagem cerebral: {infarct_text}. {leukoaraiosis_text}.")

        # Avaliação Vascular
        stenosis_text = f"Estenose arterial ipsilateral de {self.stenosis}%".replace(" de 0%", "ausente ou <50%")
        dissection_text = ""
        if self.dissection:
            dissection_text = "Sinais radiológicos de dissecção arterial presentes."
        elif self.dissection_history:
            dissection_text = "História clínica sugestiva de dissecção arterial."
        else:
            dissection_text = "Sem evidência de dissecção arterial."
        description_parts.append(f"Avaliação vascular: {stenosis_text}. {dissection_text}")

        # Avaliação Cardíaca
        cardiac_info = []
        if self.afib: cardiac_info.append("Fibrilação atrial")
        if self.mech_valve: cardiac_info.append("Prótese valvar mecânica")
        if self.recent_mi: cardiac_info.append("Infarto do miocárdio recente (<3 meses)")
        if self.lvef is not None: cardiac_info.append(f"Fração de ejeção do VE: {self.lvef}%")
        if self.thrombus: cardiac_info.append("Trombo intracardíaco")
        if self.endocarditis: cardiac_info.append("Endocardite")
        if self.pfo:
            pfo_detail = "Forame oval patente (FOP)"
            if self.venous_thrombosis: pfo_detail += " com trombose venosa concomitante"
            cardiac_info.append(pfo_detail)
        description_parts.append(f"Achados cardíacos: {', '.join(cardiac_info) if cardiac_info else 'Nenhum achado cardíaco significativo'}.")

        # Outras Causas
        other_causes_info = []
        if self.vasculitis: other_causes_info.append("Vasculite do SNC")
        if self.thrombophilia: other_causes_info.append("Trombofilia com trombo")
        if self.other_definite_cause: other_causes_info.append("Outra causa determinada (ex: Moyamoya)")
        if self.other_probable_cause: other_causes_info.append("Outra causa provável (ex: Enxaqueca com aura)")
        description_parts.append(f"Outras etiologias: {', '.join(other_causes_info) if other_causes_info else 'Nenhuma outra causa específica identificada'}.")
        
        return " ".join(description_parts).replace("  ", " ").strip()


class ASCODClassifier:
    """Classificador ASCOD/TOAST para AVC"""
    
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        
    def analyze_with_ai(self, clinical_description: str) -> Optional[str]:
        """Análise usando IA do Gemini"""
        print('\n🤖 Analisando com IA...\n')
        
        prompt = f"""Analise o seguinte caso clínico e forneça a classificação ASCOD completa:

{clinical_description}"""
        
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{
                    "text": f"{ASCOD_SYSTEM_INSTRUCTION}\n\n{prompt}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "topK": 20,
                "topP": 0.8,
                "maxOutputTokens": 2048
            }
        }
        
        try:
            response = requests.post(GEMINI_API_URL, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if 'candidates' in result and result['candidates']:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                print("Erro: Resposta inválida da API")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Erro ao chamar API Gemini: {e}")
            return None
    
    def collect_structured_input(self) -> PatientData:
        """Coleta dados estruturados via CLI"""
        print('\n--- Entrada de Dados Estruturada ---\n')
        
        data = PatientData()
        
        # Funções auxiliares
        def get_bool(prompt: str) -> bool:
            while True:
                resp = input(prompt).lower()
                if resp in ['s', 'sim', 'y', 'yes']:
                    return True
                elif resp in ['n', 'não', 'nao', 'no']:
                    return False
                print("Por favor, responda com 's' ou 'n'")
        
        def get_int(prompt: str, min_val: int = 0, max_val: int = 100, allow_none: bool = False) -> Optional[int]:
            while True:
                try:
                    val_str = input(prompt)
                    if allow_none and val_str.lower() in ['n/a', 'na', 'none', '']:
                        return None
                    val = int(val_str)
                    if min_val <= val <= max_val:
                        return val
                    print(f"Por favor, insira um número entre {min_val} e {max_val}.")
                except ValueError:
                    print("Por favor, insira um número válido ou 'N/A'.")

        def get_infarct_type(prompt: str) -> str:
            options = ['cortical_large', 'subcortical_small_lacunar', 'subcortical_other_size', 'none']
            while True:
                resp = input(f"{prompt} ({', '.join(options)}): ").lower()
                if resp in options:
                    return resp
                print(f"Tipo de infarto inválido. Escolha entre: {', '.join(options)}.")

        # Coleta de dados
        print("=== Fatores de Risco ===")
        data.htn = get_bool("Hipertensão (HAS)? (s/n): ")
        data.dm = get_bool("Diabetes Mellitus (DM)? (s/n): ")
        data.dlp = get_bool("Dislipidemia (DLP)? (s/n): ")
        data.smoker = get_bool("Tabagismo? (s/n): ")
        
        print("\n=== Achados de Imagem ===")
        data.stenosis = get_int("Grau de estenose arterial ipsilateral (0-100%): ")
        data.infarct_type = get_infarct_type("Tipo de infarto")
        data.leukoaraiosis = get_bool("Leucoaraiose presente? (s/n): ")
        
        print("\n=== Achados Cardíacos ===")
        data.afib = get_bool("Fibrilação atrial ou flutter atrial? (s/n): ")
        data.mech_valve = get_bool("Prótese valvar mecânica? (s/n): ")
        data.recent_mi = get_bool("Infarto do miocárdio recente (<3 meses)? (s/n): ")
        data.lvef = get_int("Fração de ejeção do VE (0-100, ou N/A se não avaliado): ", allow_none=True)
        data.thrombus = get_bool("Trombo no átrio esquerdo (AE) ou ventrículo esquerdo (VE)? (s/n): ")
        data.endocarditis = get_bool("Endocardite infecciosa? (s/n): ")
        data.pfo = get_bool("Forame oval patente (FOP)? (s/n): ")
        if data.pfo:
            data.venous_thrombosis = get_bool("Trombose venosa concomitante ao FOP (para embolia paradoxal)? (s/n): ")
        
        print("\n=== Outras Causas ===")
        data.vasculitis = get_bool("Vasculite do SNC (com achados anormais em LCR/angiografia)? (s/n): ")
        data.thrombophilia = get_bool("Trombofilia (ex: deficiência de proteína C/S) com trombo venoso/arterial? (s/n): ")
        data.other_definite_cause = get_bool("Outra causa determinada (ex: Moyamoya, Fabry)? (s/n): ")
        data.other_probable_cause = get_bool("Outra causa provável (ex: enxaqueca com aura, sem AVC durante a crise)? (s/n): ")
        
        print("\n=== Dissecção ===")
        data.dissection = get_bool("Sinais radiológicos de dissecção arterial (hematoma, flap intimal, sinal do barbante)? (s/n): ")
        if not data.dissection:
            data.dissection_history = get_bool("História clínica sugestiva de dissecção (dor cervical/cefaleia/trauma)? (s/n): ")
        
        return data
    
    def display_results(self, result: str):
        """Exibe o resultado da análise com IA"""
        print('\n' + '='*50)
        print('RESULTADOS')
        print('='*50)

        if result:
            print(result)
        else:
            print("Não foi possível obter a classificação da IA.")
        
        print('\n' + '='*50)
    
    def run_cli(self):
        """Interface principal do programa"""
        print('='*60)
        print('    Classificador ASCOD/TOAST de AVC - Versão Python')
        print('='*60)
        
        while True:
            print('\nEscolha uma opção:')
            print('1. Entrada estruturada (formulário)')
            print('2. Análise por texto com IA')
            print('3. Sair')
            
            choice = input('\nOpção: ')
            
            if choice == '1':
                data = self.collect_structured_input()
                description_from_form = data.to_natural_language()
                ai_output = self.analyze_with_ai(description_from_form)
                self.display_results(ai_output)
                
            elif choice == '2':
                print('\n--- Análise por Texto com IA ---')
                print('Descreva o caso clínico (digite END em nova linha para finalizar):\n')
                
                lines = []
                while True:
                    line = input()
                    if line.upper() == 'END':
                        break
                    lines.append(line)
                
                description = '\n'.join(lines)
                ai_output = self.analyze_with_ai(description)
                
                if ai_output:
                    print('\n=== Análise da IA ===\n')
                    print(ai_output)
                
            elif choice == '3':
                print('\nEncerrando...')
                break
                
            else:
                print('\nOpção inválida! Tente novamente.')


def main():
    """Função principal"""
    classifier = ASCODClassifier()
    classifier.run_cli()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\nPrograma interrompido pelo usuário.')
        sys.exit(0)
    except Exception as e:
        print(f'\nErro inesperado: {e}')
        sys.exit(1) 