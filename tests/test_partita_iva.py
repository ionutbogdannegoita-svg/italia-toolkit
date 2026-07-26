"""
Test per cifra_controllo_partita_iva.

Fonte: fonti/partita_iva.md §4 (checksum Luhn) e §5.1 (vettori 10 cifre).

La funzione presa_cifra_controllo_partita_iva(dieci_cifre: str) -> int
prende le prime 10 cifre di una P.IVA e restituisce l'undicesima cifra di
controllo come intero 0-9, usando l'algoritmo di Luhn. Solleva ValueError
se l'ingresso non è esattamente 10 cifre decimali.
"""

from __future__ import annotations

import pytest
from hypothesis import given, strategies as st
from stdnum import luhn


# ── Vettori noti-buoni: 10 cifre → cifra attesa ──────────────────────
# Derivati da fonti/partita_iva.md §5.1, verificati con stdnum.luhn.calc_check_digit.

NOTI_BUONI = [
    ("0074311015", 7),   # da 00743110157 — esempio svolto §4
    ("0764352056", 7),   # da 07643520567
    ("1337852015", 2),   # da 13378520152
    ("1234567001", 7),   # da 12345670017
    ("9999999120", 3),   # da 99999991203
    ("5000000888", 3),   # da 50000008883
    ("0000001999", 2),   # da 00000019992
    ("0000000000", 0),   # nessun corrispettivo valido, ma checksum = 0
]


@pytest.mark.parametrize("dieci,cifra_attesa", NOTI_BUONI)
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


# ── Proprietà: la cifra è sempre un intero 0-9 ─────────────────────

@given(st.text(min_size=10, max_size=10, alphabet="0123456789"))
def test_cifra_sempre_tra_0_e_9(dieci: str) -> None:
    """La cifra restituita è sempre un intero compreso tra 0 e 9."""
    from italia.partita_iva import cifra_controllo_partita_iva
    risultato = cifra_controllo_partita_iva(dieci)
    assert isinstance(risultato, int)
    assert 0 <= risultato <= 9


# ── Proprietà: aggiungere la cifra giusta rende le 11 cifre valide per Luhn ──

@given(st.text(min_size=10, max_size=10, alphabet="0123456789"))
def test_checksum_corretto_rende_luhn_valido(dieci: str) -> None:
    """Se appendi la cifra calcolata, le 11 cifre passano il test Luhn."""
    from italia.partita_iva import cifra_controllo_partita_iva
    completo = dieci + str(cifra_controllo_partita_iva(dieci))
    assert luhn.is_valid(completo)
