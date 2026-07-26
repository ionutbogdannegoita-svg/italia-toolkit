# ROADMAP — la stella polare

L'elenco ordinato del lavoro. **Il loop non inventa task: li prende da qui.**
Quando questa lista finisce, il loop **si ferma** e scrive una domanda in
`RAPPORTO.md`. Non prosegue a fantasia.

Questo file è in `PERCORSI_VIETATI`: il loop lo legge e non lo può toccare.
Lo stato di avanzamento non sta qui — sta in `Progetto Agnes/stato/`, dove il
loop può scrivere. Così la lista del lavoro e il registro di chi l'ha fatto
restano due cose separate.

---

## Come si legge (e come la legge la macchina)

Ogni riga di tabella è **un task**. Le colonne sono fisse e in quest'ordine:

| colonna | significato |
|---|---|
| `ID` | identificatore stabile. Non si riusa e non si rinumera, mai. |
| `funzione` | il nome esatto della funzione pubblica da costruire |
| `modulo` | il file di `italia/` in cui vive |
| `fonte` | il file di `fonti/` da citare nella spec. **Senza, il task è nullo.** |
| `dipende` | ID che devono essere `FATTO` prima di cominciare, `—` se nessuno |
| `cosa deve fare` | una riga. Se non ci sta in una riga, il task è troppo grande |

**Regola per la coda concorrente:** due task che dichiarano lo **stesso
modulo** non partono mai insieme. Otto lavoratori in parallelo su uno stesso
file producono solo conflitti. La colonna `modulo` è il lucchetto.

**Regola di dimensione:** un task deve stare sotto il tetto delle guardie —
150 righe di diff e 3 file. Un task che non ci sta è un task scritto male:
va spezzato qui, non fatto passare allentando la guardia.

---

## Blocco 1 — Partita IVA
*Fonte pronta: [`fonti/partita_iva.md`](fonti/partita_iva.md)*

| ID | funzione | modulo | fonte | dipende | cosa deve fare |
|---|---|---|---|---|---|
| T003 | `cifra_controllo_partita_iva` | `italia/partita_iva.py` | `partita_iva.md` | — | dalle prime 10 cifre calcola l'undicesima (Luhn, §4) |
| T002 | `normalizza_partita_iva` | `italia/partita_iva.py` | `partita_iva.md` | — | toglie spazi, trattini, punti e il prefisso `IT`; restituisce le 11 cifre o solleva `ValueError` (§1) |
| T004 | `ufficio_partita_iva` | `italia/partita_iva.py` | `partita_iva.md` | T002 | dalle cifre 8-10 restituisce `'provinciale'` o `'speciale'`; solleva `ValueError` se il codice non è ammesso (§3, vettori §3.1) |
| T001 | `valida_partita_iva` | `italia/partita_iva.py` | `partita_iva.md` | T003, T002, T004 | `True`/`False`: **compone** le tre sopra e aggiunge il solo controllo che manca, progressivo ≠ `0000000` (§2) |
| T005 | `valida_codice_fiscale_ente` | `italia/partita_iva.py` | `partita_iva.md` | T003 | codice fiscale delle persone giuridiche: stesso checksum, **senza** il vincolo sull'ufficio |

> **Perché quest'ordine, e non `valida_partita_iva` per prima.** Ci abbiamo
> provato: il primo giro reale ha prodotto 271 righe di diff contro un tetto di
> 150, ed è stato bocciato. Chiedere in un colpo solo formato, progressivo,
> ufficio e checksum, con tutti i vettori della fonte, è un task mal
> decomposto. Le primitive prima, la composizione dopo: ogni pezzo sta sotto
> il tetto e `valida_partita_iva` diventa quattro righe che chiamano le altre.
> Gli ID non sono stati rinumerati — la regola in cima a questo file dice che
> non si fa — è cambiato l'ordine.

> **Secondo riordino, 26 luglio, per lo stesso motivo.** Con T003 e T002 già
> fatti, T001 è stato bocciato **di nuovo** dalla guardia del tetto: 214 righe,
> di cui 172 di soli test. Stavolta il codice era corretto, pytest verde e la
> mutazione superata: non era un problema di qualità, era ancora un problema di
> taglia. La causa: T001 doveva costruire da zero **tutta** la regola del §3,
> cinque intervalli con i loro confini, e sono i vettori dell'ufficio a fare
> volume.
>
> `T004` esisteva già, ma stava **dopo**: la primitiva dell'ufficio veniva
> chiesta dopo la funzione che ne ha bisogno. Spostata prima, con la firma
> chiarita perché sia componibile. Ora T001 ha davvero una regola sola da
> aggiungere, il §2, che è una riga.
>
> È la seconda volta che la guardia del tetto boccia T001 e la seconda volta
> che aveva ragione lei. Il tetto non è stato toccato nessuna delle due.

## Blocco 2 — Codice fiscale
*Fonte pronta: [`fonti/codice_fiscale.md`](fonti/codice_fiscale.md)*

