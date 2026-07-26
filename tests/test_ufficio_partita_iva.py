"""
Test per ufficio_partita_iva.

Fonte: fonti/partita_iva.md §3 (codice ufficio) e §3.1 (vettori di confine).

La funzione ufficio_partita_iva(partita_iva: str) -> str
prende una P.IVA di 11 cifre normalizzata, ne guarda le cifre 8-10 (codice
ufficio) e restituisce 'provinciale' per 001-100, 'speciale' per 120/121/888/999.
Su qualunque altro codice solleva ValueError.
"""

from __future__ import annotations

import pytest
from hypothesis import given, strategies as st


# ═══════════════════════════════════════════════════════════════════════
# Vettori di confine §3.1 — AMMESSI
# ═══════════════════════════════════════════════════════════════════════

UFFICIO_AMMESSI = [
    # (partita_iva_11_cifre, codice_ufficio, risultato_atteso)
    ("12345670017", "001", "provinciale"),   # primo ufficio provinciale
    ("00743110027", "002", "provinciale"),   # da 00743110157, ufficio 002
    ("00743110097", "099", "provinciale"),   # da 00743110157, ufficio 099
    ("00743111007", "100", "provinciale"),   # ultimo provinciale, incluso
    ("99999991203", "120", "speciale"),      # Direzione Centrale Accertamento
    ("00743111217", "121", "speciale"),      # soggetti identificati direttamente
    ("50000008883", "888", "speciale"),      # enti non residenti / casi particolari
    ("00000019992", "999", "speciale"),      # soggetti non residenti
]


@pytest.mark.parametrize("piuva,ufficio,atteso", UFFICIO_AMMESSI)
def test_riconosce_uffici_ammessi(piuva: str, ufficio: str, atteso: str) -> None:
    """Gli uffici ammessi (001-100, 120, 121, 888, 999) restituiscono il nome."""
    from italia.partita_iva import ufficio_partita_iva
    assert ufficio_partita_iva(piuva) == atteso


# ── Casi RIFIUTATI (ValueError) per codice ufficio non ammesso ──────

UFFICIO_RIFIUTATI = [
    ("00743110007", "000"),   # sotto il primo ufficio
    ("00743111017", "101"),   # primo escluso dopo intervallo provinciale
    ("00743111197", "119"),   # ultimo escluso prima dei speciali
    ("00743111227", "122"),   # primo escluso dopo i due speciali
    ("00743118877", "887"),   # ultimo escluso prima di 888
    ("00743118897", "889"),   # primo escluso dopo 888
    ("00743119987", "998"),   # ultimo escluso prima di 999
]


@pytest.mark.parametrize("piuva,ufficio", UFFICIO_RIFIUTATI)
def test_rifiuta_ufficio_inesistente_anche_col_checksum_giusto(
    piuva: str, ufficio: str
) -> None:
    """Un codice ufficio non ammesso solleva ValueError."""
    from italia.partita_iva import ufficio_partita_iva
    with pytest.raises(ValueError):
        ufficio_partita_iva(piuva)


# ── Proprietà: solo gli uffici ammessi sono accettati ────────────────

PROVINCIALI = [f"{i:03d}" for i in range(1, 101)]
SPECIALI = ["120", "121", "888", "999"]
TUTTI_AMMESSI = PROVINCIALI + SPECIALI


@given(st.sampled_from(TUTTI_AMMESSI))
def test_qualunque_ufficio_ammesso_riconosciuto(ufficio: str) -> None:
    """Qualsiasi codice ufficio ammesso produce 'provinciale' o 'speciale'."""
    from italia.partita_iva import ufficio_partita_iva
    # Costruisco una P.IVA fittizia con questo ufficio
    piuva = "0000000" + ufficio + "0"
    risultato = ufficio_partita_iva(piuva)
    assert risultato in ("provinciale", "speciale")


@given(st.integers(min_value=0, max_value=999))
def test_ufficio_non_ammesso_solleva_value_error(codice: int) -> None:
    """Un codice ufficio non nella lista ammessa solleva ValueError."""
    from italia.partita_iva import ufficio_partita_iva
    if codice in (1, 2, 99, 100, 120, 121, 888, 999):
        pytest.skip("codice ammesso: non deve sollevare")
    piuva = "0000000" + f"{codice:03d}" + "0"
    with pytest.raises(ValueError):
        ufficio_partita_iva(piuva)


# ═══════════════════════════════════════════════════════════════════════
# Riparazione T024: cifre non-ASCII → errore di FORMATO, non ufficio
# ═══════════════════════════════════════════════════════════════════════

# La correzione aggiunge isascii() al controllo di formato in cima.
# Senza di essa, su '٠٠٧٤٣١١٠١٥٧' (cifre arabo-indiane) il controllo
# passa (isdigit() dice True) e si arriva al confronto dell'ufficio,
# sollevando ValueError con messaggio "codice ufficio non ammesso"
# invece che l'errore di formato "11 cifre decimali ASCII".


def test_cifre_arabo_indiane_sollevano_valuerror_formato() -> None:
    """Cifre arabo-indiane: l'errore è di formato, non di codice ufficio."""
    from italia.partita_iva import ufficio_partita_iva
    # 11 caratteri, isdigit() dice True ma non sono 0-9 ASCII
    arabo_indiano = "٠٠٧٤٣١١٠١٥٧"
    with pytest.raises(ValueError, match="11"):
        ufficio_partita_iva(arabo_indiano)


def test_cifre_fullwidth_sollevano_valuerror_formato() -> None:
    """Cifre fullwidth: l'errore è di formato, non di codice ufficio."""
    from italia.partita_iva import ufficio_partita_iva
    fullwidth = "００７４３１１０１５７"
    with pytest.raises(ValueError, match="11"):
        ufficio_partita_iva(fullwidth)
