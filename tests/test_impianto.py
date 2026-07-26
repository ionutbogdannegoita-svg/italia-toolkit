"""
Prova d'impianto — non giudica algoritmi, giudica l'impalcatura.

Se questo file diventa rosso non è un bug di dominio: è il pacchetto che non
si importa, una dipendenza sparita, o una fonte ufficiale cancellata da
`fonti/`. Gli algoritmi hanno i loro test, scritti dall'Architetto, altrove.

L'ultimo gruppo è il più importante: `fonti/` è l'oracolo del progetto.
Se una fonte sparisce, il loop resta senza autorità e comincerebbe a inventare.
Meglio che se ne accorga la CI, subito, e non un umano fra tre settimane.
"""

from __future__ import annotations

from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parent.parent
FONTI = RADICE / "fonti"

# Le fonti che devono esistere, e una stringa che deve comparirci dentro:
# non basta che il file ci sia, deve contenere ancora l'algoritmo.
FONTI_ATTESE = {
    "codice_fiscale.md": "A B C D E H L M P R S T",
    "partita_iva.md": "10 − (T mod 10)",
    "iban.md": "MOD 97-10",
    "README.md": "l'oracolo",
}


class TestPacchetto:
    def test_il_pacchetto_si_importa(self):
        import italia
        assert italia is not None

    def test_dichiara_la_versione(self):
        import italia
        assert italia.__version__.count(".") == 2


class TestDipendenzeDiTest:
    """I tre oracoli hanno bisogno di questi due, o non sono oracoli."""

    def test_hypothesis_disponibile(self):
        import hypothesis
        assert hypothesis.given is not None

    def test_libreria_di_riferimento_disponibile(self):
        from stdnum.it import iva
        assert iva.validate("00743110157") == "00743110157"

    def test_la_libreria_di_riferimento_non_e_una_dipendenza_di_runtime(self):
        """
        `python-stdnum` è il secondo parere nei test, non un pezzo della
        libreria. Se finisse in `[project.dependencies]` staremmo spacciando
        per nostro il lavoro di qualcun altro — e distribuendo una dipendenza
        a chi installa il pacchetto.
        """
        testo = (RADICE / "pyproject.toml").read_text(encoding="utf-8")
        prima = testo.split("[project.optional-dependencies]")[0]
        assert "stdnum" not in prima


class TestOracolo:
    @pytest.mark.parametrize("nome,impronta", sorted(FONTI_ATTESE.items()))
    def test_ogni_fonte_esiste_e_contiene_ancora_l_algoritmo(self, nome, impronta):
        percorso = FONTI / nome
        assert percorso.is_file(), f"fonte sparita: fonti/{nome}"
        assert impronta in percorso.read_text(encoding="utf-8"), (
            f"fonti/{nome} esiste ma non contiene più {impronta!r}"
        )

    def test_le_fonti_non_sono_segnaposto_vuoti(self):
        for nome in FONTI_ATTESE:
            assert len((FONTI / nome).read_text(encoding="utf-8")) > 1000

    def test_nessuna_fonte_a_sorpresa(self):
        """
        Una fonte in più che nessuno ha dichiarato è una fonte che nessun test
        sorveglia: o la si mette in FONTI_ATTESE, o non sta in `fonti/`.
        """
        trovate = {f.name for f in FONTI.glob("*.md")}
        assert trovate == set(FONTI_ATTESE), (
            f"non dichiarate: {trovate - set(FONTI_ATTESE)}"
        )
