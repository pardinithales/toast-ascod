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