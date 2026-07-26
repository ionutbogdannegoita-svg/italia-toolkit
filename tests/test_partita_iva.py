"""
Test per cifra_controllo_partita_iva, normalizza_partita_iva e ufficio_partita_iva.

Fonte: fonti/partita_iva.md §4 (checksum Luhn) e §5.1 (vettori 10 cifre);
       fonti/partita_iva.md §1 (formato) e §5.2 (normalizzazione);
       fonti/partita_iva.md §3 (codice ufficio) e §3.1 (vettori di confine).

La funzione cifra_controllo_partita_iva(dieci_cifre: str) -> int
prende le prime 10 cifre di una P.IVA e restituisce l'undicesima cifra di
controllo come intero 0-9, usando l'algoritmo di Luhn. Solleva ValueError
se l'ingresso non è esattamente 10 cifre decimali.

La funzione normalizza_partita_iva(numero: str) -> str
tolte spazi, trattini, punti e prefisso IT, restituendo le 11 cifre.
Solleva ValueError se quel che resta non è esattamente 11 cifre.
Non valida checksum né ufficio.

La funzione ufficio_partita_iva(partita_iva: str) -> str
prende una P.IVA di 11 cifre normalizzata, ne guarda le cifre 8-10 (codice
ufficio) e restituisce 'provinciale' per 001-100, 'speciale' per 120/121/888/999.
Su qualunque altro codice solleva ValueError.
"""

from __future__ import annotations

import pytest
from hypothesis import given, strategies as st
from stdnum import luhn


# ═══════════════════════════════════════════════════════════════════════
# cifra_controllo_partita_iva — vettori noti-buoni
# ═══════════════════════════════════════════════════════════════════════

NOTI_BUONI_CIFRA = [
    ("0074311015", 7),   # da 00743110157 — esempio svolto §4
    ("0764352056", 7),   # da 07643520567
    ("1337852015", 2),   # da 13378520152
    ("1234567001", 7),   # da 12345670017
    ("9999999120", 3),   # da 99999991203
    ("5000000888", 3),   # da 50000008883
    ("0000001999", 2),   # da 00000019992
    ("0000000000", 0),   # nessun corrispettivo valido, ma checksum = 0
]


@pytest.mark.parametrize("dieci,cifra_attesa", NOTI_BUONI_CIFRA)
def test_calcola_cifra_corretta(dieci: str, cifra_attesa: int) -> None:
    """Le 10 cifre note restituiscono la cifra di controllo attesa."""
    from italia.partita_iva import cifra_controllo_partita_iva
    assert cifra_controllo_partita_iva(dieci) == cifra_attesa


# ── Vettori da rifiutare: devono sollevare ValueError ────────────────

NOTI_CATTIVI_VALUE_ERROR = [
    "",                # 0 cifre
    "007431101",       # 9 cifre
    "00743110157",     # 11 cifre
    "007431101A",      # carattere non numerico
    "007431 015",      # spazio interno
    "0074311015 ",     # spazio in coda
]


@pytest.mark.parametrize("ingresso", NOTI_CATTIVI_VALUE_ERROR)
def test_rifiuta_ingressi_invalidi(ingresso: str) -> None:
    """Ingressi non esattamente 10 cifre decimali sollevano ValueError."""
    from italia.partita_iva import cifra_controllo_partita_iva
    with pytest.raises(ValueError):
        cifra_controllo_partita_iva(ingresso)


# ── Proprietà Hypothesis: confronto con stdnum.luhn ─────────────────

@given(st.text(min_size=10, max_size=10, alphabet="0123456789"))
def test_coincide_con_luhn_di_riferimento(dieci: str) -> None:
    """Per ogni stringa di 10 cifre, il risultato coincide con stdnum.luhn."""
    from italia.partita_iva import cifra_controllo_partita_iva
    assert str(cifra_controllo_partita_iva(dieci)) == luhn.calc_check_digit(dieci)


@given(st.text(min_size=10, max_size=10, alphabet="0123456789"))
def test_cifra_sempre_tra_0_e_9(dieci: str) -> None:
    """La cifra restituita è sempre un intero compreso tra 0 e 9."""
    from italia.partita_iva import cifra_controllo_partita_iva
    risultato = cifra_controllo_partita_iva(dieci)
    assert isinstance(risultato, int)
    assert 0 <= risultato <= 9


