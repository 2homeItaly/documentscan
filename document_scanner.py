#!/usr/bin/env python3
"""
Document Scanner Pipeline - Automated A4 Document Processing
Automatizza il processing di foto di documenti A4 scattate con smartphone
"""

import cv2
import numpy as np
import os
import argparse
from pathlib import Path
from typing import Tuple, List, Optional
import logging
from PIL import Image
from datetime import datetime
import sys

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentScanner:
    """Classe principale per il processing dei documenti"""

    # Dimensioni A4 in pixel (300 DPI)
    A4_WIDTH = 2480
    A4_HEIGHT = 3508
    A4_RATIO = 1.414

    def __init__(self,
                 output_dir: str = "processed",
                 grayscale: bool = False,
                 enhance: bool = True,
                 dpi: int = 300,
                 quality: int = 95):
        """
        Inizializza il document scanner

        Args:
            output_dir: Directory di output per i documenti processati
            grayscale: Se True, converte in bianco e nero
            enhance: Se True, applica enhancement alla leggibilità
            dpi: DPI del documento finale
            quality: Qualità JPEG (1-100)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.grayscale = grayscale
        self.enhance = enhance
        self.dpi = dpi
        self.quality = quality

        # Calcola dimensioni A4 in base al DPI
        self.a4_width = int(8.27 * dpi)  # A4 width in inches
        self.a4_height = int(11.69 * dpi)  # A4 height in inches

        logger.info(f"DocumentScanner inizializzato - A4: {self.a4_width}x{self.a4_height}px @ {dpi} DPI")

    def order_points(self, pts: np.ndarray) -> np.ndarray:
        """
        Ordina i punti in ordine: top-left, top-right, bottom-right, bottom-left

        Args:
            pts: Array di 4 punti

        Returns:
            Array ordinato di punti
        """
        rect = np.zeros((4, 2), dtype="float32")

        # Top-left avrà la somma minima, bottom-right la massima
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        # Top-right avrà la differenza minima, bottom-left la massima
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        return rect

    def detect_document_contour(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Rileva i bordi del documento nell'immagine

        Args:
            image: Immagine input

        Returns:
            Array di 4 punti che rappresentano gli angoli del documento, o None
        """
        # Ridimensiona l'immagine per processing più veloce
        ratio = image.shape[0] / 500.0
        orig = image.copy()
        image_resized = cv2.resize(image, (int(image.shape[1] / ratio), 500))

        # Converti in grayscale
        gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)

        # Applica blur per ridurre il rumore
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Applica edge detection
        edged = cv2.Canny(blurred, 75, 200)

        # Applica dilatazione per chiudere i gap
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(edged, kernel, iterations=1)

        # Trova contorni
        contours, _ = cv2.findContours(dilated.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        document_contour = None

        # Loop sui contorni per trovare il documento
        for contour in contours:
            # Approssima il contorno
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

            # Se il contorno ha 4 punti, assumiamo sia il documento
            if len(approx) == 4:
                document_contour = approx
                break

        if document_contour is None:
            # Fallback: usa i bordi dell'immagine
            logger.warning("Contorno documento non rilevato, uso bordi immagine")
            h, w = image_resized.shape[:2]
            document_contour = np.array([
                [[0, 0]],
                [[w-1, 0]],
                [[w-1, h-1]],
                [[0, h-1]]
            ])

        # Scala i punti alla dimensione originale
        document_contour = document_contour.reshape(4, 2) * ratio

        return document_contour

    def four_point_transform(self, image: np.ndarray, pts: np.ndarray) -> np.ndarray:
        """
        Applica la trasformazione prospettica per raddrizzare il documento

        Args:
            image: Immagine input
            pts: Array di 4 punti degli angoli del documento

        Returns:
            Immagine trasformata
        """
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect

        # Calcola la larghezza del nuovo documento
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        # Calcola l'altezza del nuovo documento
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        # Assicura il rapporto A4
        if maxWidth / maxHeight < self.A4_RATIO:
            maxWidth = int(maxHeight * self.A4_RATIO)
        else:
            maxHeight = int(maxWidth / self.A4_RATIO)

        # Costruisci i punti di destinazione
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")

        # Calcola la matrice di trasformazione prospettica e applica
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        return warped

    def deskew_image(self, image: np.ndarray) -> np.ndarray:
        """
        Corregge l'inclinazione del documento

        Args:
            image: Immagine input

        Returns:
            Immagine raddrizzata
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)

        # Rileva l'angolo di inclinazione usando coordinate dei pixel
        coords = np.column_stack(np.where(gray > 0))

        if len(coords) == 0:
            return image

        angle = cv2.minAreaRect(coords)[-1]

        # Correggi l'angolo
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Ruota l'immagine se l'angolo è significativo
        if abs(angle) > 0.5:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h),
                                    flags=cv2.INTER_CUBIC,
                                    borderMode=cv2.BORDER_REPLICATE)
            return rotated

        return image

    def remove_shadows(self, image: np.ndarray) -> np.ndarray:
        """
        Rimuove ombre e migliora l'uniformità del background

        Args:
            image: Immagine input

        Returns:
            Immagine senza ombre
        """
        # Converti in LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        # Applica CLAHE (Contrast Limited Adaptive Histogram Equalization) al canale L
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)

        # Merge e converti back a BGR
        lab = cv2.merge([l, a, b])
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        return result

    def enhance_document(self, image: np.ndarray) -> np.ndarray:
        """
        Migliora la leggibilità del documento come uno scanner professionale

        Args:
            image: Immagine input

        Returns:
            Immagine migliorata
        """
        # Rimuovi ombre
        image = self.remove_shadows(image)

        # Converti in grayscale se richiesto
        if self.grayscale:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Applica adaptive thresholding per ottenere effetto scanner B&N
            thresh = cv2.adaptiveThreshold(
                gray, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11, 10
            )

            # Converti back a BGR per uniformità
            image = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        else:
            # Aumenta contrasto e nitidezza
            # Sharpening kernel
            kernel = np.array([[-1,-1,-1],
                             [-1, 9,-1],
                             [-1,-1,-1]])
            sharpened = cv2.filter2D(image, -1, kernel)

            # Blend con l'originale
            image = cv2.addWeighted(image, 0.7, sharpened, 0.3, 0)

            # Aumenta leggermente la saturazione
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:, :, 1] = hsv[:, :, 1] * 1.2
            hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
            image = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        return image

    def resize_to_a4(self, image: np.ndarray) -> np.ndarray:
        """
        Ridimensiona l'immagine esattamente in formato A4

        Args:
            image: Immagine input

        Returns:
            Immagine ridimensionata A4
        """
        # Ridimensiona mantenendo il rapporto A4
        resized = cv2.resize(image, (self.a4_width, self.a4_height),
                           interpolation=cv2.INTER_LANCZOS4)
        return resized

    def process_image(self, image_path: Path) -> Optional[np.ndarray]:
        """
        Processa una singola immagine attraverso l'intera pipeline

        Args:
            image_path: Path dell'immagine da processare

        Returns:
            Immagine processata o None se fallisce
        """
        try:
            logger.info(f"Processing: {image_path.name}")

            # Carica immagine
            image = cv2.imread(str(image_path))
            if image is None:
                logger.error(f"Impossibile caricare: {image_path}")
                return None

            # Step 1: Rileva bordi del documento
            logger.info("  - Rilevamento bordi documento...")
            contour = self.detect_document_contour(image)

            # Step 2: Applica perspective transform
            logger.info("  - Correzione prospettiva...")
            warped = self.four_point_transform(image, contour)

            # Step 3: Deskew (raddrizza)
            logger.info("  - Correzione inclinazione...")
            deskewed = self.deskew_image(warped)

            # Step 4: Enhancement (rimozione ombre, miglioramento contrasto)
            if self.enhance:
                logger.info("  - Enhancement qualità...")
                enhanced = self.enhance_document(deskewed)
            else:
                enhanced = deskewed

            # Step 5: Ridimensiona a A4
            logger.info("  - Ridimensionamento A4...")
            final = self.resize_to_a4(enhanced)

            logger.info(f"  ✓ Completato: {image_path.name}")
            return final

        except Exception as e:
            logger.error(f"Errore processing {image_path.name}: {e}")
            return None

    def process_batch(self, input_dir: Path, image_extensions: List[str] = None) -> List[Tuple[str, np.ndarray]]:
        """
        Processa tutte le immagini in una directory

        Args:
            input_dir: Directory contenente le immagini
            image_extensions: Lista di estensioni da processare

        Returns:
            Lista di tuple (nome_file, immagine_processata)
        """
        if image_extensions is None:
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']

        processed_images = []

        # Trova tutte le immagini
        image_files = []
        for ext in image_extensions:
            image_files.extend(input_dir.glob(f'*{ext}'))
            image_files.extend(input_dir.glob(f'*{ext.upper()}'))

        image_files = sorted(set(image_files))

        logger.info(f"Trovate {len(image_files)} immagini da processare")

        for image_path in image_files:
            processed = self.process_image(image_path)
            if processed is not None:
                # Salva l'immagine processata
                output_path = self.output_dir / f"processed_{image_path.name}"
                cv2.imwrite(str(output_path), processed,
                          [cv2.IMWRITE_JPEG_QUALITY, self.quality])
                processed_images.append((image_path.stem, processed))
                logger.info(f"Salvato: {output_path}")

        logger.info(f"Processate con successo {len(processed_images)}/{len(image_files)} immagini")
        return processed_images

    def create_pdf(self, images: List[Tuple[str, np.ndarray]],
                   output_name: str = "output.pdf",
                   single_pdf: bool = True) -> None:
        """
        Crea PDF dalle immagini processate

        Args:
            images: Lista di tuple (nome, immagine)
            output_name: Nome del file PDF di output
            single_pdf: Se True, crea un singolo PDF, altrimenti uno per immagine
        """
        if not images:
            logger.warning("Nessuna immagine da convertire in PDF")
            return

        try:
            if single_pdf:
                # Crea un singolo PDF con tutte le pagine
                logger.info(f"Creazione PDF unico: {output_name}")

                pil_images = []
                for name, img in images:
                    # Converti da BGR (OpenCV) a RGB (PIL)
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(img_rgb)
                    pil_images.append(pil_img)

                if pil_images:
                    output_path = self.output_dir / output_name
                    pil_images[0].save(
                        str(output_path),
                        "PDF",
                        resolution=self.dpi,
                        save_all=True,
                        append_images=pil_images[1:] if len(pil_images) > 1 else []
                    )
                    logger.info(f"✓ PDF creato: {output_path} ({len(pil_images)} pagine)")
            else:
                # Crea un PDF separato per ogni immagine
                logger.info("Creazione PDF individuali...")
                for name, img in images:
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(img_rgb)

                    output_path = self.output_dir / f"{name}.pdf"
                    pil_img.save(str(output_path), "PDF", resolution=self.dpi)
                    logger.info(f"✓ PDF creato: {output_path}")

                logger.info(f"Creati {len(images)} PDF individuali")

        except Exception as e:
            logger.error(f"Errore nella creazione PDF: {e}")


def main():
    """Funzione principale con CLI"""
    parser = argparse.ArgumentParser(
        description='Document Scanner - Automatizza il processing di documenti A4 fotografati',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi di utilizzo:

  # Processing base con un singolo PDF
  python document_scanner.py -i ./input -o ./output

  # Conversione in bianco e nero con PDF separati
  python document_scanner.py -i ./docs -o ./scanned --grayscale --separate-pdfs

  # Alta qualità con DPI personalizzato
  python document_scanner.py -i ./input -o ./output --dpi 600 --quality 100

  # Senza enhancement automatico
  python document_scanner.py -i ./input --no-enhance
        """
    )

    parser.add_argument(
        '-i', '--input',
        type=str,
        required=True,
        help='Directory contenente le immagini da processare'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default='processed',
        help='Directory di output (default: processed)'
    )

    parser.add_argument(
        '--grayscale',
        action='store_true',
        help='Converti in bianco e nero (modalità scanner)'
    )

    parser.add_argument(
        '--no-enhance',
        action='store_true',
        help='Disabilita enhancement automatico della qualità'
    )

    parser.add_argument(
        '--dpi',
        type=int,
        default=300,
        choices=[150, 200, 300, 600],
        help='DPI del documento finale (default: 300)'
    )

    parser.add_argument(
        '--quality',
        type=int,
        default=95,
        choices=range(1, 101),
        metavar='[1-100]',
        help='Qualità JPEG 1-100 (default: 95)'
    )

    parser.add_argument(
        '--separate-pdfs',
        action='store_true',
        help='Crea un PDF separato per ogni immagine invece di un singolo PDF'
    )

    parser.add_argument(
        '--pdf-name',
        type=str,
        default='scanned_document.pdf',
        help='Nome del PDF di output (default: scanned_document.pdf)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Output verboso'
    )

    args = parser.parse_args()

    # Configura logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Valida input directory
    input_dir = Path(args.input)
    if not input_dir.exists():
        logger.error(f"Directory input non trovata: {input_dir}")
        sys.exit(1)

    if not input_dir.is_dir():
        logger.error(f"Il path non è una directory: {input_dir}")
        sys.exit(1)

    # Inizializza scanner
    logger.info("=== Document Scanner Pipeline ===")
    logger.info(f"Input: {input_dir}")
    logger.info(f"Output: {args.output}")
    logger.info(f"Modalità: {'Bianco e Nero' if args.grayscale else 'Colore'}")
    logger.info(f"DPI: {args.dpi}")
    logger.info(f"Qualità: {args.quality}")

    scanner = DocumentScanner(
        output_dir=args.output,
        grayscale=args.grayscale,
        enhance=not args.no_enhance,
        dpi=args.dpi,
        quality=args.quality
    )

    # Processa batch
    start_time = datetime.now()
    processed_images = scanner.process_batch(input_dir)

    # Crea PDF
    if processed_images:
        scanner.create_pdf(
            processed_images,
            output_name=args.pdf_name,
            single_pdf=not args.separate_pdfs
        )

    # Report finale
    duration = (datetime.now() - start_time).total_seconds()
    logger.info("=== Processing Completato ===")
    logger.info(f"Immagini processate: {len(processed_images)}")
    logger.info(f"Tempo impiegato: {duration:.2f}s")
    logger.info(f"Output salvato in: {Path(args.output).absolute()}")


if __name__ == "__main__":
    main()