| ID | funzione | modulo | fonte | dipende | cosa deve fare |
|---|---|---|---|---|---|
| T006 | `cin_codice_fiscale` | `italia/codice_fiscale.py` | `codice_fiscale.md` | — | dai primi 15 caratteri calcola il carattere di controllo (tabelle pari/dispari) |
| T007 | `valida_codice_fiscale` | `italia/codice_fiscale.py` | `codice_fiscale.md` | T006 | 16 caratteri: struttura, lettera del mese, giorno 01-31/41-71, Belfiore `[A-Z][0-9]{3}`, CIN. Accetta gli omocodici |
| T008 | `normalizza_codice_fiscale` | `italia/codice_fiscale.py` | `codice_fiscale.md` | T007 | maiuscolo, via spazi e punteggiatura; restituisce 16 caratteri o solleva `ValueError` |
| T009 | `sciogli_omocodia` | `italia/codice_fiscale.py` | `codice_fiscale.md` | T007 | riporta un codice omocodico alla forma con le cifre originali |
| T010 | `estrai_data_nascita` | `italia/codice_fiscale.py` | `codice_fiscale.md` | T007 | restituisce `(anno_2_cifre, mese, giorno)`. **Non** indovina il secolo |
| T011 | `estrai_sesso` | `italia/codice_fiscale.py` | `codice_fiscale.md` | T007 | `'M'` o `'F'` dal giorno (>40 ⇒ femmina) |
| T012 | `iniziali_cognome` | `italia/codice_fiscale.py` | `codice_fiscale.md` | — | le 3 lettere del cognome: consonanti, poi vocali, padding `X` |
| T013 | `iniziali_nome` | `italia/codice_fiscale.py` | `codice_fiscale.md` | T012 | le 3 lettere del nome, **con il salto della 2ª consonante** se sono ≥ 4 |
| T014 | `genera_codice_fiscale` | `italia/codice_fiscale.py` | `codice_fiscale.md` | T013, T006 | da cognome, nome, data, sesso e codice Belfiore costruisce il codice completo |

## Blocco 3 — IBAN
*Fonte pronta: [`fonti/iban.md`](fonti/iban.md)*

| ID | funzione | modulo | fonte | dipende | cosa deve fare |
|---|---|---|---|---|---|
| T015 | `normalizza_iban` | `italia/iban.py` | `iban.md` | — | maiuscolo e via gli spazi; rifiuta i caratteri non alfanumerici |
| T016 | `cifre_controllo_iban` | `italia/iban.py` | `iban.md` | T015 | dalle due cifre a `00`, calcola `98 − (n mod 97)` |
| T017 | `valida_iban` | `italia/iban.py` | `iban.md` | T016 | ISO 13616: formato, lunghezza del paese se nota, mod-97 = 1 |
| T018 | `cin_iban_italiano` | `italia/iban.py` | `iban.md` | — | il CIN dai 22 caratteri di ABI+CAB+conto (stesse tabelle del codice fiscale) |
| T019 | `valida_iban_italiano` | `italia/iban.py` | `iban.md` | T017, T018 | tutto `valida_iban`, **più** paese `IT`, 27 caratteri e CIN corretto |
| T020 | `estrai_abi_cab` | `italia/iban.py` | `iban.md` | T019 | restituisce `(cin, abi, cab, conto)` da un IBAN italiano |
| T021 | `componi_iban_italiano` | `italia/iban.py` | `iban.md` | T018, T016 | da ABI, CAB e conto costruisce l'IBAN completo, CIN e cifre di controllo inclusi |

---

## Oltre il blocco 3 — servono fonti nuove

Il loop **non parte** su questi finché il titolare non ha scritto la fonte.
Sono elencati per dare l'ordine, non per essere presi.

| dominio | fonte da scrivere | perché serve un umano |
|---|---|---|
| Tabella Belfiore | `fonti/belfiore.md` + dati | è un dato aggiornabile dell'Agenzia delle Entrate, non un algoritmo |
| CIG e CUP | `fonti/cig_cup.md` | struttura e checksum dai documenti ANAC/CIPE |
| Targhe automobilistiche | `fonti/targhe.md` | formati per periodo, nessun checksum: sono regole, vanno decise |
| Scadenze fiscali | `fonti/scadenze.md` | calendario che cambia ogni anno, e per legge |
| IVA e ritenute | `fonti/iva_ritenute.md` | aliquote e arrotondamenti: sbagliarli è un danno vero |
| Interessi di mora | `fonti/interessi_mora.md` | tassi BCE + D.Lgs. 231/2002, dipendono dal semestre |
| CAP | `fonti/cap.md` | tabella Poste Italiane |

---

## Quando la lista finisce

Il loop **si ferma**. Non riordina, non inventa, non "migliora" quello che ha
già fatto. Scrive in cima a `RAPPORTO.md`:

> **ROADMAP esaurita.** Ultimo task completato: `<ID>`. Servono nuove fonti
> per proseguire — vedi la tabella "Oltre il blocco 3".

Fermarsi con la lista vuota è il comportamento giusto. Un loop che si inventa
il lavoro da fare è esattamente ciò che questo progetto vuole evitare.
