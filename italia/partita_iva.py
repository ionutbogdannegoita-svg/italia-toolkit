"""
Funzioni per la partita IVA italiana.

Fonte: fonti/partita_iva.md
"""

from __future__ import annotations


def cifra_controllo_partita_iva(dieci_cifre: str) -> int:
    """
    Calcola la cifra di controllo (Luhn) delle prime 10 cifre di una P.IVA.

    Fonte: `fonti/partita_iva.md` §4 (checksum Luhn).

        >>> cifra_controllo_partita_iva("0074311015")
        7
        >>> cifra_controllo_partita_iva("0000000000")
        0

    Solleva ValueError se l'ingresso non è esattamente 10 cifre decimali.
    """
    if len(dieci_cifre) != 10 or not dieci_cifre.isdigit():
        raise ValueError(
            f"ingresso deve essere esattamente 10 cifre decimali, "
            f"non {dieci_cifre!r}"
        )

    totale = 0
    for i, char in enumerate(dieci_cifre):
        cifra = int(char)
        posizione = i + 1  # 1-based da sinistra
        if posizione % 2 == 0:  # posizione pari: raddoppia
            doubled = cifra * 2
            if doubled > 9:
                doubled -= 9
            totale += doubled
        else:  # posizione dispari: somma così
            totale += cifra

    return (10 - (totale % 10)) % 10


def normalizza_partita_iva(numero: str) -> str:
    """
    Normalizza un numero di partita IVA rimuovendo spazi, trattini, punti
    e il prefisso IT, restituendo le 11 cifre pulite.

    Fonte: `fonti/partita_iva.md` §1 (formato) e §5.2 (normalizzazione).

        >>> normalizza_partita_iva("00743110157")
        '00743110157'
        >>> normalizza_partita_iva("IT 007-431.101.57")
        '00743110157'

    Solleva ValueError se il risultato non è esattamente 11 cifre decimali.
    Non valida checksum né codice ufficio.
    """
    s = numero.strip()
    # Rimuovi prefisso IT (con eventuale spazio dopo)
    if s.upper().startswith("IT"):
        s = s[2:].lstrip()
    # Rimuovi spazi, trattini, punti
    s = s.replace(" ", "").replace("-", "").replace(".", "")
    # Verifica che il risultato sia esattamente 11 cifre
    if len(s) != 11 or not s.isdigit():
        raise ValueError(
            f"la partita IVA normalizzata deve avere 11 cifre, "
            f"non {s!r}"
        )
    return s
