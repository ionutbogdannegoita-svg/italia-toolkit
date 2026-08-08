"""
Test per la validazione della partita IVA italiana.

Questi test verificano l'implementazione dell'algoritmo ufficiale
(DPR 605/1973, art. 4) contro i vettori di prova in fonti/partita_iva.md.

Tre oracoli:
1. Vettori ufficiali (dalla documentazione fonti/)
2. Proprietà con Hypothesis (generazione casuale)
3. Confronto differenziale con python-stdnum (oracolo di riferimento)
"""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from italia.partita_iva import estrai_partita_iva, valida_partita_iva


class TestValidaPartitaIVA_VettoriUfficiali:
    """Test basati sui vettori ufficiali in fonti/partita_iva.md"""

    @pytest.mark.parametrize(
        "partita_iva,atteso",
        [
            # Noti-BUONI — devono risultare validi
            ("00743110157", True),  # esempio svolto nella documentazione
            ("07643520567", True),
            ("13378520152", True),
            ("12345670017", True),  # confine inferiore uffici (001)
            ("99999991203", True),  # ufficio speciale 120
            ("50000008883", True),  # ufficio speciale 888
            ("00000019992", True),  # ufficio speciale 999, progressivo minimo
            # Formati equivalenti
            ("IT00743110157", True),
            ("IT 00743110157", True),
            ("007-431-101-57", True),
            (" 00743110157 ", True),
            ("007.431.101.57", True),
            ("it00743110157", True),  # case insensitive
        ],
    )
    def test_partite_iva_valide(self, partita_iva, atteso):
        assert valida_partita_iva(partita_iva) is atteso

    @pytest.mark.parametrize(
        "partita_iva,atteso,motivazione",
        [
            # Noti-CATTIVI — devono risultare invalidi
            ("00743110158", False, "cifra di controllo errata"),
            ("0074311015", False, "10 cifre"),
            ("007431101570", False, "12 cifre"),
            ("0074311015X", False, "carattere non numerico"),
            ("", False, "stringa vuota"),
            ("00000000000", False, "progressivo 0000000, mai assegnato"),
            ("00000010007", False, "ufficio 000 inesistente"),
            ("01234567897", False, "ufficio 789 inesistente"),
            ("12345678903", False, "ufficio 890 inesistente"),
            # Altri casi invalidi
            ("None", False, "stringa letterale None"),
            ("abcdefghijk", False, "lettere invece di cifre"),
            ("12345", False, "troppo corta"),
            ("IT12345", False, "prefisso IT ma troppo corta"),
        ],
    )
    def test_partite_iva_invalide(self, partita_iva, atteso, motivazione):
        assert valida_partita_iva(partita_iva) is atteso


class TestValidaPartitaIVA_Proprieta:
    """Test basati su proprietà invarianti verificate con Hypothesis"""

    @given(st.text())
    def test_input_non_stringa_o_vuoto_restituisce_false(self, testo):
        """Qualsiasi input che non sia una stringa valida di 11 cifre è falso"""
        risultato = valida_partita_iva(testo)

        # Se contiene caratteri non numerici (escluso IT prefisso), deve essere False
        pulito = testo.strip().replace(" ", "").replace("-", "").replace(".", "")
        if pulito.upper().startswith("IT"):
            pulito = pulito[2:]

        if not pulito.isdigit() or len(pulito) != 11:
            assert risultato is False

    @given(st.integers(min_value=0, max_value=10**12))
    def test_solo_checksum_corretto_passa_altri_controlli(self, numero):
        """
        Verifica che numeri casuali passino solo se soddisfano tutti i controlli.
        Questo test è più debole perché la maggior parte dei numeri casuali
        non passerà il checksum di Luhn.
        """
        candidata = str(numero).zfill(11)
        risultato = valida_partita_iva(candidata)

        # Se il risultato è True, allora deve avere:
        # 1. Lunghezza 11
        # 2. Solo cifre
        # 3. Progressivo non nullo
        # 4. Ufficio valido
        if risultato:
            assert len(candidata) == 11
            assert candidata.isdigit()
            assert candidata[:7] != "0000000"
            ufficio = int(candidata[7:10])
            uffici_validi = list(range(1, 101)) + [120, 121, 888, 999]
            assert ufficio in uffici_validi


class TestValidaPartitaIVA_ConfrontoStdnum:
    """Confronto differenziale con python-stdnum come oracolo di riferimento"""

    stdnum = pytest.importorskip("stdnum.it.iva")

    @pytest.mark.parametrize(
        "partita_iva",
        [
            "00743110157",
            "07643520567",
            "13378520152",
            "12345670017",
            "99999991203",
            "50000008883",
            "00000019992",
        ],
    )
    def test_concordanza_con_stdnum_valide(self, partita_iva):
        """Le nostre partite IVA valide devono esserlo anche per stdnum"""
        stdnum_valido = self.stdnum.is_valid(partita_iva)
        assert valida_partita_iva(partita_iva) == stdnum_valido

    @pytest.mark.parametrize(
        "partita_iva",
        [
            "00743110158",
            "00000000000",
            "00000010007",
            "01234567897",
            "12345678903",
        ],
    )
    def test_concordanza_con_stdnum_invalide(self, partita_iva):
        """Le nostre partite IVA invalide devono esserlo anche per stdnum"""
        stdnum_valido = self.stdnum.is_valid(partita_iva)
        assert valida_partita_iva(partita_iva) == stdnum_valido

    @given(
        st.builds(
            lambda p, u, c: f"{p}{u}{c}",
            st.text(st.sampled_from("0123456789"), min_size=7, max_size=7),
            st.text(st.sampled_from("0123456789"), min_size=3, max_size=3),
            st.text(st.sampled_from("0123456789"), min_size=1, max_size=1),
        )
    )
    def test_confronto_su_input_casuali(self, candidata):
        """
        Genera partite IVA casuali e confronta il risultato con stdnum.
        Entrambi devono concordare sulla validità.
        """
        stdnum_valido = self.stdnum.is_valid(candidata)
        nostro_risultato = valida_partita_iva(candidata)
        assert (
            nostro_risultato == stdnum_valido
        ), f"Disaccordo su {candidata}: noi={nostro_risultato}, stdnum={stdnum_valido}"


class TestEstraiPartitaIVA:
    """Test per la funzione di estrazione partita IVA da testo"""

    @pytest.mark.parametrize(
        "testo,atteso",
        [
            ("La P.IVA è 00743110157, grazie.", "00743110157"),
            ("Contatto: IT07643520567", "07643520567"),
            ("Fattura n.1 - P.IVA: 13378520152", "13378520152"),
            ("007-431-101-57 è valida", "00743110157"),
            ("Multiple: 00743110157 e 07643520567", "00743110157"),  # prima valida
        ],
    )
    def test_estrazione_da_testo(self, testo, atteso):
        assert estrai_partita_iva(testo) == atteso

    @pytest.mark.parametrize(
        "testo",
        [
            "Nessuna partita IVA qui",
            "Solo testo senza numeri",
            "12345 cifre a caso",
            "00000000000 invalida",  # progressivo nullo
            "01234567897 invalida",  # ufficio invalido
            "",
        ],
    )
    def test_nessuna_estrazione(self, testo):
        assert estrai_partita_iva(testo) is None
