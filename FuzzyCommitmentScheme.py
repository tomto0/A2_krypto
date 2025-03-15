import numpy as np

# Schritt 1: Erstellen eines zufälligen binären biometrischen Templates
KEY_LENGTH = 128  # 128-Bit-Schlüssel
biometrisches_template = np.random.randint(0, 100, KEY_LENGTH * 7 // 4, dtype=np.uint8)  # Richtige Länge für XOR

# Schritt 2: Generieren eines zufälligen 128-Bit-Schlüssels
schluessel = np.random.randint(0, 100, KEY_LENGTH, dtype=np.uint8)
print("Originaler Schlüssel:", schluessel.tolist())


# Schritt 3: Codierung des Schlüssels mit Hamming ECC (Hamming(7,4))
def hamming_kodieren(daten):
    kodiert = []
    for i in range(0, len(daten), 4):
        d1, d2, d3, d4 = (daten[i:i + 4] if i + 4 <= len(daten) else np.zeros(4, dtype=np.uint8))
        p1 = d1 ^ d2 ^ d4
        p2 = d1 ^ d3 ^ d4
        p3 = d2 ^ d3 ^ d4
        kodiert.extend([p1, p2, d1, p3, d2, d3, d4])
    return np.array(kodiert, dtype=np.uint8)


kodierter_schluessel = hamming_kodieren(schluessel)
print("Kodierter Schlüssel (Hamming 7,4):", kodierter_schluessel.tolist())

# Schritt 4: Erstellen des Commitments
commitment = np.bitwise_xor(biometrisches_template, kodierter_schluessel)
print("Commitment:", commitment.tolist())


# Schritt 5: Simulierte biometrische Varianz (Kippen einiger Bits)
def bits_kippen(daten, anzahl_kippen=2):
    indizes = np.random.choice(len(daten), anzahl_kippen, replace=False)
    daten[indizes] ^= 1
    print(f"Gekippte Bits an Positionen: {indizes.tolist()}")


rauschendes_biometrisches = biometrisches_template.copy()
bits_kippen(rauschendes_biometrisches, 2)
print("Verändertes biometrisches Template:", rauschendes_biometrisches.tolist())


# Schritt 6: Wiederherstellung des Schlüssels mit ECC-Dekodierung
def hamming_dekodieren(kodiert):
    dekodiert = []
    for i in range(0, len(kodiert), 7):
        if i + 7 > len(kodiert):
            break  # Falls unvollständige Gruppen, ignoriere sie
        p1, p2, d1, p3, d2, d3, d4 = kodiert[i:i + 7]
        s1 = p1 ^ d1 ^ d2 ^ d4
        s2 = p2 ^ d1 ^ d3 ^ d4
        s3 = p3 ^ d2 ^ d3 ^ d4
        fehler_position = (s3 << 2) | (s2 << 1) | s1

        # Fehlerkorrektur anwenden, aber nur falls Fehlerposition in den Datenbits liegt
        if 1 <= fehler_position <= 7:
            kodiert[i + fehler_position - 1] ^= 1
            print(f"Korrigiertes Bit an Position: {i + fehler_position - 1}")

            # Nach Korrektur, Bits erneut extrahieren
            p1, p2, d1, p3, d2, d3, d4 = kodiert[i:i + 7]

        dekodiert.extend([d1, d2, d3, d4])

    return np.array(dekodiert[:KEY_LENGTH], dtype=np.uint8)  # Ursprüngliche Länge wiederherstellen


wiederhergestellter_schluessel = hamming_dekodieren(np.bitwise_xor(rauschendes_biometrisches, commitment))
print("Wiederhergestellter Schlüssel:", wiederhergestellter_schluessel.tolist())
print("Schlüssel stimmen überein:",
      "✅ Erfolgreich!" if np.array_equal(schluessel, wiederhergestellter_schluessel) else "❌ Fehlgeschlagen!")
