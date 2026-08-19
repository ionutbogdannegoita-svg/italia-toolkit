# Template per Pull Request

<!-- 
Questo template guida la review. Non è burocrazia: aiuta chi revisiona 
a capire subito cosa c'è da guardare e perché.
-->

## Cosa fa questa PR

<!-- Una riga: qual è l'obiettivo? -->

## Task / Issue di riferimento

<!-- Se c'è un task della ROADMAP o una issue, citla qui -->

## Tipo di modifica

- [ ] Nuova funzione
- [ ] Bug fix
- [ ] Refactoring (stesso comportamento, codice diverso)
- [ ] Test nuovi o modificati
- [ ] Documentazione
- [ ] Altro: _______

## Come è stato testato

<!-- 
Descrivi brevemente:
- Vettori ufficiali usati (se applicabile)
- Property-based test aggiunti
- Confronto differenziale con python-stdnum
-->

## Checklist pre-review

- [ ] `pytest` è verde localmente
- [ ] Le guardie sul diff passano (se ho modificato codice)
- [ ] Il diff sta sotto i tetti (150 righe, 3 file) — se no, ho spezzato il task
- [ ] Ho citato la fonte corretta nella spec/docstring
- [ ] Nessuna dipendenza runtime aggiunta

## Note per il reviewer

<!-- Punti specifici su cui vuoi feedback, dubbi rimasti, decisioni prese -->

---

**Se questa PR viene dal turno notturno:** il rapporto completo è nel primo commento della PR. Controlla soprattutto i test scartati e le motivazioni.
