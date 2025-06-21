#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Flask para o Classificador ASCOD/TOAST
"""

from flask import Flask, request, jsonify, render_template, g
from flask_cors import CORS
import os
import sys
import re
import json
from dataclasses import fields
from ascod_classifier import ASCODClassifier, PatientData
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Optional

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app)

# Carrega a chave da API e inicializa o classificador
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("AVISO: Chave da API Gemini não encontrada. A análise por IA estará desabilitada.")
    classifier = None
else:
    try:
        classifier = ASCODClassifier(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Erro ao inicializar o classificador: {e}")
        classifier = None

def get_classifier():
    """Cria uma instância do classificador por request."""
    if 'classifier' not in g:
        g.classifier = ASCODClassifier()
    return g.classifier

@app.route('/')
def index():
    """Serve a página principal"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    if not classifier:
        return jsonify({'success': False, 'error': 'Classificador de IA não inicializado. Verifique a chave da API.'}), 500

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Requisição inválida.'}), 400

    analysis_input = ""
    natural_language_prompt = ""

    if data.get('type') == 'structured':
        # Remove o 'type' para não passar para o dataclass
        form_data = data.copy()
        form_data.pop('type', None)
        
        # Converte os valores para os tipos corretos
        for field in fields(PatientData):
            if field.name in form_data:
                # Converte strings de números para int
                if field.type == Optional[int] and isinstance(form_data[field.name], str):
                    try:
                        form_data[field.name] = int(form_data[field.name])
                    except (ValueError, TypeError):
                        form_data[field.name] = None
                # Garante que os booleanos sejam booleanos
                elif field.type == bool:
                    form_data[field.name] = str(form_data[field.name]).lower() in ['true', '1', 'on']

        try:
            patient_data = PatientData(**form_data)
            natural_language_prompt = patient_data.to_natural_language()
            analysis_input = natural_language_prompt
        except TypeError as e:
            return jsonify({'success': False, 'error': f'Dados do formulário inválidos: {e}'}), 400

    elif data.get('type') == 'text':
        analysis_input = data.get('text', '')
        natural_language_prompt = analysis_input
    
    else:
        return jsonify({'success': False, 'error': 'Tipo de análise inválido.'}), 400

    if not analysis_input:
        return jsonify({'success': False, 'error': 'Nenhuma informação para análise.'}), 400

    try:
        # A resposta da IA já é uma string JSON
        ai_response_str = classifier.analyze_with_ai(analysis_input)
        ai_result = json.loads(ai_response_str)

        # Constrói o código ASCOD e TOAST
        ascod_code = "N/A"
        toast_code = "N/A"

        if 'ascod' in ai_result:
            ascod_grades = [ai_result['ascod'].get(cat, {}).get('grade', '9') for cat in ['A', 'S', 'C', 'O', 'D']]
            ascod_code = ''.join(f"{letter}{grade}" for letter, grade in zip(['A','S','C','O','D'], ascod_grades))

        if 'toast' in ai_result:
            toast_code = ai_result['toast'].get('classification', 'Indeterminado')


        # Monta a resposta final, mesclando o resultado da IA
        final_response = {
            'success': True,
            'ascod_code': ascod_code,
            'toast_code': toast_code,
            'natural_language_prompt': natural_language_prompt,
            **ai_result  # Mescla o dicionário da IA na resposta principal
        }
        
        return jsonify(final_response)

    except json.JSONDecodeError:
        return jsonify({'success': False, 'error': 'Falha ao decodificar a resposta da IA. Resposta recebida: ' + ai_response_str}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro inesperado durante a análise: {str(e)}'}), 500

if __name__ == '__main__':
    # Cria diretório templates se não existir
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True, port=int(os.getenv("PORT", 5000))) 