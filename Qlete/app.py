import os
import json
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Pasta onde os arquivos JSON dos quizzes serão salvos
QUIZ_FOLDER = os.path.join(os.path.dirname(__file__), 'quizes')

# Garante que a pasta exista
if not os.path.exists(QUIZ_FOLDER):
    os.makedirs(QUIZ_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/quizzes', methods=['GET'])
def get_quizzes():
    """Lista todos os quizzes disponíveis na pasta baseado nos metadados"""
    quizzes_lista = []
    for filename in os.listdir(QUIZ_FOLDER):
        if filename.endswith('.json'):
            filepath = os.path.join(QUIZ_FOLDER, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    metadata = data.get('metadata', {})
                    quizzes_lista.append({
                        'id': filename,
                        'titulo': metadata.get('titulo', filename),
                        'tema': metadata.get('tema', 'Geral'),
                        'dificuldade': metadata.get('dificuldade', 'Média'),
                        'ano': metadata.get('ano', 'N/A')
                    })
            except Exception as e:
                print(f"Erro ao ler {filename}: {e}")
    return jsonify(quizzes_lista)

@app.route('/api/quiz/<filename>', methods=['GET'])
def get_quiz_detail(filename):
    """Retorna as perguntas de um quiz específico"""
    filepath = os.path.join(QUIZ_FOLDER, filename)
    if os.path.exists(filepath) and filename.endswith('.json'):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': 'Erro ao ler o arquivo'}), 500
    return jsonify({'error': 'Quiz não encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)