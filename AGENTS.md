# AGENTS.md — regole per chi scrive questo codice senza sorveglianza

Questa libreria la costruisce un modello che lavora 24 ore su 24, senza
nessuno che guardi. Il titolare rivede quando gli va. Qui ci sono le regole
del cantiere.

Questo file è in `PERCORSI_VIETATI`: **il loop non può riscriverlo.** Non è
sfiducia, è progettazione — un sistema che può cambiare le proprie regole non
ha regole.

---

## 1. Cos'è questa libreria

Funzioni **pure** per il dominio italiano. Pura significa, senza sconti:

- nessuna rete, nessun file, nessun orologio, nessun `random`;
- nessuno stato globale, nessuna variabile di modulo che cambi;
- stessi argomenti ⇒ stesso risultato, oggi e fra dieci anni;
- **nessuna dipendenza di runtime.** `[project.dependencies]` è vuoto e resta
  vuoto. `python-stdnum` esiste solo nei test.

Se un task sembra chiedere una chiamata di rete o una tabella che invecchia,
il task è scritto male: fermarsi e segnalarlo, non arrangiarsi.

## 2. La separazione dei poteri

Quattro ruoli. I divieti li applica il codice (`officina/guardie.py`), non la
tua buona volontà: se provi lo stesso, il diff viene bocciato e il lavoro
buttato.

| ruolo | produce | non può toccare |
|---|---|---|
| **Architetto** | spec + test di accettazione, **prima** del codice | i file sorgente |
| **Operaio** | l'implementazione che fa passare i test | **i file di test** |
| **Collaudatore** | test avversari contro codice già accettato | i file sorgente |
| **Ispettore** | qualità e sicurezza | tutto: propone soltanto |

Il senso è uno solo: **chi scrive il codice non scrive l'esame.** Un modello
che può fare entrambe le cose, prima o poi, ammorbidisce l'esame. Non per
malizia — perché è la strada più breve verso il verde.

## 3. Le fonti sono l'autorità

Ogni funzione nasce da un file di [`fonti/`](fonti/README.md), citato **per
nome e per paragrafo** nella spec.

- **Una spec senza fonte è nulla.** Il task viene annullato, non discusso.
- La fonte vince sempre: se ricordi l'algoritmo diversamente da come è scritto
  lì, **ricordi male**. La fonte è stata verificata a mano contro
  `python-stdnum` prima di essere scritta.
- Non esiste la fonte per il dominio che ti serve? Il task **non si fa**.
  Si segnala che manca. Non la si scrive: `fonti/` è vietato in scrittura.

## 4. Come si scrive il codice

- **Italiano** per nomi pubblici, docstring e commenti. `valida_partita_iva`,
  non `validate_vat`. È una libreria di dominio italiano: chi la usa pensa in
  italiano.
- **Una funzione, una cosa.** Se il nome ha una "e" dentro, sono due funzioni.
- **Type hints ovunque** sulle funzioni pubbliche.
- **Docstring con un esempio eseguibile** e il riferimento alla fonte:

  ```python
  def valida_partita_iva(numero: str) -> bool:
      """
      Dice se `numero` è una partita IVA formalmente valida.

      Fonte: `fonti/partita_iva.md` §4 (checksum Luhn) e §3 (codice ufficio).

          >>> valida_partita_iva("00743110157")
          True
          >>> valida_partita_iva("00743110158")
          False
      """
  ```

- **Errori:** `ValueError` per un ingresso malformato quando la funzione deve
  restituire un valore; `False` quando la funzione è una domanda sì/no.
  Le `valida_*` non sollevano mai: rispondono `True` o `False`.
- **Niente astrazioni speculative.** Nessuna classe dove basta una funzione,
  nessun parametro "per il futuro". Il futuro è nella ROADMAP, non nel codice.
- **Vietati dal codice, non dal buon senso:** `eval`, `exec`, `os.system`,
  `subprocess` con `shell=True`, `pickle`, `__import__`, `verify=False`.
  La guardia li blocca sul diff.

## 5. Come si scrivono i test

- In `tests/`, un file per modulo: `tests/test_partita_iva.py`.
- **Prima i vettori ufficiali** della fonte: noti-buoni e noti-cattivi, tutti,
  copiati esattamente. Sono l'oracolo #2.
- Poi le **proprietà** con Hypothesis (oracolo #3). Esempi di proprietà vere:
  - un numero generato con la cifra di controllo giusta è sempre valido;
  - cambiare una cifra qualsiasi lo rende quasi sempre invalido;
  - `normalizza(normalizza(x)) == normalizza(x)`.
- Poi il **confronto differenziale** con `python-stdnum` su input casuali,
  **dove il riferimento è applicabile**. Non lo è per
  `valida_iban_italiano`: siamo più severi, `stdnum` non controlla il CIN
  (vedi `fonti/iban.md` §5).
- **Un test deve poter fallire.** Se passa anche con la funzione bersaglio
  rotta di proposito, è un test-fuffa e viene buttato. Il controllo è
  automatico: il loop rompe la funzione e rilancia il test.
- Nomi in italiano, che dicono il comportamento:
  `test_rifiuta_ufficio_inesistente_anche_col_checksum_giusto`.

## 6. Il cricchetto

Si lavora sul branch **`sviluppo`**. Su `main` non si scrive mai.

Si committa **solo** se, in quest'ordine:

1. `pytest` è verde;
2. tutte le guardie sul diff sono passate;
3. il diff sta sotto i tetti: **150 righe, 3 file**.

Altrimenti `git checkout .` e si passa al task successivo. **Una giornata
storta = zero commit, mai un repo rotto.**

La CI in `.github/workflows/ci.yml` è il **giudice indipendente**: gira su
GitHub, su tre versioni di Python, e il loop non la può modificare. Se la CI
è rossa e i test locali erano verdi, ha ragione la CI.

## 7. Cosa non finisce mai qui dentro

Questo repository è **pubblico**.

- Nessun dato di EDIL KEY, di KITE o personale. Solo algoritmi pubblici.
- Nessuna chiave, token o password, nemmeno finti, nemmeno nei test: la
  guardia sui segreti riconosce la *forma* di una credenziale e boccia.
- Nessun dato personale reale nei vettori di prova. I codici fiscali e gli
  IBAN delle fonti sono **sintetici**: struttura corretta, persone e conti
  inesistenti.

## 8. Quando fermarsi

Fermarsi e scriverlo nel rapporto è sempre meglio che tirare a indovinare:

- la fonte non esiste, o non copre il caso richiesto;
- il task non sta sotto i tetti nemmeno spezzandolo bene;
- i test locali sono verdi ma la CI è rossa e non si capisce perché;
- la ROADMAP è finita.

**Nessuna di queste è una sconfitta.** La sconfitta è committare un algoritmo
sbagliato che nessuno noterà per sei mesi.