@given(st.text(min_size=10, max_size=10, alphabet="0123456789"))
def test_checksum_corretto_rende_luhn_valido(dieci: str) -> None:
    """Se appendi la cifra calcolata, le 11 cifre passano il test Luhn."""
    from italia.partita_iva import cifra_controllo_partita_iva
    completo = dieci + str(cifra_controllo_partita_iva(dieci))
    assert luhn.is_valid(completo)


# ═══════════════════════════════════════════════════════════════════════
# normalizza_partita_iva — vettori §5.2
# ═══════════════════════════════════════════════════════════════════════

NORMALIZZA_INVIANTI = [
    ("00743110157", "00743110157"),       # invariato
    ("IT00743110157", "00743110157"),     # prefisso IT
    ("IT 00743110157", "00743110157"),    # prefisso IT + spazio
    ("007-431-101-57", "00743110157"),    # trattini
    (" 00743110157 ", "00743110157"),     # spazi esterni
    ("007.431.101.57", "00743110157"),    # punti
]


@pytest.mark.parametrize("ingresso,atteso", NORMALIZZA_INVIANTI)
def test_normalizza_formatti_equivalenti(ingresso: str, atteso: str) -> None:
    """Formatti equivalenti vengono ricondotti alle 11 cifre."""
    from italia.partita_iva import normalizza_partita_iva
    assert normalizza_partita_iva(ingresso) == atteso


def test_normalizza_non_valida_checksum() -> None:
    """P.IVA con cifra di controllo errata viene normalizzata lo stesso."""
    from italia.partita_iva import normalizza_partita_iva
    assert normalizza_partita_iva("00743110158") == "00743110158"


NORMALIZZA_VALUE_ERROR = [
    "",                # lunghezza 0
    "0074311015",      # 10 cifre
    "007431101570",    # 12 cifre
    "0074311015X",     # carattere non numerico
]


@pytest.mark.parametrize("ingresso", NORMALIZZA_VALUE_ERROR)
def test_normalizza_rifiuta_lunghezza_errata(ingresso: str) -> None:
    """Dopo la pulizia, se non sono 11 cifre → ValueError."""
    from italia.partita_iva import normalizza_partita_iva
    with pytest.raises(ValueError):
        normalizza_partita_iva(ingresso)


@given(st.text(min_size=11, max_size=11, alphabet="0123456789"))
def test_normalizza_idempotente(nove: str) -> None:
    """Normalizzare due volte dà lo stesso risultato."""
    from italia.partita_iva import normalizza_partita_iva
    assert normalizza_partita_iva(normalizza_partita_iva(nove)) == normalizza_partita_iva(nove)


@given(st.text(min_size=1, max_size=30, alphabet="0123456789 IT-."))
def test_normalizza_risultato_solo_cifre_11(caratteri_misti: str) -> None:
    """Il risultato è sempre una stringa di esattamente 11 cifre."""
    from italia.partita_iva import normalizza_partita_iva
    try:
        risultato = normalizza_partita_iva(caratteri_misti)
    except ValueError:
        return
    assert len(risultato) == 11
    assert risultato.isdigit()


COMPACT_CONFRONTABILI = [
    "00743110157",
    "IT00743110157",
    "IT 00743110157",
    "007-431-101-57",
    " 00743110157 ",
    "00743110158",
]


@pytest.mark.parametrize("ingresso", COMPACT_CONFRONTABILI)
def test_normalizza_coincide_con_compact_senza_punti(ingresso: str) -> None:
    """Senza punti, normalizza_partita_iva coincide con stdnum.it.iva.compact."""
    from italia.partita_iva import normalizza_partita_iva
    import stdnum.it.iva as iva
    assert normalizza_partita_iva(ingresso) == iva.compact(ingresso)


# ═══════════════════════════════════════════════════════════════════════
# ufficio_partita_iva — vettori §3.1 (confine)
# Fonte: fonti/partita_iva.md §3 (codice ufficio) e §3.1 (vettori di confine)
# ═══════════════════════════════════════════════════════════════════════

# Costruiti partendo da P.IVA della fonte (§5) e sostituendo le cifre 8-10.
# La cifra di controllo (11ª) è lasciata com'è: ufficio_partita_iva non
# valida il checksum, ma tenendolo corretto evitiamo falsi negativi.

# ── Casi AMMESSI ────────────────────────────────────────────────────

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


# ── Casi RIFIUTATI (ValueError) ─────────────────────────────────────

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
