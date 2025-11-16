#!/usr/bin/env python3
"""
Document Scanner - Web Interface
Interfaccia web user-friendly per il Document Scanner
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
from pathlib import Path
from document_scanner import DocumentScanner
import logging
import shutil
from datetime import datetime
import json
import zipfile
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'web_output'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Crea directory necessarie
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}


def allowed_file(filename):
    """Verifica se il file ha un'estensione permessa"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_old_files():
    """Pulisce i file più vecchi di 1 ora"""
    try:
        now = datetime.now().timestamp()
        for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
            for file_path in Path(folder).glob('*'):
                if file_path.is_file():
                    if now - file_path.stat().st_mtime > 3600:  # 1 ora
                        file_path.unlink()
    except Exception as e:
        logger.error(f"Errore cleanup: {e}")


@app.route('/')
def index():
    """Pagina principale"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    """Gestisce l'upload dei file"""
    try:
        cleanup_old_files()

        if 'files[]' not in request.files:
            return jsonify({'error': 'Nessun file caricato'}), 400

        files = request.files.getlist('files[]')

        if not files or files[0].filename == '':
            return jsonify({'error': 'Nessun file selezionato'}), 400

        uploaded_files = []
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        session_folder = Path(app.config['UPLOAD_FOLDER']) / session_id
        session_folder.mkdir(exist_ok=True)

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = session_folder / filename
                file.save(str(filepath))
                uploaded_files.append({
                    'name': filename,
                    'path': str(filepath),
                    'size': os.path.getsize(filepath)
                })

        return jsonify({
            'success': True,
            'session_id': session_id,
            'files': uploaded_files,
            'count': len(uploaded_files)
        })

    except Exception as e:
        logger.error(f"Errore upload: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/process', methods=['POST'])
def process_documents():
    """Processa i documenti caricati"""
    try:
        data = request.json
        session_id = data.get('session_id')

        # Parametri di processing
        params = data.get('params', {})
        grayscale = params.get('grayscale', False)
        dpi = int(params.get('dpi', 300))
        quality = int(params.get('quality', 95))
        single_pdf = params.get('single_pdf', True)
        pdf_name = params.get('pdf_name', 'scanned_document.pdf')

        # Percorsi
        input_folder = Path(app.config['UPLOAD_FOLDER']) / session_id
        output_folder = Path(app.config['OUTPUT_FOLDER']) / session_id
        output_folder.mkdir(exist_ok=True)

        if not input_folder.exists():
            return jsonify({'error': 'Sessione non trovata'}), 404

        # Inizializza scanner
        scanner = DocumentScanner(
            output_dir=str(output_folder),
            grayscale=grayscale,
            enhance=True,
            dpi=dpi,
            quality=quality
        )

        # Processa batch
        processed_images = scanner.process_batch(input_folder)

        if not processed_images:
            return jsonify({'error': 'Nessuna immagine processata con successo'}), 400

        # Crea PDF
        scanner.create_pdf(
            processed_images,
            output_name=pdf_name,
            single_pdf=single_pdf
        )

        # Prepara informazioni sui file di output
        output_files = []
        for file_path in output_folder.glob('*'):
            if file_path.is_file():
                output_files.append({
                    'name': file_path.name,
                    'size': file_path.stat().st_size,
                    'type': 'pdf' if file_path.suffix == '.pdf' else 'image'
                })

        return jsonify({
            'success': True,
            'session_id': session_id,
            'processed_count': len(processed_images),
            'output_files': output_files
        })

    except Exception as e:
        logger.error(f"Errore processing: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/preview/<session_id>/<filename>')
def preview_image(session_id, filename):
    """Mostra preview dell'immagine processata"""
    try:
        output_folder = Path(app.config['OUTPUT_FOLDER']) / session_id
        file_path = output_folder / filename

        if not file_path.exists() or file_path.suffix.lower() == '.pdf':
            return jsonify({'error': 'File non trovato'}), 404

        return send_file(str(file_path), mimetype='image/jpeg')

    except Exception as e:
        logger.error(f"Errore preview: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/download/<session_id>/<filename>')
def download_file(session_id, filename):
    """Download di un singolo file"""
    try:
        output_folder = Path(app.config['OUTPUT_FOLDER']) / session_id
        file_path = output_folder / filename

        if not file_path.exists():
            return jsonify({'error': 'File non trovato'}), 404

        mimetype = 'application/pdf' if file_path.suffix == '.pdf' else 'image/jpeg'
        return send_file(str(file_path), mimetype=mimetype, as_attachment=True)

    except Exception as e:
        logger.error(f"Errore download: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/download-all/<session_id>')
def download_all(session_id):
    """Download di tutti i file come ZIP"""
    try:
        output_folder = Path(app.config['OUTPUT_FOLDER']) / session_id

        if not output_folder.exists():
            return jsonify({'error': 'Sessione non trovata'}), 404

        # Crea ZIP in memoria
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in output_folder.glob('*'):
                if file_path.is_file():
                    zf.write(file_path, file_path.name)

        memory_file.seek(0)

        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'scanned_documents_{session_id}.zip'
        )

    except Exception as e:
        logger.error(f"Errore download ZIP: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/config-profiles')
def get_config_profiles():
    """Restituisce i profili di configurazione disponibili"""
    try:
        config_path = Path('config_example.json')
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                return jsonify(config.get('profiles', {}))
        else:
            return jsonify({
                'default': {
                    'description': 'Configurazione standard',
                    'grayscale': False,
                    'dpi': 300,
                    'quality': 95
                },
                'high_quality': {
                    'description': 'Massima qualità',
                    'grayscale': False,
                    'dpi': 600,
                    'quality': 100
                },
                'bw_scanner': {
                    'description': 'Bianco e nero',
                    'grayscale': True,
                    'dpi': 300,
                    'quality': 95
                }
            })
    except Exception as e:
        logger.error(f"Errore caricamento profili: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve i file statici"""
    return send_from_directory('static', filename)


if __name__ == '__main__':
    print("=" * 60)
    print("  Document Scanner - Web Interface")
    print("=" * 60)
    print("\n🌐 Server in esecuzione su: http://localhost:5000")
    print("\n📝 Apri il browser e vai a: http://localhost:5000")
    print("\n🛑 Premi CTRL+C per fermare il server\n")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
