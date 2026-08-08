# Changelog

Tutte le modifiche significative a questo progetto sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.1.0/) e il progetto aderisce al [Versionamento Semantico](https://semver.org/lang/it/).

## [Non rilasciato]

### Aggiunto
- Implementazione di `valida_partita_iva()` per la validazione delle partite IVA italiane
- Implementazione di `estrai_partita_iva()` per l'estrazione da testo
- Documentazione completa della fonte in `fonti/partita_iva.md`
- Test completi con tre oracoli: vettori ufficiali, Hypothesis, python-stdnum
- File `CONTRIBUTING.md` per le linee guida di contribuzione
- Type hints su tutte le funzioni pubbliche e private

### Modificato
- Esposto `valida_partita_iva` e `estrai_partita_iva` in `italia/__init__.py`

---

## [0.1.0] - 2025-01-XX

### Aggiunto
- Struttura iniziale del pacchetto
- Impalcatura di test in `tests/test_impianto.py`
- Documentazione delle fonti in `fonti/`
- README.md e ROADMAP.md
- Configurazione pyproject.toml senza dipendenze di runtime
- Licenza MIT

[Non rilasciato]: https://github.com/ionutbogdannegoita-svg/italia-toolkit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ionutbogdannegoita-svg/italia-toolkit/releases/tag/v0.1.0
