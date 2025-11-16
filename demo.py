#!/usr/bin/env python3
"""
Demo Script - Genera documenti sintetici e li processa
Dimostra le capacità del Document Scanner senza bisogno di foto reali
"""

import cv2
import numpy as np
from pathlib import Path
from document_scanner import DocumentScanner
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_synthetic_document(width=3000, height=4000, rotation_angle=15, perspective=True):
    """
    Crea un documento A4 sintetico con prospettiva e rotazione

    Args:
        width: Larghezza immagine
        height: Altezza immagine
        rotation_angle: Angolo di rotazione in gradi
        perspective: Se True, applica distorsione prospettica

    Returns:
        Immagine numpy array
    """
    # Crea sfondo (tavolo/scrivania)
    background = np.random.randint(40, 80, (height, width, 3), dtype=np.uint8)

    # Aggiungi texture legno al background
    for i in range(0, height, 20):
        color_variation = np.random.randint(-10, 10)
        background[i:i+10, :] = np.clip(background[i:i+10, :] + color_variation, 0, 255)

    # Crea documento A4 bianco
    doc_width = int(width * 0.6)
    doc_height = int(doc_width * 1.414)  # Rapporto A4

    document = np.ones((doc_height, doc_width, 3), dtype=np.uint8) * 255

    # Aggiungi contenuto al documento
    # Header
    cv2.rectangle(document, (50, 50), (doc_width-50, 150), (200, 220, 255), -1)
    cv2.putText(document, "DOCUMENTO UFFICIALE", (100, 120),
                cv2.FONT_HERSHEY_BOLD, 2.5, (50, 50, 50), 4)

    # Sottotitolo
    cv2.putText(document, "Test Document Scanner Pipeline", (100, 250),
                cv2.FONT_HERSHEY_SIMPLEX, 1.8, (80, 80, 80), 3)

    # Linee di testo simulate
    y_position = 400
    line_spacing = 80
    for i in range(15):
        # Linea di "testo"
        line_width = np.random.randint(doc_width-200, doc_width-100)
        cv2.line(document, (100, y_position), (line_width, y_position), (50, 50, 50), 3)

        # Occasionalmente aggiungi una parola evidenziata
        if i % 4 == 0:
            cv2.rectangle(document, (120, y_position-25), (400, y_position+10),
                         (100, 255, 255), -1)
            cv2.line(document, (120, y_position), (400, y_position), (50, 50, 50), 3)

        y_position += line_spacing

    # Box informazioni
    cv2.rectangle(document, (100, doc_height-400), (doc_width-100, doc_height-100),
                 (230, 230, 230), -1)
    cv2.rectangle(document, (100, doc_height-400), (doc_width-100, doc_height-100),
                 (100, 100, 100), 3)
    cv2.putText(document, "Data: 16/11/2025", (150, doc_height-300),
                cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 2)
    cv2.putText(document, "ID: DOC-2024-001", (150, doc_height-220),
                cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 2)

    # Firma simulata
    cv2.putText(document, "Firma: _____________", (150, doc_height-140),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)

    # Aggiungi ombra al documento (simulazione foto reale)
    shadow = document.copy()
    shadow_offset = 20
    shadow = cv2.GaussianBlur(shadow, (21, 21), 0)
    shadow = (shadow * 0.3).astype(np.uint8)

    # Calcola posizione centrale nel background
    y_offset = (height - doc_height) // 2
    x_offset = (width - doc_width) // 2

    if perspective:
        # Applica distorsione prospettica (simula foto angolata)
        pts_src = np.float32([
            [0, 0],
            [doc_width, 0],
            [doc_width, doc_height],
            [0, doc_height]
        ])

        # Punti di destinazione con prospettiva
        offset_tl = np.random.randint(-100, 50)
        offset_tr = np.random.randint(-50, 100)
        offset_br = np.random.randint(-50, 100)
        offset_bl = np.random.randint(-100, 50)

        pts_dst = np.float32([
            [x_offset + offset_tl, y_offset + offset_tl],
            [x_offset + doc_width + offset_tr, y_offset + offset_tr],
            [x_offset + doc_width + offset_br, y_offset + doc_height + offset_br],
            [x_offset + offset_bl, y_offset + doc_height + offset_bl]
        ])

        # Applica trasformazione prospettica
        M = cv2.getPerspectiveTransform(pts_src, pts_dst)
        warped = cv2.warpPerspective(document, M, (width, height),
                                     borderMode=cv2.BORDER_CONSTANT,
                                     borderValue=(0, 0, 0))

        # Crea mask per il documento
        mask = np.zeros((height, width), dtype=np.uint8)
        mask_warped = cv2.warpPerspective(np.ones((doc_height, doc_width), dtype=np.uint8) * 255,
                                         M, (width, height))

        # Combina con background
        result = background.copy()
        result[mask_warped > 0] = warped[mask_warped > 0]

    else:
        # Senza prospettiva, solo posizionamento centrale
        result = background.copy()
        result[y_offset:y_offset+doc_height, x_offset:x_offset+doc_width] = document

    # Aggiungi rumore fotografico
    noise = np.random.normal(0, 3, result.shape).astype(np.int16)
    result = np.clip(result.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Simula variazioni di illuminazione
    for i in range(5):
        center_x = np.random.randint(0, width)
        center_y = np.random.randint(0, height)
        brightness = np.random.randint(-15, 15)

        Y, X = np.ogrid[:height, :width]
        dist = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
        mask_illum = np.clip(1 - dist / (width * 0.3), 0, 1)

        for c in range(3):
            result[:, :, c] = np.clip(result[:, :, c] + brightness * mask_illum, 0, 255)

    return result


def run_demo():
    """Esegue la demo completa"""
    logger.info("=" * 60)
    logger.info("DOCUMENT SCANNER - DEMO")
    logger.info("=" * 60)

    # Crea directory
    demo_input = Path("demo_input")
    demo_output = Path("demo_output")
    demo_input.mkdir(exist_ok=True)
    demo_output.mkdir(exist_ok=True)

    logger.info("\n[1/4] Generazione documenti sintetici...")

    # Genera diversi documenti di esempio
    documents = [
        ("doc_with_perspective.jpg", True, 15),
        ("doc_rotated.jpg", False, 10),
        ("doc_slight_rotation.jpg", True, 5),
    ]

    for filename, perspective, rotation in documents:
        logger.info(f"  Creazione: {filename}")
        doc = create_synthetic_document(
            width=2000,
            height=2800,
            rotation_angle=rotation,
            perspective=perspective
        )
        cv2.imwrite(str(demo_input / filename), doc)

    logger.info(f"\n✓ Creati {len(documents)} documenti sintetici in {demo_input}/")

    logger.info("\n[2/4] Processing con modalità colore...")

    # Scanner modalità colore
    scanner_color = DocumentScanner(
        output_dir=str(demo_output / "color"),
        grayscale=False,
        dpi=300,
        quality=95
    )

    processed_color = scanner_color.process_batch(demo_input)
    scanner_color.create_pdf(processed_color, output_name="documenti_colore.pdf")

    logger.info(f"✓ Processati {len(processed_color)} documenti (colore)")

    logger.info("\n[3/4] Processing con modalità bianco e nero...")

    # Scanner modalità B&N
    scanner_bw = DocumentScanner(
        output_dir=str(demo_output / "bw"),
        grayscale=True,
        dpi=300,
        quality=95
    )

    processed_bw = scanner_bw.process_batch(demo_input)
    scanner_bw.create_pdf(processed_bw, output_name="documenti_bw.pdf")

    logger.info(f"✓ Processati {len(processed_bw)} documenti (B&N)")

    logger.info("\n[4/4] Processing con alta qualità...")

    # Scanner alta qualità
    scanner_hq = DocumentScanner(
        output_dir=str(demo_output / "high_quality"),
        grayscale=False,
        dpi=600,
        quality=100
    )

    processed_hq = scanner_hq.process_batch(demo_input)
    scanner_hq.create_pdf(processed_hq, output_name="documenti_alta_qualita.pdf")

    logger.info(f"✓ Processati {len(processed_hq)} documenti (alta qualità)")

    # Report finale
    logger.info("\n" + "=" * 60)
    logger.info("DEMO COMPLETATA!")
    logger.info("=" * 60)
    logger.info(f"\n📁 Input generati in: {demo_input.absolute()}")
    logger.info(f"📁 Output salvati in: {demo_output.absolute()}")
    logger.info("\nDirectory output:")
    logger.info(f"  • {demo_output / 'color'}/          - Documenti a colori")
    logger.info(f"  • {demo_output / 'bw'}/             - Documenti bianco e nero")
    logger.info(f"  • {demo_output / 'high_quality'}/   - Documenti alta qualità (600 DPI)")

    logger.info("\nPDF generati:")
    for pdf_dir in ['color', 'bw', 'high_quality']:
        pdf_files = list((demo_output / pdf_dir).glob("*.pdf"))
        for pdf in pdf_files:
            size_mb = pdf.stat().st_size / (1024 * 1024)
            logger.info(f"  • {pdf.name} ({size_mb:.2f} MB)")

    logger.info("\n✅ Confronta i risultati per vedere la differenza!")
    logger.info("💡 Suggerimento: Apri i PDF per vedere la qualità del processing")


if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        logger.info("\n\nDemo interrotta dall'utente")
    except Exception as e:
        logger.error(f"\n\nErrore durante la demo: {e}")
        import traceback
        traceback.print_exc()
