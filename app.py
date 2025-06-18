#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Flask para o Classificador ASCOD/TOAST
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys
from dataclasses import asdict
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

# Instância global do classificador
classifier = ASCODClassifier()

@app.route('/')
def index():
    """Serve a página principal"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Endpoint para análise com IA"""
    try:
        data = request.json
        
        if data.get('type') == 'text':
            # Análise por texto livre
            clinical_text = data.get('text', '')
            if not clinical_text:
                return jsonify({'error': 'Texto clínico não fornecido'}), 400
            
            result = classifier.analyze_with_ai(clinical_text)
            
        elif data.get('type') == 'structured':
            # Análise por dados estruturados
            patient_data = PatientData(
                htn=data.get('htn', False),
                dm=data.get('dm', False),
                dlp=data.get('dlp', False),
                smoker=data.get('smoker', False),
                stenosis=data.get('stenosis', 0),
                infarct_type=data.get('infarct_type', 'none'),
                leukoaraiosis=data.get('leukoaraiosis', False),
                afib=data.get('afib', False),
                mech_valve=data.get('mech_valve', False),
                recent_mi=data.get('recent_mi', False),
                lvef=data.get('lvef'),
                thrombus=data.get('thrombus', False),
                endocarditis=data.get('endocarditis', False),
                pfo=data.get('pfo', False),
                venous_thrombosis=data.get('venous_thrombosis', False),
                vasculitis=data.get('vasculitis', False),
                thrombophilia=data.get('thrombophilia', False),
                other_definite_cause=data.get('other_definite_cause', False),
                other_probable_cause=data.get('other_probable_cause', False),
                dissection=data.get('dissection', False),
                dissection_history=data.get('dissection_history', False)
            )
            
            # Converte para linguagem natural e analisa
            clinical_text = patient_data.to_natural_language()
            result = classifier.analyze_with_ai(clinical_text)
            
        else:
            return jsonify({'error': 'Tipo de análise não especificado'}), 400
        
        if result:
            # Extrai as classificações do resultado
            ascod_code = extract_ascod_code(result)
            toast_code = extract_toast_code(result)
            
            return jsonify({
                'success': True,
                'result': result,
                'ascod_code': ascod_code,
                'toast_code': toast_code,
                'clinical_text': clinical_text if data.get('type') == 'structured' else None
            })
        else:
            return jsonify({'error': 'Falha na análise com IA'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_ascod_code(text):
    """Extrai o código ASCOD do resultado"""
    import re
    match = re.search(r'A(\d)-S(\d)-C(\d)-O(\d)-D(\d)', text)
    if match:
        return f"A{match.group(1)}-S{match.group(2)}-C{match.group(3)}-O{match.group(4)}-D{match.group(5)}"
    return None

def extract_toast_code(text):
    """Extrai o código TOAST do resultado"""
    import re
    match = re.search(r'TOAST\s+(\d+[ab]?)', text, re.IGNORECASE)
    if match:
        return f"TOAST {match.group(1)}"
    return None

if __name__ == '__main__':
    # Cria diretório templates se não existir
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True, port=5000) 