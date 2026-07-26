"""Funzioni pure per il codice fiscale italiano."""

from __future__ import annotations


# ── Tabelle CIN (fonte: fonti/codice_fiscale.md §7) ────────────────────

# Valore per posizione dispari (1,3,5,...,15) — sia lettere che cifre
_CIN_DISPARI: dict[str, int] = {
    'A': 1, 'B': 0, 'C': 5, 'D': 7, 'E': 9, 'F': 13, 'G': 15, 'H': 17,
    'I': 19, 'J': 21, 'K': 2, 'L': 4, 'M': 18, 'N': 20, 'O': 11, 'P': 3,
    'Q': 6, 'R': 8, 'S': 12, 'T': 14, 'U': 16, 'V': 10, 'W': 22, 'X': 25,
    'Y': 24, 'Z': 23,
    '0': 1, '1': 0, '2': 5, '3': 7, '4': 9, '5': 13, '6': 15, '7': 17,
    '8': 19, '9': 21,
}

# Valore per posizione pari (2,4,6,...,14) — sia lettere che cifre
_CIN_PARI: dict[str, int] = {
    'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7,
    'I': 8, 'J': 9, 'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15,
    'Q': 16, 'R': 17, 'S': 18, 'T': 19, 'U': 20, 'V': 21, 'W': 22, 'X': 23,
    'Y': 24, 'Z': 25,
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
    '8': 8, '9': 9,
}


def cin_codice_fiscale(primi15: str) -> str:
    """
    Calcola il carattere di controllo (CIN) dai primi 15 caratteri del codice
    fiscale.

    Fonte: `fonti/codice_fiscale.md` §7 (checksum CIN).

        >>> cin_codice_fiscale("RSSMRA80A01H501")
        'U'
        >>> cin_codice_fiscale("MRTMTT25D09F205")
        'Z'

    Solleva ValueError se l'ingresso non è una stringa esatta di 15
    caratteri alfanumerici maiuscoli.
    """
    if not isinstance(primi15, str) or len(primi15) != 15:
        raise ValueError(
            "l'ingresso deve essere una stringa di esattamente 15 caratteri"
        )
    if not primi15.isalnum() or primi15 != primi15.upper():
        raise ValueError(
            "l'ingresso deve contenere solo caratteri alfanumerici maiuscoli"
        )

    somma = 0
    for i, car in enumerate(primi15):
        if i % 2 == 0:  # posizione 1-based dispari
            somma += _CIN_DISPARI[car]
        else:  # posizione 1-based pari
            somma += _CIN_PARI[car]

    resto = somma % 26
    return chr(ord('A') + resto)
