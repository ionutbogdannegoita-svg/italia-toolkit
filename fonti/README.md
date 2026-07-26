# `fonti/` — l'oracolo

Qui dentro stanno gli algoritmi ufficiali, **scritti a mano da un umano** prima
che esistesse una riga di codice. Non sono documentazione: sono l'autorità.

## A cosa serve

Questa libreria viene scritta da un modello che lavora senza sorveglianza.
Un modello, su un algoritmo che non ricorda bene, non dice "non lo so":
inventa qualcosa di plausibile. Su una regola di dominio è una catastrofe
silenziosa, perché il codice gira e restituisce risultati sbagliati con la
faccia di quelli giusti.

Rimedio: **su questo dominio decide la matematica, non un'opinione.** Codice
fiscale, partita IVA e IBAN hanno checksum ufficiali. Esiste una risposta
giusta, ed è scritta qui.

## Le tre regole

1. **Una spec che non cita la fonte viene rifiutata.** Ogni funzione nuova
   nasce da un file di questa cartella, citato per nome e per paragrafo.
   Niente fonte, niente task.

2. **`fonti/` è di sola lettura per il loop.** È in `PERCORSI_VIETATI`
   (`officina/guardie.py`): qualunque diff che la tocchi viene bocciato prima
   del commit. Il modello non può cambiare l'esame mentre lo sostiene.

3. **I vettori qui dentro sono verificati, non copiati.** Ogni valore in
   queste tabelle è stato calcolato e incrociato con `python-stdnum` prima di
   essere scritto. Attenzione: in rete girano moltissimi esempi *falsi* —
   `RSSMRA85M01H501Z`, il "Mario Rossi" più diffuso del web, ha il carattere
   di controllo sbagliato (quello vero è `Q`). Per questo sta fra i
   noti-cattivi invece che fra i noti-buoni.

## Come si usano nei test

I tre oracoli del progetto, in ordine di durezza:

| # | Oracolo | Dove vive |
|---|---|---|
| 1 | Algoritmo ufficiale di questa cartella | `fonti/*.md`, citato nella spec |
| 2 | Vettori noti-buoni / noti-cattivi | tabelle di questi file, copiate nei test |
| 3 | Property-based (Hypothesis) + confronto differenziale con `python-stdnum` su input casuali | **solo nei test** |

Il terzo merita una precisazione: `python-stdnum` è una dipendenza **di test**,
mai di runtime. Non compare in `[project.dependencies]` e nessun modulo di
`italia/` la importa. Serve come secondo parere su 10.000 input casuali, non
come implementazione da avvolgere.

Dove la nostra regola è deliberatamente **più severa** del riferimento, il file
della fonte lo dice a chiare lettere e il confronto differenziale va ristretto
alla parte in comune. Oggi succede in un punto solo: il CIN dell'IBAN italiano,
che `stdnum` non controlla (vedi `iban.md`, §5).

## Indice

| File | Dominio | Norma di riferimento |
|---|---|---|
| [`codice_fiscale.md`](codice_fiscale.md) | codice fiscale persone fisiche | DM 23/12/1976 |
| [`partita_iva.md`](partita_iva.md) | partita IVA | DPR 605/1973 |
| [`iban.md`](iban.md) | IBAN, con CIN italiano | ISO 13616 · CBI |
