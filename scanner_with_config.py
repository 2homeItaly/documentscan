#!/usr/bin/env python3
"""
Document Scanner con supporto per file di configurazione JSON
Permette di utilizzare profili predefiniti per diversi tipi di documenti
"""

import json
import argparse
from pathlib import Path
from document_scanner import DocumentScanner
import logging
import sys

logger = logging.getLogger(__name__)


def load_config(config_path: Path) -> dict:
    """Carica configurazione da file JSON"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Errore caricamento config: {e}")
        sys.exit(1)


def list_profiles(config: dict):
    """Mostra tutti i profili disponibili"""
    print("\n=== Profili Disponibili ===\n")
    for name, profile in config['profiles'].items():
        print(f"📋 {name}")
        print(f"   {profile['description']}")
        print(f"   DPI: {profile['dpi']} | Qualità: {profile['quality']} | B&N: {profile['grayscale']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Document Scanner con supporto configurazione JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:

  # Usa profilo default
  python scanner_with_config.py -i ./input --profile default

  # Usa profilo per fatture
  python scanner_with_config.py -i ./fatture --profile invoices

  # Lista tutti i profili disponibili
  python scanner_with_config.py --list-profiles

  # Usa configurazione personalizzata
  python scanner_with_config.py -i ./input --config my_config.json --profile custom
        """
    )

    parser.add_argument(
        '-i', '--input',
        type=str,
        help='Directory contenente le immagini da processare'
    )

    parser.add_argument(
        '-c', '--config',
        type=str,
        default='config_example.json',
        help='File di configurazione JSON (default: config_example.json)'
    )

    parser.add_argument(
        '-p', '--profile',
        type=str,
        default='default',
        help='Profilo da utilizzare (default: default)'
    )

    parser.add_argument(
        '--list-profiles',
        action='store_true',
        help='Mostra tutti i profili disponibili e esci'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Output verboso'
    )

    args = parser.parse_args()

    # Configura logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Carica configurazione
    config_path = Path(args.config)
    if not config_path.exists():
        logger.error(f"File di configurazione non trovato: {config_path}")
        sys.exit(1)

    config = load_config(config_path)

    # Se richiesto, mostra profili e esci
    if args.list_profiles:
        list_profiles(config)
        return

    # Verifica input directory
    if not args.input:
        logger.error("Specifica una directory input con -i/--input")
        parser.print_help()
        sys.exit(1)

    input_dir = Path(args.input)
    if not input_dir.exists():
        logger.error(f"Directory input non trovata: {input_dir}")
        sys.exit(1)

    # Verifica profilo
    if args.profile not in config['profiles']:
        logger.error(f"Profilo '{args.profile}' non trovato nel file di configurazione")
        logger.info(f"Profili disponibili: {', '.join(config['profiles'].keys())}")
        sys.exit(1)

    # Carica profilo
    profile = config['profiles'][args.profile]

    logger.info("=== Document Scanner con Configurazione ===")
    logger.info(f"Profilo: {args.profile}")
    logger.info(f"Descrizione: {profile['description']}")
    logger.info(f"Input: {input_dir}")
    logger.info(f"Output: {profile['output_dir']}")

    # Inizializza scanner con parametri del profilo
    scanner = DocumentScanner(
        output_dir=profile['output_dir'],
        grayscale=profile['grayscale'],
        enhance=profile['enhance'],
        dpi=profile['dpi'],
        quality=profile['quality']
    )

    # Processa batch
    from datetime import datetime
    start_time = datetime.now()

    processed_images = scanner.process_batch(
        input_dir,
        image_extensions=config.get('image_extensions', ['.jpg', '.jpeg', '.png'])
    )

    # Crea PDF
    if processed_images:
        pdf_config = profile.get('pdf', {})
        single_pdf = pdf_config.get('single_pdf', True)
        pdf_name = pdf_config.get('pdf_name', 'output.pdf')

        scanner.create_pdf(
            processed_images,
            output_name=pdf_name,
            single_pdf=single_pdf
        )

    # Report finale
    duration = (datetime.now() - start_time).total_seconds()
    logger.info("=== Processing Completato ===")
    logger.info(f"Profilo utilizzato: {args.profile}")
    logger.info(f"Immagini processate: {len(processed_images)}")
    logger.info(f"Tempo impiegato: {duration:.2f}s")
    logger.info(f"Output salvato in: {Path(profile['output_dir']).absolute()}")


if __name__ == "__main__":
    main()
