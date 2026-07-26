"""
Test per normalizza_partita_iva — riparazione cifre non-ASCII.

Fonte: fonti/partita_iva.md §1 (formato) e §5.2 (normalizzazione).

La funzione normalizza_partita_iva(numero: str) -> str
rimuove spazi, trattini, punti e prefisso IT, restituendo le 11 cifre pulite.
Solleva ValueError se il risultato non è esattamente 11 cifre decimali ASCII.

Bug T023: la versione precedente usava str.isdigit() che accetta cifre
arabo-indiane (٠١٢...) e fullwidth (０１２...), mentre la fonte §1 richiede
str.isascii() and str.isdigit().
"""

from __future__ import annotations

import pytest
from hypothesis import given, strategies as st


# ═══════════════════════════════════════════════════════════════════════
# Vettori noti-buoni — §5.2, tabella "normalizzazione"
# ═══════════════════════════════════════════════════════════════════════

NOTI_BUONI_NORMALIZZA = [
    ("00743110157", "00743110157"),       # invariato
    ("IT00743110157", "00743110157"),     # prefisso IT senza spazio
    ("IT 00743110157", "00743110157"),    # prefisso IT con spazio
    ("007-431-101-57", "00743110157"),    # trattini
    (" 00743110157 ", "00743110157"),     # spazi ai bordi
    ("007.431.101.57", "00743110157"),    # punti (§5.2 nota: li togliamo)
]


@pytest.mark.parametrize("ingresso,atteso", NOTI_BUONI_NORMALIZZA)
def test_normalizza_rimuove_spazi_trattini_punti_prefisso(
    ingresso: str, atteso: str
) -> None:
    """I formati equivalenti del §5.2 vengono normalizzati alla stringa pura."""
    from italia.partita_iva import normalizza_partita_iva
    assert normalizza_partita_iva(ingresso) == atteso


# ═══════════════════════════════════════════════════════════════════════
# Normalizzazione NON valida il checksum — §5.2
#
# La fonte dice esplicitamente: "La normalizzazione non guarda il checksum:
# '00743110158' ha la cifra di controllo sbagliata e va restituito invariato
# lo stesso. Rifiutarlo è compito di valida_partita_iva."
# ═══════════════════════════════════════════════════════════════════════

NOTI_BUONI_NO_CHECKSUM = [
    ("00743110158", "00743110158"),        # checksum errato, ma normalizza
    ("IT00743110158", "00743110158"),      # checksum errato con prefisso IT
    ("007-431-101-58", "00743110158"),     # checksum errato con trattini
    (" 00743110158 ", "00743110158"),      # checksum errato con spazi
]


@pytest.mark.parametrize("ingresso,atteso", NOTI_BUONI_NO_CHECKSUM)
def test_normalizza_non_valida_checksum(ingresso: str, atteso: str) -> None:
    """La normalizzazione non guarda il checksum: §5.2."""
    from italia.partita_iva import normalizza_partita_iva
    assert normalizza_partita_iva(ingresso) == atteso


# ═══════════════════════════════════════════════════════════════════════
# Vettori da rifiutare — §5.2, tabella "da rifiutare con ValueError"
# ═══════════════════════════════════════════════════════════════════════

NOTI_CATTIVI_VALUE_ERROR = [
    "",                # lunghezza 0
    "0074311015",      # 10 cifre
    "007431101570",    # 12 cifre
    "0074311015X",     # carattere non numerico
    "٠٠٧٤٣١١٠١٥٧",   # cifre arabo-indiane: 11 caratteri, non 0-9 (§1)
    "００７４３１１０１５７",  # cifre fullwidth: 11 caratteri, non 0-9 (§1)
]


@pytest.mark.parametrize("ingresso", NOTI_CATTIVI_VALUE_ERROR)
def test_rifiuta_ingressi_non_ascii_o_lunghezza_errata(ingresso: str) -> None:
    """Ingressi con cifre non-ASCII o lunghezza != 11 sollevano ValueError."""
    from italia.partita_iva import normalizza_partita_iva
    with pytest.raises(ValueError):
        normalizza_partita_iva(ingresso)


# ═══════════════════════════════════════════════════════════════════════
# Confini del prefisso IT — §1
#
# Casi limite sul prefisso IT: solo prefisso, prefisso + cifre non-ASCII,
# prefisso + lunghezza sbagliata. Tutti devono essere rifiutati.
# ═══════════════════════════════════════════════════════════════════════

