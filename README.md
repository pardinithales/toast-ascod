# 🧠 Classificador ASCOD/TOAST para AVC com IA

Sistema inteligente para classificação etiológica de Acidente Vascular Cerebral (AVC) utilizando os critérios ASCOD e TOAST, com suporte de Inteligência Artificial via Google Gemini.

## 🚀 Funcionalidades

- **Classificação ASCOD**: Análise detalhada em 5 categorias (Aterosclerose, Small-vessel, Cardiopatia, Outras causas, Dissecção)
- **Classificação TOAST**: Determinação do subtipo etiológico do AVC
- **Interface Web Moderna**: Design responsivo e intuitivo
- **Análise com IA**: Integração com Google Gemini para análise de casos clínicos
- **Múltiplos Formatos**: Entrada estruturada ou texto livre

## 🔧 Configuração das Variáveis de Ambiente

### ⚠️ IMPORTANTE: Configuração da API Gemini

Este projeto requer uma chave da API Google Gemini para funcionar. **NÃO** incluímos chaves hardcoded por segurança.

#### 1. Obter Chave da API Gemini
1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crie uma nova chave de API
3. Copie a chave gerada

#### 2. Configurar Variáveis de Ambiente

**Opção A: Arquivo .env (Recomendado para desenvolvimento)**
```bash
# Copie o arquivo de exemplo
cp env.example .env

# Edite o arquivo .env e adicione sua chave
GEMINI_API_KEY=sua_chave_aqui
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

**Opção B: Variáveis de Sistema (Para produção)**
```bash
export GEMINI_API_KEY=sua_chave_aqui
export FLASK_ENV=production
export FLASK_DEBUG=False
```

**Opção C: Arquivo config.env (Alternativa)**
```bash
# Use o arquivo config.env já criado
# Edite e adicione sua chave da API
```

## 🏃‍♂️ Como Executar

### Pré-requisitos
- Python 3.8+
- pip

### Instalação
```bash
# Clone o repositório
git clone https://github.com/pardinithales/toast-ascod.git
cd toast-ascod

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente (veja seção acima)
cp env.example .env
# Edite o .env com sua chave da API

# Execute a aplicação
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

### Versão CLI (Python)
```bash
python ascod_classifier.py
```

## 🌐 Deploy em Produção

