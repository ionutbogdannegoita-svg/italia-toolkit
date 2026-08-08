# Contribuire a italia-toolkit

Grazie per voler contribuire a **italia-toolkit**! Questo documento spiega come farlo nel modo corretto.

## Filosofia del progetto

1. **Funzioni pure**: nessuna rete, nessun file, nessuno stato globale.
2. **Nessuna dipendenza di runtime**: la libreria deve funzionare "out of the box".
3. **Fonti prima del codice**: ogni funzione nasce da un algoritmo ufficiale in `fonti/`.
4. **Test come oracoli**: tre fonti di verità — vettori ufficiali, proprietà con Hypothesis, confronto con `python-stdnum`.

## Come aggiungere una nuova funzione

### 1. Scegliere il dominio

Consulta la [`ROADMAP.md`](ROADMAP.md) per vedere cosa è già implementato e cosa manca.

### 2. Scrivere la fonte

Crea o aggiorna un file in `fonti/` con:
- Riferimento normativo ufficiale
- Algoritmo passo-passo
- Vettori di prova (validi e invalidi)
- Casi limite documentati

Esempio: `fonti/codice_fiscale.md`

### 3. Implementare la funzione

Crea un modulo in `italia/` con:
- Type hints completi
- Docstring dettagliata con esempi
- Funzioni helper private (prefisso `_`)
- Gestione robusta degli input

### 4. Esporre nel pacchetto

Aggiungi le esportazioni in `italia/__init__.py`:
```python
from italia.tua_funzione import tua_funzione

__all__ = [..., "tua_funzione"]
```

### 5. Scrivere i test

Crea `tests/test_tua_funzione.py` con tre sezioni:
1. **Vettori ufficiali**: tutti i casi da `fonti/`
2. **Proprietà con Hypothesis**: test generativi
3. **Confronto con stdnum**: se applicabile

### 6. Aggiornare la documentazione

- README.md con esempio d'uso
- ROADMAP.md segnando il completamento
- Eventualmente esempi avanzati

## Standard di codice

### Formattazione
- Usa **Black** per la formattazione automatica
- Usa **Ruff** per i linting veloce
- Massimo 88 caratteri per riga (default Black)

### Type hints
- Obbligatori su tutte le funzioni pubbliche e private
- Usa `from __future__ import annotations` per forward references
- Preferisci `str | None` a `Optional[str]` (Python 3.10+)

### Nomenclatura
- Funzioni pubbliche: `nome_funzione()` (snake_case)
- Funzioni private: `_nome_funzione()` (prefisso underscore)
- Costanti: `NOME_COSTANTE` (UPPER_CASE)
- Classi: `NomeClasse` (PascalCase)

### Documentazione
- Docstring obbligatoria per ogni funzione pubblica
- Formato Google o NumPy
- Includi almeno un esempio nel docstring
- Spiega i casi limite e le eccezioni

## Workflow di sviluppo

```bash
# 1. Fork e clona
git clone https://github.com/tuo-username/italia-toolkit
cd italia-toolkit

# 2. Ambiente virtuale
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 3. Installa dipendenze di sviluppo
pip install -e ".[dev]"

# 4. Crea un branch
git checkout -b feature/tua-funzionalita

# 5. Sviluppa e testa
python -m pytest tests/ -v

# 6. Formatta e linta
black italia/ tests/
ruff check italia/ tests/

# 7. Commit e push
git add .
git commit -m "feat: aggiungi valida_codice_fiscale"
git push origin feature/tua-funzionalita

# 8. Pull Request su GitHub
```

## Commit convention

Segui [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` nuova funzionalità
- `fix:` correzione bug
- `docs:` documentazione
- `style:` formattazione (nessun impatto sul codice)
- `refactor:` refactoring (nessun cambiamento comportamentale)
- `test:` aggiunta/modifica test
- `chore:` manutenzione (dipendenze, CI, ecc.)

Esempi:
```
feat: aggiungi valida_codice_fiscale
fix: correggi checksum per IBAN con spazi
docs: aggiungi esempi nel README
test: aggiungi vettori per ufficio 121
```

## Linee guida per i test

### Copertura minima
- Tutti i vettori ufficiali devono essere testati
- Almeno 3 test di proprietà con Hypothesis
- Confronto con stdnum se esiste equivalente

### Naming dei test
```python
def test_descrizione_chiara(self, ...):
```

### Assert
- Usa `assert risultato is atteso` per booleani
- Usa `assert risultato == valore_atteso` per valori
- Messaggi di errore chiari nei test complessi

### Hypothesis
```python
@given(st.test_strategy())
def test_proprieta(self, input_generato):
    # Verifica invarianti
    assert proprieta(input_generato)
```

## Review process

1. **CI verde**: tutti i test devono passare
2. **Code review**: almeno un maintainer approva
3. **No breaking changes**: senza major version bump
4. **Documentazione aggiornata**: README e docstring

## Domande frequenti

### Posso usare dipendenze esterne?
**No**, tranne nella standard library. Le dipendenze sono ammesse solo in `[dev]` per i test.

### Come gestisco gli encoding?
Assumi sempre **UTF-8** per file di testo e stringhe in input.

### Devo supportare Python < 3.11?
**No**, il progetto richiede Python 3.11+.

### Posso aggiungere funzioni non pure?
**No**, violerebbe la filosofia del progetto. Funzioni che richiedono rete o I/O vanno in un pacchetto separato.

## Contatti

- GitHub Issues: per bug report e feature request
- GitHub Discussions: per domande e confronti

Grazie per contribuire a rendere italia-toolkit lo standard per le validazioni italiane in Python! 🇮🇹
