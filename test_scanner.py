#!/usr/bin/env python3
"""
Script di test e validazione per DocumentScanner
Verifica che tutte le funzionalità funzionino correttamente
"""

import cv2
import numpy as np
from pathlib import Path
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_opencv_installation():
    """Test 1: Verifica installazione OpenCV"""
    print("\n[TEST 1] Verifica installazione OpenCV...")
    try:
        version = cv2.__version__
        print(f"  ✓ OpenCV versione: {version}")

        # Test funzioni critiche
        assert hasattr(cv2, 'imread'), "imread non disponibile"
        assert hasattr(cv2, 'Canny'), "Canny non disponibile"
        assert hasattr(cv2, 'getPerspectiveTransform'), "getPerspectiveTransform non disponibile"
        assert hasattr(cv2, 'createCLAHE'), "createCLAHE non disponibile"

        print("  ✓ Tutte le funzioni OpenCV necessarie sono disponibili")
        return True
    except Exception as e:
        print(f"  ✗ ERRORE: {e}")
        return False


def test_numpy():
    """Test 2: Verifica NumPy"""
    print("\n[TEST 2] Verifica NumPy...")
    try:
        version = np.__version__
        print(f"  ✓ NumPy versione: {version}")

        # Test operazioni base
        arr = np.array([[1, 2], [3, 4]])
        assert arr.shape == (2, 2), "Shape non corretta"
        assert np.sum(arr) == 10, "Somma non corretta"

        print("  ✓ NumPy funziona correttamente")
        return True
    except Exception as e:
        print(f"  ✗ ERRORE: {e}")
        return False


def test_pillow():
    """Test 3: Verifica Pillow"""
    print("\n[TEST 3] Verifica Pillow/PIL...")
    try:
        from PIL import Image
        print(f"  ✓ Pillow importato correttamente")

        # Crea immagine test
        img = Image.new('RGB', (100, 100), color='red')
        assert img.size == (100, 100), "Dimensioni non corrette"

        print("  ✓ Pillow funziona correttamente")
        return True
    except Exception as e:
        print(f"  ✗ ERRORE: {e}")
        return False


def test_document_scanner_import():
    """Test 4: Verifica import DocumentScanner"""
    print("\n[TEST 4] Verifica import DocumentScanner...")
    try:
        from document_scanner import DocumentScanner
        print("  ✓ DocumentScanner importato correttamente")

        # Test inizializzazione
        scanner = DocumentScanner(output_dir="test_output")
        assert scanner.dpi == 300, "DPI default non corretto"
        assert scanner.a4_width == 2480, "Larghezza A4 non corretta"
        assert scanner.a4_height == 3508, "Altezza A4 non corretta"

        print("  ✓ DocumentScanner inizializzato correttamente")
        return True
    except Exception as e:
        print(f"  ✗ ERRORE: {e}")
        return False


