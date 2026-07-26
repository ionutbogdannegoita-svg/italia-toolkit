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
