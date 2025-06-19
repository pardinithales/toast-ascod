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

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuração da API Gemini usando variável de ambiente
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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
    """Endpoint para análise com IA"""
    try:
        data = request.json
        classifier = get_classifier()
        
        if data.get('type') == 'text':
            clinical_text = data.get('text', '')
            if not clinical_text:
                return jsonify({'error': 'Texto clínico não fornecido'}), 400
            result_json_str = classifier.analyze_with_ai(clinical_text)
        
        elif data.get('type') == 'structured':
            known_fields = {f.name for f in fields(PatientData)}
            patient_data_args = {k: v for k, v in data.items() if k in known_fields}
            
            # Converte valores numéricos que podem vir como strings vazias
            for field in ['stenosis', 'lvef']:
                if field in patient_data_args and patient_data_args[field] == '':
                    patient_data_args[field] = None
            
            patient_data = PatientData(**patient_data_args)
            clinical_text = patient_data.to_natural_language()
            result_json_str = classifier.analyze_with_ai(clinical_text)
            
        else:
            return jsonify({'error': 'Tipo de análise não especificado'}), 400
        
        if result_json_str:
            # Tenta carregar o JSON e extrair os códigos
            result_data = json.loads(result_json_str)
            ascod_grades = [str(result_data['ascod'][letter]['grade']) for letter in 'ASCOD']
            ascod_code = f"A{ascod_grades[0]}-S{ascod_grades[1]}-C{ascod_grades[2]}-O{ascod_grades[3]}-D{ascod_grades[4]}"
            toast_code = f"TOAST {result_data['toast']['classification']}"

            return jsonify({
                'success': True,
                'result': result_data, # Envia o objeto JSON parseado
                'ascod_code': ascod_code,
                'toast_code': toast_code,
                'clinical_text': clinical_text
            })
        else:
            return jsonify({'error': 'Falha na análise com IA'}), 500
            
    except json.JSONDecodeError:
        return jsonify({'error': 'A resposta da IA não é um JSON válido.', 'raw_response': result_json_str}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Cria diretório templates se não existir
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True, port=int(os.getenv("PORT", 5000))) 