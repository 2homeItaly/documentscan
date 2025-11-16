#!/usr/bin/env python3
"""
Esempi di utilizzo programmatico del DocumentScanner
"""

from document_scanner import DocumentScanner
from pathlib import Path
import logging

# Configura logging
logging.basicConfig(level=logging.INFO)

def example_1_basic_usage():
    """Esempio 1: Utilizzo base"""
    print("\n=== Esempio 1: Utilizzo Base ===\n")

    scanner = DocumentScanner(
        output_dir="output_example1",
        grayscale=False,
        enhance=True,
        dpi=300,
        quality=95
    )

    # Processa tutte le immagini nella directory
    input_dir = Path("input")
    processed = scanner.process_batch(input_dir)

    # Crea un singolo PDF
    scanner.create_pdf(processed, output_name="documento_completo.pdf", single_pdf=True)

    print(f"✓ Processate {len(processed)} immagini")


def example_2_grayscale_separate_pdfs():
    """Esempio 2: Bianco e nero con PDF separati"""
    print("\n=== Esempio 2: B&N con PDF Separati ===\n")

    scanner = DocumentScanner(
        output_dir="output_example2",
        grayscale=True,  # Modalità scanner B&N
        enhance=True,
        dpi=600,  # Alta risoluzione
        quality=100
    )

    input_dir = Path("input")
    processed = scanner.process_batch(input_dir)

    # Crea un PDF per ogni immagine
    scanner.create_pdf(processed, single_pdf=False)

    print(f"✓ Creati {len(processed)} PDF individuali")


def example_3_single_image():
    """Esempio 3: Processing di singola immagine"""
    print("\n=== Esempio 3: Singola Immagine ===\n")

    scanner = DocumentScanner(
        output_dir="output_example3",
        grayscale=False,
        enhance=True,
        dpi=300,
        quality=95
    )

    # Processa una singola immagine
    image_path = Path("input/documento.jpg")

    if image_path.exists():
        processed = scanner.process_image(image_path)

        if processed is not None:
            # Salva come PDF
            scanner.create_pdf(
                [(image_path.stem, processed)],
                output_name=f"{image_path.stem}.pdf",
                single_pdf=True
            )
            print("✓ Immagine processata e convertita in PDF")
    else:
        print(f"⚠ Immagine non trovata: {image_path}")


def example_4_low_quality_fast():
    """Esempio 4: Processing veloce con qualità ridotta"""
    print("\n=== Esempio 4: Processing Veloce ===\n")

    scanner = DocumentScanner(
        output_dir="output_example4",
        grayscale=True,
        enhance=False,  # Disabilita enhancement per velocità
        dpi=150,  # DPI bassi per file più piccoli
        quality=75
    )

    input_dir = Path("input")
    processed = scanner.process_batch(input_dir)

    scanner.create_pdf(processed, output_name="draft.pdf", single_pdf=True)

    print(f"✓ Processing veloce completato: {len(processed)} immagini")


def example_5_high_quality_archival():
    """Esempio 5: Massima qualità per archiviazione"""
    print("\n=== Esempio 5: Qualità Archivio ===\n")

    scanner = DocumentScanner(
        output_dir="output_example5",
        grayscale=False,  # Mantieni colore
        enhance=True,
        dpi=600,  # Massima risoluzione
        quality=100  # Massima qualità
    )

    input_dir = Path("input")
    processed = scanner.process_batch(input_dir)

    scanner.create_pdf(
        processed,
        output_name="archivio_alta_qualita.pdf",
        single_pdf=True
    )

    print(f"✓ Documento archivio creato: {len(processed)} pagine @ 600 DPI")


def example_6_custom_pipeline():
    """Esempio 6: Pipeline personalizzata con controllo granulare"""
    print("\n=== Esempio 6: Pipeline Personalizzata ===\n")

    import cv2
    import numpy as np

    scanner = DocumentScanner(output_dir="output_example6")

    image_path = Path("input/documento.jpg")

    if image_path.exists():
        # Carica immagine
        img = cv2.imread(str(image_path))

        # Step 1: Rileva bordi
        contour = scanner.detect_document_contour(img)

        # Step 2: Trasformazione prospettica
        warped = scanner.four_point_transform(img, contour)

        # Step 3: Deskew
        deskewed = scanner.deskew_image(warped)

        # Step 4: Enhancement personalizzato
        enhanced = scanner.enhance_document(deskewed)

        # Step 5: Resize A4
        final = scanner.resize_to_a4(enhanced)

        # Salva risultato
        output_path = scanner.output_dir / "custom_processed.jpg"
        cv2.imwrite(str(output_path), final, [cv2.IMWRITE_JPEG_QUALITY, 95])

        print(f"✓ Pipeline personalizzata completata: {output_path}")
    else:
        print(f"⚠ Immagine non trovata: {image_path}")


def example_7_batch_with_error_handling():
    """Esempio 7: Batch processing con gestione errori avanzata"""
    print("\n=== Esempio 7: Batch con Error Handling ===\n")

    scanner = DocumentScanner(
        output_dir="output_example7",
        grayscale=True,
        dpi=300
    )

    input_dir = Path("input")

    # Lista per tracciare successi e fallimenti
    successful = []
    failed = []

    # Processa ogni file individualmente con try-except
    image_files = list(input_dir.glob("*.jpg")) + list(input_dir.glob("*.png"))

    for img_path in image_files:
        try:
            processed = scanner.process_image(img_path)
            if processed is not None:
                successful.append((img_path.stem, processed))
            else:
                failed.append(img_path.name)
        except Exception as e:
            print(f"✗ Errore con {img_path.name}: {e}")
            failed.append(img_path.name)

    # Crea PDF solo con immagini processate con successo
    if successful:
        scanner.create_pdf(successful, output_name="batch_result.pdf")

    # Report
    print(f"\n✓ Successi: {len(successful)}")
    print(f"✗ Fallimenti: {len(failed)}")
    if failed:
        print(f"  File falliti: {', '.join(failed)}")


if __name__ == "__main__":
    print("=== Esempi di Utilizzo DocumentScanner ===")
    print("\nScegli un esempio da eseguire:")
    print("1. Utilizzo base")
    print("2. Bianco e nero con PDF separati")
    print("3. Singola immagine")
    print("4. Processing veloce")
    print("5. Qualità archivio")
    print("6. Pipeline personalizzata")
    print("7. Batch con error handling")
    print("0. Esegui tutti gli esempi")

    choice = input("\nInserisci il numero (0-7): ").strip()

    examples = {
        '1': example_1_basic_usage,
        '2': example_2_grayscale_separate_pdfs,
        '3': example_3_single_image,
        '4': example_4_low_quality_fast,
        '5': example_5_high_quality_archival,
        '6': example_6_custom_pipeline,
        '7': example_7_batch_with_error_handling,
    }

    if choice == '0':
        for func in examples.values():
            func()
    elif choice in examples:
        examples[choice]()
    else:
        print("Scelta non valida")
