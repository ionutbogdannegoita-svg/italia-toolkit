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

    Solleva ValueError se l'ingresso non è esattamente 10 cifre decimali ASCII.
    """
    if len(dieci_cifre) != 10 or not dieci_cifre.isascii() or not dieci_cifre.isdigit():
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
    if len(s) != 11 or not s.isascii() or not s.isdigit():
        raise ValueError(
            f"la partita IVA normalizzata deve avere 11 cifre, "
            f"non {s!r}"
        )
    return s


def ufficio_partita_iva(partita_iva: str) -> str:
    """
    Restituisce il tipo di ufficio che ha attribuito la partita IVA.

    Prende una P.IVA di 11 cifre già normalizzata, ne guarda le cifre 8-10
    (codice ufficio) e restituisce 'provinciale' per i codici da 001 a 100
    inclusi, oppure 'speciale' per 120, 121, 888 e 999.
    Su qualunque altro codice solleva ValueError.

    Fonte: `fonti/partita_iva.md` §3 (codice ufficio) e §3.1 (vettori di confine).

        >>> ufficio_partita_iva("00743110157")
        'provinciale'
        >>> ufficio_partita_iva("99999991203")
        'speciale'
        >>> ufficio_partita_iva("00743110007")
        Traceback (most recent call last):
        ...
        ValueError: codice ufficio '000' non ammesso
    """
    if len(partita_iva) != 11 or not partita_iva.isascii() or not partita_iva.isdigit():
        raise ValueError(
            f"partita IVA deve essere 11 cifre, non {partita_iva!r}"
        )

    codice = partita_iva[7:10]

    # Uffici provinciali: 001-100 inclusi
    if "001" <= codice <= "100":
        return "provinciale"

    # Uffici speciali
    if codice in ("120", "121", "888", "999"):
        return "speciale"

    raise ValueError(f"codice ufficio {codice!r} non ammesso")


def valida_partita_iva(numero: str) -> bool:
    """
    Dice se `numero` è una partita IVA formalmente valida.

    Fonte: `fonti/partita_iva.md` §1 (formato), §2 (progressivo),
           §3 (codice ufficio), §4 (checksum Luhn).

        >>> valida_partita_iva("00743110157")
        True
        >>> valida_partita_iva("00743110158")
        False
        >>> valida_partita_iva("00000000000")
        False
    """
    try:
        piva = normalizza_partita_iva(numero)
    except ValueError:
        return False

    # §2: progressivo (cifre 1-7) non può essere 0000000
    if piva[:7] == "0000000":
        return False

    # §3: codice ufficio (cifre 8-10) deve essere ammesso
    try:
        ufficio_partita_iva(piva)
    except ValueError:
        return False

    # §4: checksum Luhn sulle prime 10 cifre
    if cifra_controllo_partita_iva(piva[:10]) != int(piva[10]):
        return False

    return True
