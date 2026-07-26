"""Test per cin_codice_fiscale.

Fonte: fonti/codice_fiscale.md §7 (checksum CIN).

La funzione cin_codice_fiscale(primi15: str) -> str prende i primi 15
caratteri di un codice fiscale e restituisce il carattere di controllo
(CIN) calcolato secondo le tabelle pari/dispari del §7.

Solleva ValueError se l'ingresso non è una stringa esatta di 15
caratteri alfanumerici maiuscoli.
"""

from __future__ import annotations

import re

import pytest
from hypothesis import given, strategies as st


# ── Vettori ufficiali dal §9.0 della fonte ──────────────────────────
# Copiati così come verificati con stdnum.it.codicefiscale.calc_check_digit.

NOTI_BUONI_CIN = [
    ("RSSMRA80A01H501", "U"),
    ("MRTMTT25D09F205", "Z"),
    ("DLCNNA90B52L219", "V"),
    ("FOXDAA00T71H501", "U"),
    ("MLLSNT82P65Z404", "U"),
    ("RSSMRA85M00H501", "R"),
]

INGRESSI_RIFIUTATI = [
    "",
    "RSSMRA80A01H50",       # 14 caratteri
    "RSSMRA80A01H501U",     # 16 caratteri
    "rssmra80a01h501",      # minuscole
    "RSSMRA80A01H50!",      # carattere non alfanumerico
    "RSSMRA80A01H50 ",      # spazio in coda
]


class TestVettoriCin:
    """Casi noti dal §9.0 della fonte."""

    @pytest.mark.parametrize("primi15,atteso", NOTI_BUONI_CIN)
    def test_calcola_cin_corretto(self, primi15: str, atteso: str):
        from italia.codice_fiscale import cin_codice_fiscale
        assert cin_codice_fiscale(primi15) == atteso

    @pytest.mark.parametrize("ingresso", INGRESSI_RIFIUTATI)
    def test_rifiuta_ingressi_invalidi(self, ingresso: str):
        from italia.codice_fiscale import cin_codice_fiscale
        with pytest.raises(ValueError):
            cin_codice_fiscale(ingresso)


class TestConfrontoStdnum:
    """Confronto differenziale con python-stdnum — §10 della fonte."""

    @pytest.mark.parametrize("primi15,atteso", NOTI_BUONI_CIN)
    def test_corrisponde_a_stdnum(self, primi15: str, atteso: str):
        from stdnum.it import codicefiscale
        from italia.codice_fiscale import cin_codice_fiscale
        stdnum_result = codicefiscale.calc_check_digit(primi15)
        assert stdnum_result == atteso
        assert cin_codice_fiscale(primi15) == stdnum_result


class TestProprietaCin:
    """Proprietà che cin_codice_fiscale deve soddisfare."""

    @given(st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", min_size=15, max_size=15))
    def test_restituisce_una_sola_lettera(self, primi15: str):
        """Il risultato è sempre una lettera maiuscola A-Z."""
        from italia.codice_fiscale import cin_codice_fiscale
        risultato = cin_codice_fiscale(primi15)
        assert len(risultato) == 1
        assert risultato.isupper() and risultato.isalpha()

    @given(st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", min_size=15, max_size=15))
    def test_riproposta_deterministica(self, primi15: str):
        """Due chiamate con lo stesso input danno lo stesso output."""
        from italia.codice_fiscale import cin_codice_fiscale
        assert cin_codice_fiscale(primi15) == cin_codice_fiscale(primi15)
