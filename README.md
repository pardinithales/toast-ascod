# Classificador ASCOD/TOAST - Sistema de Análise de AVC com IA

Sistema avançado para classificação etiológica de AVC isquêmico utilizando os critérios ASCOD e TOAST, com suporte de Inteligência Artificial (Google Gemini).

## 🚀 Características

- **Interface Web Moderna**: Design responsivo e intuitivo
- **Duas Modalidades de Entrada**:
  - Formulário estruturado com campos específicos
  - Entrada de texto livre para análise direta
- **Análise com IA**: Integração com Google Gemini para classificação precisa
- **Visualização Rica**: Resultados apresentados em cards interativos
- **API REST**: Backend Flask para fácil integração

## 📋 Pré-requisitos

- Python 3.8+
- Chave de API do Google Gemini
- Git (para deploy)

## 🔧 Instalação Local

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/ascod-toast-classifier.git
cd ascod-toast-classifier
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
# Windows
set GEMINI_API_KEY=sua_chave_api_aqui
# Linux/Mac
export GEMINI_API_KEY=sua_chave_api_aqui
```

5. Execute a aplicação:
```bash
python app.py
```

Acesse: `http://localhost:5000`

## 🌐 Deploy no Render

### Passo 1: Prepare o código

1. Crie um repositório no GitHub
2. Faça commit de todos os arquivos:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/seu-usuario/ascod-toast-classifier.git
git push -u origin main
```

### Passo 2: Configure no Render

1. Acesse [render.com](https://render.com) e crie uma conta
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório GitHub
4. Configure:
   - **Name**: ascod-toast-classifier
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### Passo 3: Variáveis de Ambiente

No painel do Render, adicione:
- `GEMINI_API_KEY`: Sua chave API do Google Gemini
- `PYTHON_VERSION`: 3.11.7

### Passo 4: Deploy

Clique em "Create Web Service" e aguarde o deploy!

## 🐳 Deploy com Docker (Alternativa)

1. Crie um `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

2. Build e execute:
```bash
docker build -t ascod-classifier .
docker run -p 5000:5000 -e GEMINI_API_KEY=sua_chave ascod-classifier
```

## 🚀 Deploy no Vercel (Alternativa Rápida)

1. Instale Vercel CLI:
```bash
npm i -g vercel
```

2. Crie `vercel.json`:
```json
{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

3. Deploy:
```bash
vercel
```

## 📦 Criando Executável Standalone (Windows)

Para criar um executável `.exe`:

1. Instale PyInstaller:
```bash
pip install pyinstaller
```

2. Crie o executável:
```bash
pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" --hidden-import flask app.py
```

3. O executável estará em `dist/app.exe`

## 🔑 Obtendo Chave API Gemini

1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Clique em "Create API Key"
3. Copie a chave gerada

## 📊 Uso da Aplicação

### Entrada Estruturada
1. Preencha os campos do formulário
2. Clique em "Analisar com IA"
3. Visualize os resultados

### Entrada de Texto Livre
1. Cole a descrição clínica completa
2. Clique em "Analisar com IA"
3. Visualize os resultados

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python, Flask, Flask-CORS
- **Frontend**: HTML5, CSS3, JavaScript
- **IA**: Google Gemini API
- **Deploy**: Render/Heroku/Vercel

## 📝 Licença

Este projeto está sob a licença MIT.

## 👥 Contribuição

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no GitHub. 