NOTI_CATTIVI_IT_CONFINE = [
    ("IT٠٠٧٤٣١١٠١٥٧", "prefisso IT + cifre arabo-indiane (§1)"),
    ("IT００７４３１１０１５７", "prefisso IT + cifre fullwidth (§1)"),
    ("IT0074311015", "prefisso IT + 10 cifre (lunghezza sbagliata)"),
    ("IT007431101570", "prefisso IT + 12 cifre (lunghezza sbagliata)"),
    ("IT0074311015X", "prefisso IT + carattere non numerico"),
    ("IT", "solo prefisso IT, nessuna cifra"),
    ("IT ", "prefisso IT + spazio, nessuna cifra"),
    ("IT-", "prefisso IT + trattino, nessuna cifra"),
    ("IT.", "prefisso IT + punto, nessuna cifra"),
]


@pytest.mark.parametrize("ingresso,ragione", NOTI_CATTIVI_IT_CONFINE)
def test_rifiuta_prefisso_it_casi_confine(ingresso: str, ragione: str) -> None:
    """Il prefisso IT non salva ingressi con cifre non-ASCII o lunghezza errata."""
    from italia.partita_iva import normalizza_partita_iva
    with pytest.raises(ValueError):
        normalizza_partita_iva(ingresso)


# ═══════════════════════════════════════════════════════════════════════
# Solo separatori — §1
#
# Stringhe composte esclusivamente da spazi, trattini, punti o combinazioni
# di questi: dopo la pulizia diventano vuote, quindi ValueError.
# ═══════════════════════════════════════════════════════════════════════

NOTI_CATTIVI_SEPARATORI = [
    "   ",       # solo spazi
    "---",       # solo trattini
    "...",       # solo punti
    " - . ",     # mischia separatori
    "IT - . ",   # prefisso IT + separatori
]


@pytest.mark.parametrize("ingresso", NOTI_CATTIVI_SEPARATORI)
def test_rifiuta_solo_separatori(ingresso: str) -> None:
    """Solo separatori producono stringa vuota dopo pulizia → ValueError."""
    from italia.partita_iva import normalizza_partita_iva
    with pytest.raises(ValueError):
        normalizza_partita_iva(ingresso)


# ═══════════════════════════════════════════════════════════════════════
# Proprietà Hypothesis: idempotenza e forma del risultato
# ═══════════════════════════════════════════════════════════════════════


@given(st.text(min_size=11, max_size=11, alphabet="0123456789"))
def test_idempotente_su_cifre_ascii(dieci: str) -> None:
    """Normalizzare due volte lo stesso ingresso ASCII produce lo stesso risultato."""
    from italia.partita_iva import normalizza_partita_iva
    assert normalizza_partita_iva(dieci) == normalizza_partita_iva(normalizza_partita_iva(dieci))


@given(st.text(min_size=11, max_size=11, alphabet="0123456789"))
def test_risultato_e_sempre_11_cifre_ascii(dieci: str) -> None:
    """Il risultato di normalizza è sempre una stringa di 11 cifre ASCII."""
    from italia.partita_iva import normalizza_partita_iva
    risultato = normalizza_partita_iva(dieci)
    assert len(risultato) == 11
    assert risultato.isascii() and risultato.isdigit()


# ═══════════════════════════════════════════════════════════════════════
# Confronto differenziale con stdnum.it.iva.compact — §6
#
# compact toglie spazi, trattini, due punti MA NON i punti.
# Noi togliamo anche i punti (§5.2 nota). Quindi il confronto vale
# SOLO su ingressi ASCII SENZA punti.
# Le cifre non-ASCII sono fuori dal confronto: compact le accetta,
# noi le rifiutiamo (§1).
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize(
    "ingresso",
    [
        "00743110157",
        "IT00743110157",
        "IT 00743110157",
        "007-431-101-57",
        " 00743110157 ",
    ],
)
def test_coincide_con_compact_senza_punti(ingresso: str) -> None:
    """Su ingressi ASCII senza punti, coincide con stdnum.it.iva.compact."""
    from italia.partita_iva import normalizza_partita_iva
    import stdnum.it.iva as iva
    assert normalizza_partita_iva(ingresso) == iva.compact(ingresso)


@given(
    st.text(
        min_size=1, max_size=20,
        alphabet="0123456789IT -",
    ).filter(lambda s: "." not in s)
)
def test_coincide_con_compact_senza_punti_proprieta(ingresso: str) -> None:
    """Proprietà: per ogni stringa ASCII senza punti, coincide con compact."""
    from italia.partita_iva import normalizza_partita_iva
    import stdnum.it.iva as iva
    # Entrambe le funzioni accettano solo ingressi che producono 11 cifre
    try:
        nostro = normalizza_partita_iva(ingresso)
    except ValueError:
        return  # se noi rifiutiamo, non confrontiamo
    try:
        riferimento = iva.compact(ingresso)
    except Exception:
        return
    assert nostro == riferimento