def test_create_synthetic_document():
    """Test 5: Crea documento sintetico per test"""
    print("\n[TEST 5] Creazione documento sintetico...")
    try:
        # Crea immagine con documento A4 bianco su sfondo scuro
        img_width, img_height = 1000, 1414  # Rapporto A4
        image = np.ones((img_height, img_width, 3), dtype=np.uint8) * 50  # Sfondo grigio scuro

        # Documento bianco (A4 con prospettiva)
        pts = np.array([
            [100, 200],   # Top-left
            [900, 150],   # Top-right
            [950, 1300],  # Bottom-right
            [50, 1350]    # Bottom-left
        ], dtype=np.int32)

        cv2.fillPoly(image, [pts], (255, 255, 255))

        # Aggiungi del testo simulato
        cv2.putText(image, "DOCUMENTO DI TEST", (300, 600),
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
        cv2.putText(image, "A4 Format Test", (350, 800),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)

        # Salva immagine test
        test_dir = Path("test_input")
        test_dir.mkdir(exist_ok=True)
        test_path = test_dir / "test_document.jpg"

        cv2.imwrite(str(test_path), image)
        print(f"  ✓ Documento sintetico creato: {test_path}")

        return True, test_path
    except Exception as e:
        print(f"  ✗ ERRORE: {e}")
        return False, None


def test_edge_detection():
    """Test 6: Test edge detection"""
    print("\n[TEST 6] Test edge detection...")
    try:
        from document_scanner import DocumentScanner

        # Crea documento test
        success, test_path = test_create_synthetic_document()
        if not success:
            return False

        scanner = DocumentScanner()
        image = cv2.imread(str(test_path))

        # Test rilevamento contorni
        contour = scanner.detect_document_contour(image)
        assert contour is not None, "Contorno non rilevato"
        assert len(contour) == 4, f"Contorno deve avere 4 punti, trovati {len(contour)}"

        print(f"  ✓ Contorno rilevato con successo: {contour.shape}")
        return True
    except Exception as e:
        print(f"  ✗ ERRORE: {e}")
        return False


def test_perspective_transform():
    """Test 7: Test trasformazione prospettica"""
    print("\n[TEST 7] Test perspective transform...")
    try:
        from document_scanner import DocumentScanner

        test_dir = Path("test_input")
        test_path = test_dir / "test_document.jpg"

        if not test_path.exists():
            test_create_synthetic_document()

        scanner = DocumentScanner()
        image = cv2.imread(str(test_path))
        contour = scanner.detect_document_contour(image)

        # Test trasformazione
        warped = scanner.four_point_transform(image, contour)
        assert warped is not None, "Trasformazione fallita"
        assert len(warped.shape) == 3, "Immagine deve essere a colori"

        # Verifica rapporto A4
        h, w = warped.shape[:2]
        ratio = h / w
        expected_ratio = 1.414
        assert abs(ratio - expected_ratio) < 0.1, f"Rapporto non A4: {ratio}"

        print(f"  ✓ Perspective transform OK - Dimensioni: {w}×{h}, Ratio: {ratio:.3f}")
        return True
    except Exception as e:
        print(f"  ✗ ERRORE: {e}")
        return False


def test_deskew():
    """Test 8: Test deskew"""
    print("\n[TEST 8] Test deskew...")
    try:
        from document_scanner import DocumentScanner

        # Crea immagine inclinata
        img = np.ones((500, 700, 3), dtype=np.uint8) * 255
        cv2.rectangle(img, (100, 100), (600, 400), (0, 0, 0), 2)

        # Ruota di 5 gradi
        center = (350, 250)
        M = cv2.getRotationMatrix2D(center, 5, 1.0)
        rotated = cv2.warpAffine(img, M, (700, 500))

        scanner = DocumentScanner()
        deskewed = scanner.deskew_image(rotated)

        assert deskewed is not None, "Deskew fallito"
        print(f"  ✓ Deskew completato - Dimensioni: {deskewed.shape[:2]}")
        return True
    except Exception as e:
        print(f"  ✗ ERRORE: {e}")
        return False


def test_enhancement():
    """Test 9: Test enhancement"""
    print("\n[TEST 9] Test enhancement...")
    try:
        from document_scanner import DocumentScanner

        # Crea immagine con ombre
        img = np.ones((500, 700, 3), dtype=np.uint8) * 200
        # Aggiungi ombra
        cv2.circle(img, (350, 250), 150, (100, 100, 100), -1)

        scanner = DocumentScanner()

        # Test rimozione ombre
        enhanced = scanner.remove_shadows(img)
        assert enhanced is not None, "Shadow removal fallito"

        # Test enhancement completo
        enhanced_full = scanner.enhance_document(img)
        assert enhanced_full is not None, "Enhancement fallito"

        print(f"  ✓ Enhancement completato")
        return True
    except Exception as e:
        print(f"  ✗ ERRORE: {e}")
        return False


def test_resize_a4():
    """Test 10: Test resize A4"""
    print("\n[TEST 10] Test resize A4...")
    try:
        from document_scanner import DocumentScanner

        img = np.ones((1000, 707, 3), dtype=np.uint8) * 255

        scanner = DocumentScanner(dpi=300)
        resized = scanner.resize_to_a4(img)

        assert resized.shape[1] == 2480, f"Larghezza non corretta: {resized.shape[1]}"
        assert resized.shape[0] == 3508, f"Altezza non corretta: {resized.shape[0]}"

        print(f"  ✓ Resize A4 OK - Dimensioni finali: {resized.shape[1]}×{resized.shape[0]}px @ 300 DPI")
        return True
    except Exception as e:
        print(f"  ✗ ERRORE: {e}")
        return False


def test_full_pipeline():
    """Test 11: Test pipeline completa"""
    print("\n[TEST 11] Test pipeline completa...")
    try:
        from document_scanner import DocumentScanner

        # Setup
        test_input_dir = Path("test_input")
        test_output_dir = Path("test_output")
        test_input_dir.mkdir(exist_ok=True)
        test_output_dir.mkdir(exist_ok=True)

        # Crea documento test se non esiste
        test_path = test_input_dir / "test_document.jpg"
        if not test_path.exists():
            test_create_synthetic_document()

        # Inizializza scanner
        scanner = DocumentScanner(
            output_dir=str(test_output_dir),
            grayscale=False,
            dpi=300,
            quality=95
        )

        # Processa immagine
        processed = scanner.process_image(test_path)
        assert processed is not None, "Processing fallito"

        # Verifica dimensioni output
        assert processed.shape[1] == 2480, "Larghezza output non corretta"
        assert processed.shape[0] == 3508, "Altezza output non corretta"

        # Test salvataggio
        output_path = test_output_dir / "processed_test.jpg"
        cv2.imwrite(str(output_path), processed, [cv2.IMWRITE_JPEG_QUALITY, 95])
        assert output_path.exists(), "File output non salvato"

        print(f"  ✓ Pipeline completa OK - Output salvato in: {output_path}")
        return True
    except Exception as e:
        print(f"  ✗ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_creation():
    """Test 12: Test creazione PDF"""
    print("\n[TEST 12] Test creazione PDF...")
    try:
        from document_scanner import DocumentScanner
        from PIL import Image

        test_output_dir = Path("test_output")
        test_output_dir.mkdir(exist_ok=True)

        # Crea immagini test
        img1 = np.ones((3508, 2480, 3), dtype=np.uint8) * 255
        img2 = np.ones((3508, 2480, 3), dtype=np.uint8) * 200

        cv2.putText(img1, "Pagina 1", (1000, 1754), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 5)
        cv2.putText(img2, "Pagina 2", (1000, 1754), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 5)

        scanner = DocumentScanner(output_dir=str(test_output_dir))

        # Test PDF singolo
        images = [("page1", img1), ("page2", img2)]
        scanner.create_pdf(images, output_name="test_single.pdf", single_pdf=True)

        pdf_path = test_output_dir / "test_single.pdf"
        assert pdf_path.exists(), "PDF non creato"
        assert pdf_path.stat().st_size > 0, "PDF vuoto"

        print(f"  ✓ PDF creato con successo: {pdf_path} ({pdf_path.stat().st_size} bytes)")

        # Test PDF separati
        scanner.create_pdf(images, single_pdf=False)
        assert (test_output_dir / "page1.pdf").exists(), "PDF pagina 1 non creato"
        assert (test_output_dir / "page2.pdf").exists(), "PDF pagina 2 non creato"

        print(f"  ✓ PDF separati creati con successo")
        return True
    except Exception as e:
        print(f"  ✗ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_processing():
    """Test 13: Test batch processing"""
    print("\n[TEST 13] Test batch processing...")
    try:
        from document_scanner import DocumentScanner

        # Setup
        test_input_dir = Path("test_input")
        test_output_dir = Path("test_output_batch")
        test_input_dir.mkdir(exist_ok=True)

        # Crea multiple immagini test
        for i in range(3):
            img = np.ones((1414, 1000, 3), dtype=np.uint8) * 255
            cv2.putText(img, f"Document {i+1}", (300, 700),
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
            cv2.imwrite(str(test_input_dir / f"doc_{i}.jpg"), img)

        # Processa batch
        scanner = DocumentScanner(output_dir=str(test_output_dir))
        processed = scanner.process_batch(test_input_dir)

        assert len(processed) == 3, f"Dovrebbero essere 3 immagini, trovate {len(processed)}"
        print(f"  ✓ Batch processing OK - Processate {len(processed)} immagini")

        # Cleanup
        import shutil
        if test_output_dir.exists():
            shutil.rmtree(test_output_dir)

        return True
    except Exception as e:
        print(f"  ✗ ERRORE: {e}")
        return False


def run_all_tests():
    """Esegue tutti i test"""
    print("="*60)
    print("DOCUMENT SCANNER - TEST SUITE")
    print("="*60)

    tests = [
        ("Installazione OpenCV", test_opencv_installation),
        ("NumPy", test_numpy),
        ("Pillow", test_pillow),
        ("Import DocumentScanner", test_document_scanner_import),
        ("Documento Sintetico", lambda: test_create_synthetic_document()[0]),
        ("Edge Detection", test_edge_detection),
        ("Perspective Transform", test_perspective_transform),
        ("Deskew", test_deskew),
        ("Enhancement", test_enhancement),
        ("Resize A4", test_resize_a4),
        ("Pipeline Completa", test_full_pipeline),
        ("Creazione PDF", test_pdf_creation),
        ("Batch Processing", test_batch_processing),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[TEST] {name} - ✗ ECCEZIONE: {e}")
            results.append((name, False))

    # Report finale
    print("\n" + "="*60)
    print("RISULTATI TEST")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} | {name}")

    print("="*60)
    print(f"Risultato: {passed}/{total} test passati ({100*passed/total:.1f}%)")
    print("="*60)

    if passed == total:
        print("\n🎉 TUTTI I TEST PASSATI! Il sistema è pronto all'uso.")
        return 0
    else:
        print(f"\n⚠ {total-passed} test falliti. Verifica l'installazione.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
