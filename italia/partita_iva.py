"""
Validazione e normalizzazione della partita IVA italiana.

Algoritmo ufficiale: DPR 605/1973, art. 4 — checksum di Luhn su 11 cifre,
con vincoli sul progressivo (prime 7 cifre) e sull'ufficio (cifre 8-10).

Funzioni pure: nessuna rete, nessun file, nessuno stato globale.
"""

from __future__ import annotations

import re
from typing import Final

# Uffici provinciali e casi speciali ammessi nelle cifre 8-10
UFFICI_AMMESSI: Final[frozenset[int]] = frozenset(
    list(range(1, 101))  # 001-100: uffici provinciali
    + [120, 121, 888, 999]  # uffici speciali
)

# Pattern per pulire l'input: spazi, trattini, punti, prefisso IT
PULIZIA_PATTERN: Final[re.Pattern[str]] = re.compile(r"[\s\.\-]|^IT$|^IT(?=\d)")


def _normalizza_partita_iva(partita_iva: str) -> str:
    """
    Normalizza una partita IVA rimuovendo spazi, trattini, punti e il prefisso IT.

    Args:
        partita_iva: La stringa da normalizzare.

    Returns:
        La partita IVA normalizzata (solo 11 cifre) o stringa vuota se invalida.
    """
    if not isinstance(partita_iva, str):
        return ""

    # Rimuovi spazi, trattini, punti e gestisci prefisso IT
    pulita = partita_iva.strip()
    pulita = re.sub(r"[\s\.\-]", "", pulita)

    # Rimuovi prefisso IT (case insensitive)
    if pulita.upper().startswith("IT"):
        pulita = pulita[2:]

    # Verifica che siano solo cifre
    if not pulita.isdigit():
        return ""

    return pulita


def _checksum_luhn(cifre: str) -> bool:
    """
    Verifica il checksum di Luhn per le prime 10 cifre.

    Algoritmo:
    1. Cifre in posizione dispari (1,3,5,7,9) → somma diretta
    2. Cifre in posizione pari (2,4,6,8,10) → raddoppia, se >9 sottrai 9
    3. Somma totale T
    4. Cifra di controllo = (10 - (T mod 10)) mod 10

    Args:
        cifre: Stringa di 11 cifre (le prime 10 per il calcolo, l'11esima per verifica)

    Returns:
        True se il checksum è valido, False altrimenti.
    """
    totale = 0

    for i in range(10):  # Prime 10 cifre
        cifra = int(cifre[i])

        if (i + 1) % 2 == 1:  # Posizione dispari (1-based)
            totale += cifra
        else:  # Posizione pari (1-based)
            doubled = cifra * 2
            totale += doubled if doubled <= 9 else doubled - 9

    cifra_controllo_calcolata = (10 - (totale % 10)) % 10
    cifra_controllo_effettiva = int(cifre[10])

    return cifra_controllo_calcolata == cifra_controllo_effettiva


def _valida_progressivo(progressivo: str) -> bool:
    """
    Verifica che il progressivo (prime 7 cifre) non sia tutti zeri.

    Args:
        progressivo: Le prime 7 cifre della partita IVA.

    Returns:
        True se il progressivo è valido, False se è '0000000'.
    """
    return progressivo != "0000000"


def _validaUfficio(ufficio: str) -> bool:
    """
    Verifica che l'ufficio (cifre 8-10) sia nell'elenco degli uffici ammessi.

    Args:
        ufficio: Le cifre 8-10 della partita IVA come stringa.

    Returns:
        True se l'ufficio è valido, False altrimenti.
    """
    try:
        codice_ufficio = int(ufficio)
        return codice_ufficio in UFFICI_AMMESSI
    except ValueError:
        return False


def valida_partita_iva(partita_iva: str) -> bool:
    """
    Valida una partita IVA italiana secondo l'algoritmo ufficiale.

    Controlli effettuati:
    1. Formato: esattamente 11 cifre (tolerando spazi, trattini, punti, prefisso IT)
    2. Checksum di Luhn sulle prime 10 cifre
    3. Progressivo (prime 7 cifre) non nullo: non può essere '0000000'
    4. Ufficio (cifre 8-10) valido: deve essere nell'elenco ufficiale

    Args:
        partita_iva: La stringa da validare. Accetta formati come:
                     '00743110157', 'IT00743110157', '007-431-101-57', ecc.

    Returns:
        True se la partita IVA è valida, False altrimenti.

    Examples:
        >>> valida_partita_iva("00743110157")
        True
        >>> valida_partita_iva("00743110158")
        False
        >>> valida_partita_iva("IT 00743110157")
        True
        >>> valida_partita_iva("00000000000")
        False
    """
    # Normalizza l'input
    normalizzata = _normalizza_partita_iva(partita_iva)

    # Controllo lunghezza
    if len(normalizzata) != 11:
        return False

    # Controllo checksum di Luhn
    if not _checksum_luhn(normalizzata):
        return False

    # Controllo progressivo (prime 7 cifre)
    if not _valida_progressivo(normalizzata[:7]):
        return False

    # Controllo ufficio (cifre 8-10)
    if not _validaUfficio(normalizzata[7:10]):
        return False

    return True


def estrai_partita_iva(testo: str) -> str | None:
    """
    Estrae una partita IVA da un testo contenente altro.

    Cerca pattern di 11 cifre consecutive (eventualmente precedute da IT),
    tollerando anche spazi, trattini e punti tra le cifre.
    Restituisce la prima partita IVA valida trovata.

    Args:
        testo: Il testo da cui estrarre la partita IVA.

    Returns:
        La partita IVA estratta (11 cifre) o None se non trovata.

    Examples:
        >>> estrai_partita_iva("La P.IVA è 00743110157, grazie.")
        '00743110157'
        >>> estrai_partita_iva("Contatto: IT07643520567")
        '07643520567'
        >>> estrai_partita_iva("Nessuna partita IVA qui")
        None
    """
    # Pattern per trovare partite IVA con possibili separatori (spazi, trattini, punti)
    # Cattura gruppi di cifre separati da eventuali separatori
    pattern = re.compile(r"(?:IT)?(\d(?:[\s\.\-]?\d){10,})")

    for match in pattern.finditer(testo):
        candidata_raw = match.group(1)
        # Normalizza rimuovendo separatori
        candidata = _normalizza_partita_iva(candidata_raw)
        if valida_partita_iva(candidata):
            return candidata

    return None
