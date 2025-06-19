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
from dataclasses import dataclass, asdict, fields
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dotenv import load_dotenv
import google.generativeai as genai

# Carrega variáveis de ambiente
load_dotenv()

# Configuração da API Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("⚠️  AVISO: Variável de ambiente GEMINI_API_KEY não configurada!")
    print("   Configure a chave da API no arquivo .env ou como variável de ambiente.")
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
    """Estrutura para os dados do paciente, alinhada com o formulário completo e revisado."""
    # A - Aterosclerose
    stenosis: Optional[int] = 0
    a1_stenosis_lt_50_thrombus: bool = False
    a1_aortic_mobile_thrombus: bool = False
    a2_aortic_plaque_ge_4mm: bool = False
    a3_history_mi_pad: bool = False

    # S - Doença de Pequenos Vasos
    infarct_type: str = 'none'
    s_has_htn_or_dm: bool = False # Adicionado para critério S1
    s1_lacunar_infarct_syndrome: bool = False
    s1_lacunar_plus_severe_leuko: bool = False
    s3_severe_leuko_isolated: bool = False
    
    # C - Cardiopatia
    lvef: Optional[int] = None
    c1_afib_documented: bool = False
    c1_mechanical_valve: bool = False
    c1_mural_thrombus: bool = False
    c1_recent_mi: bool = False # Adicionado: IAM < 3 meses
    c1_infective_endocarditis: bool = False # Adicionado
    c1_cardiomyopathy: bool = False # Adicionado
    c1_intracardiac_mass: bool = False # Adicionado
    c1_mitral_stenosis: bool = False # Adicionado
    c1_pfo_pe_dvt: bool = False
    c2_pfo_asa: bool = False
    c3_pfo_isolated: bool = False

    # O - Outras Causas
    o1_antiphospholipid: bool = False
    o1_other_angiitis: bool = False
    o3_malignancy: bool = False
    
    # D - Dissecção
    d1_direct: bool = False
    d2_weak_evidence: bool = False

    def to_natural_language(self):
        """Gera um texto em linguagem natural a partir dos dados estruturados."""
        parts = []

        # Aterosclerose (A)
        a_parts = []
        if self.stenosis is not None:
            if self.stenosis >= 50:
                a_parts.append(f"Estenose arterial ipsilateral de {self.stenosis}% (sugestivo de A1)")
            elif 30 <= self.stenosis < 50:
                a_parts.append(f"Estenose arterial ipsilateral de {self.stenosis}% (sugestivo de A2)")
            elif self.stenosis > 0:
                 a_parts.append(f"Estenose arterial ipsilateral de {self.stenosis}% (sugestivo de A3)")
        
        if self.a1_stenosis_lt_50_thrombus: a_parts.append("Estenose <50% com trombo luminal (A1)")
        if self.a1_aortic_mobile_thrombus: a_parts.append("Trombo móvel no arco aórtico (A1)")
        if self.a2_aortic_plaque_ge_4mm: a_parts.append("Placa aórtica >=4mm sem componente móvel (A2)")
        if self.a3_history_mi_pad: a_parts.append("História de IAM ou Doença Arterial Periférica (A3)")
        if a_parts: parts.append(f"Aterosclerose: {'; '.join(a_parts)}.")

        # Doença de Pequenos Vasos (S)
        s_parts = []
        if self.infarct_type == 'subcortical_small_lacunar':
            s_parts.append("Infarto subcortical lacunar <1.5cm (sugestivo de S1)")
            if self.s_has_htn_or_dm:
                s_parts.append("em paciente com HAS ou DM")
        elif self.infarct_type == 'cortical_large':
             s_parts.append("Infarto cortical ou >1.5cm (geralmente não relacionado a pequenos vasos)")
        
        if self.s1_lacunar_infarct_syndrome: s_parts.append("Apresentou síndrome lacunar clínica clássica (S1)")
        if self.s1_lacunar_plus_severe_leuko: s_parts.append("Associado a leucoaraiose grave / Fazekas III (S1)")
        if self.s3_severe_leuko_isolated: s_parts.append("Leucoaraiose grave isolada (S3)")
        if s_parts: parts.append(f"Pequenos Vasos: {'; '.join(s_parts)}.")

        # Cardiopatia (C)
        c_parts = []
        if self.lvef is not None and self.lvef < 35:
            c_parts.append(f"Fração de Ejeção de {self.lvef}% (sugestivo de C1)")
        if self.c1_afib_documented: c_parts.append("FA/Flutter documentado (C1)")
        if self.c1_mechanical_valve: c_parts.append("Prótese valvar mecânica (C1)")
        if self.c1_mural_thrombus: c_parts.append("Trombo mural em cavidades esquerdas (C1)")
        if self.c1_recent_mi: c_parts.append("Infarto do Miocárdio recente < 3 meses (C1)")
        if self.c1_infective_endocarditis: c_parts.append("Endocardite infecciosa (C1)")
        if self.c1_cardiomyopathy: c_parts.append("Cardiomiopatia dilatada (C1)")
        if self.c1_intracardiac_mass: c_parts.append("Massa intracardíaca, como mixoma (C1)")
        if self.c1_mitral_stenosis: c_parts.append("Estenose mitral reumática (C1)")
        if self.c1_pfo_pe_dvt: c_parts.append("FOP com TEP/TVP prévio (C1)")
        if self.c2_pfo_asa: c_parts.append("FOP com Aneurisma de Septo Atrial (C2)")
        if self.c3_pfo_isolated: c_parts.append("FOP isolado (C3)")
        if c_parts: parts.append(f"Cardiopatia: {'; '.join(c_parts)}.")

        # Outras Causas (O)
        o_parts = []
        if self.o1_antiphospholipid: o_parts.append("Sd. Antifosfolípide (O1)")
        if self.o1_other_angiitis: o_parts.append("Vasculite / Angiite (O1)")
        if self.o3_malignancy: o_parts.append("Malignidade com hipercoagulação (O3)")
        if o_parts: parts.append(f"Outras Causas: {'; '.join(o_parts)}.")

        # Dissecção (D)
        d_parts = []
        if self.d1_direct: d_parts.append("Demonstração direta de hematoma mural (D1)")
        if self.d2_weak_evidence: d_parts.append("Evidência fraca de dissecção (clínica, Horner) (D2)")
        if d_parts: parts.append(f"Dissecção: {'; '.join(d_parts)}.")
        
        if not parts:
            return "Nenhuma informação clínica fornecida."
        return "Resumo clínico do paciente: " + " ".join(parts)