### Render (Recomendado)
1. Fork este repositório
2. Conecte ao [Render](https://render.com)
3. Configure as variáveis de ambiente:
   - `GEMINI_API_KEY`: Sua chave da API
   - `PYTHON_VERSION`: 3.11.0

### Vercel
```bash
# Instale a CLI do Vercel
npm i -g vercel

# Configure as variáveis de ambiente
vercel env add GEMINI_API_KEY

# Deploy
vercel --prod
```

### Docker
```bash
# Build
docker build -t toast-ascod .

# Run (com variáveis de ambiente)
docker run -p 5000:5000 -e GEMINI_API_KEY=sua_chave_aqui toast-ascod
```

### Heroku
```bash
# Configure a variável de ambiente
heroku config:set GEMINI_API_KEY=sua_chave_aqui

# Deploy
git push heroku main
```

## 📁 Estrutura do Projeto

```
toast-ascod/
├── app.py                 # Aplicação Flask principal
├── ascod_classifier.py    # Classificador CLI Python
├── templates/
│   └── index.html        # Interface web
├── static/
│   ├── css/style.css     # Estilos
│   └── js/app.js         # JavaScript
├── requirements.txt       # Dependências Python
├── Procfile              # Configuração Heroku/Render
├── Dockerfile            # Configuração Docker
├── vercel.json           # Configuração Vercel
├── env.example           # Exemplo de variáveis de ambiente
└── README.md             # Este arquivo
```

## 🔒 Segurança

- ✅ Chaves de API armazenadas em variáveis de ambiente
- ✅ Arquivos .env incluídos no .gitignore
- ✅ Validação de entrada de dados
- ✅ CORS configurado adequadamente

## 📖 Como Usar

### Interface Web
1. Acesse `http://localhost:5000`
2. Escolha entre entrada estruturada ou texto livre
3. Preencha os dados do paciente
4. Visualize as classificações ASCOD e TOAST
5. Use a IA para análise adicional

### CLI Python
1. Execute `python ascod_classifier.py`
2. Siga as instruções interativas
3. Obtenha classificação detalhada

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍⚕️ Autor

**Dr. Thales Pardini** - Neurologista
- Especialista em Neurologia Vascular
- Desenvolvedor de ferramentas médicas com IA

## ⚠️ Aviso Médico

Esta ferramenta é destinada ao **suporte à decisão clínica** e não substitui o julgamento médico profissional. Sempre confirme os resultados com avaliação clínica adequada.

---

**🔗 Links Úteis:**
- [Critérios ASCOD](https://pubmed.ncbi.nlm.nih.gov/23970794/)
- [Critérios TOAST](https://pubmed.ncbi.nlm.nih.gov/8418537/)
- [Google AI Studio](https://makersuite.google.com/)

---

⭐ **Se este projeto foi útil, deixe uma estrela no GitHub!**

# Classificador Etiológico de AVC com IA - ASCOD e TOAST

Este projeto utiliza a API do Google Gemini para classificar a etiologia de Acidentes Vasculares Cerebrais (AVCs) isquêmicos com base nos critérios ASCOD e TOAST. O sistema é projetado para auxiliar neurologistas e profissionais de saúde a analisar dados clínicos de pacientes e determinar as causas prováveis do AVC.

## Funcionalidades

- **Classificação Dupla:** Implementa tanto os critérios ASCOD (Aterosclerose, Doença de Pequenos Vasos, Cardiopatia, Outras causas, Dissecção) quanto TOAST.
- **Análise por IA:** Utiliza o modelo `gemini-2.5-pro` para interpretar resumos clínicos em texto livre ou dados estruturados.
- **Prompt Detalhado:** O sistema é guiado por um prompt robusto que contém a base de conhecimento completa dos critérios, incluindo regras para lidar com casos complexos e múltiplas etiologias.
- **Saída Estruturada:** Retorna a classificação em um formato JSON claro, com a nota e a justificativa detalhada para cada categoria.

## Exemplo de Uso e Classificação

A seguir, um exemplo real de um resumo clínico e a classificação gerada pela IA, demonstrando a precisão do sistema.

### Resumo Clínico do Paciente:

"Diabetes, chagásico com Fração de ejeção preservada, átrio esquerdo 71ml, holter com 600 ectopias atirais, aterosclerose menor 50%, lesão cortical na tomografia"

### Classificação Gerada pela IA:

**Classificação ASCOD Final:** `A2-S0-C1-O9-D9`

**Justificativa Detalhada:**

*   **A (Aterosclerose): Grau 2**
    *   **Critério(s) Atendido(s):** A2(1): Estenose <50% de uma artéria intracraniana ou extracraniana ipsilateral.
    *   **Raciocínio:** O resumo clínico informa a presença de 'aterosclerose menor 50%', o que se alinha com o critério de uma ligação causal incerta.

*   **S (Doença de Pequenos Vasos): Grau 0**
    *   **Critério(s) Atendido(s):** S0(1): Ausência de qualquer um dos achados acima em RM ou TC.
    *   **Raciocínio:** A presença de uma 'lesão cortical na tomografia' é incompatível com o padrão de infarto por doença de pequenos vasos, que se manifesta como lesões subcorticais ou no tronco cerebral com menos de 20 mm.

*   **C (Cardiopatia): Grau 1**
    *   **Critério(s) Atendido(s):** C1(11): Combinação de um padrão de infarto embólico (infarto cortical ou cerebelar >1,5 cm) com uma fonte cardíaca de risco.
    *   **Raciocínio:** O paciente apresenta uma 'lesão cortical', que é um padrão de infarto embólico. A cardiopatia chagásica com dilatação acentuada do átrio esquerdo (71ml) e ectopias atriais representa uma fonte cardíaca com potencial embólico, justificando a classificação como C1 em conjunto com o padrão do infarto.

*   **O (Outra Causa): Grau 9**
    *   **Critério(s) Atendido(s):** O9(1): Avaliação incompleta com base na suspeita clínica para excluir outras causas.
    *   **Raciocínio:** O resumo não fornece informações sobre a investigação de outras causas raras de AVC (como vasculites ou trombofilias). Portanto, a avaliação para esta categoria é considerada incompleta.

*   **D (Dissecção): Grau 9**
    *   **Critério(s) Atendido(s):** D9(1): A investigação mínima das artérias cervicais e intracranianas não foi relatada como negativa para dissecção.
    *   **Raciocínio:** O texto não especifica se foi realizada uma avaliação vascular completa para excluir dissecção (ex: Angio-TC/RM de vasos cervicais). Na ausência dessa confirmação, a avaliação para dissecção é incompleta. 