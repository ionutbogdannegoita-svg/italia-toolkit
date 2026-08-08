"""
italia-toolkit — funzioni pure per il dominio italiano.

Codice fiscale, partita IVA, IBAN e, col tempo, il resto: validazioni e
calcoli che in Italia servono di continuo e che quasi sempre si finisce per
reimplementare male, in fretta, dentro un progetto che aveva altro da fare.

Due promesse:
  · **funzioni pure** — nessuna rete, nessun file, nessuno stato globale;
  · **nessuna dipendenza di runtime** — si installa e basta.

Ogni funzione nasce da un algoritmo ufficiale scritto in `fonti/`, con i suoi
vettori di prova. Vedi `fonti/README.md`.
"""

__version__ = "0.1.0"

from italia.partita_iva import estrai_partita_iva, valida_partita_iva

__all__ = ["__version__", "estrai_partita_iva", "valida_partita_iva"]