class ASCODClassifier:
    """Encapsula a lógica de classificação usando a API Gemini."""
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("API key for Gemini not found. Please set the GEMINI_API_KEY environment variable.")
        genai.configure(api_key=self.api_key)
        # O modelo exato pode ser ajustado conforme necessário
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def analyze_with_ai(self, text):
        """
        Analisa o texto clínico e retorna a classificação em formato JSON.
        """
        # Prompt otimizado para extrair JSON diretamente
        prompt = f"""
        Analise o seguinte resumo clínico e determine as classificações ASCOD e TOAST.
        Resumo: "{text}"
        Responda APENAS com um objeto JSON válido, sem nenhum texto ou formatação adicional (como ```json).
        A estrutura do JSON deve ser:
        {{
          "ascod": {{
            "A": {{"grade": <integer_value>, "justification": "..."}},
            "S": {{"grade": <integer_value>, "justification": "..."}},
            "C": {{"grade": <integer_value>, "justification": "..."}},
            "O": {{"grade": <integer_value>, "justification": "..."}},
            "D": {{"grade": <integer_value>, "justification": "..."}}
          }},
          "toast": {{
            "classification": "<string_value>",
            "justification": "..."
          }}
        }}
        """
        try:
            # Configuração para garantir saída JSON
            generation_config = genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
            response = self.model.generate_content(prompt, generation_config=generation_config)
            
            # A resposta já deve ser um JSON bem-formatado
            return response.text
            
        except Exception as e:
            print(f"Error during AI analysis: {e}")
            # Em caso de erro, retorna um JSON de erro para consistência
            error_response = {
                "error": "Failed to get a valid response from AI model.",
                "details": str(e)
            }
            return json.dumps(error_response) 