# Partita IVA

**Norma:** **DPR 26 ottobre 1972, n. 633** (istituzione dell'IVA), art. 35, e
**DPR 29 settembre 1973, n. 605**, art. 4 — struttura del numero di partita IVA
attribuito dall'Anagrafe tributaria. Il carattere di controllo segue
l'algoritmo di **Luhn** (ISO/IEC 7812-1).

Il numero è di **11 cifre**, sempre e solo cifre:

```
  0 0 7 4 3 1 1   0 1 5   7
  └─────┬─────┘   └─┬─┘   │
   progressivo   ufficio  controllo
       7            3         1
```

---

## 1. Formato

- Esattamente **11 caratteri**, tutti **cifre** `0-9`.
- Gli zeri iniziali sono **significativi**: `00743110157` non è
  `743110157`. Chi la tratta come un intero perde i primi zeri e sbaglia.
- In ingresso si tollerano e si scartano: spazi, trattini, punti, e il
  prefisso `IT` (usato nelle transazioni intracomunitarie).
  `IT 00743110157` e `007-431-101-57` sono lo stesso numero.

## 2. Progressivo — cifre 1-7

Numero sequenziale assegnato dall'Anagrafe tributaria.

**Vincolo:** non può essere `0000000`. Quel valore non è mai stato attribuito,
quindi `00000000000` — che pure supera il checksum — **non è una partita IVA
valida**.

## 3. Codice ufficio — cifre 8-10

Identifica l'ufficio provinciale che ha attribuito il numero.

**Valori ammessi:**

| intervallo / valore | significato |
|---|---|
| `001` – `100` | uffici provinciali |
| `120` | Direzione Centrale Accertamento (soggetti non residenti) |
| `121` | soggetti identificati direttamente |
| `888` | enti non residenti / casi particolari |
| `999` | soggetti non residenti |

Qualunque altro valore (`000`, `101`-`119`, `122`-`887`, `889`-`998`) rende il
numero invalido, **anche se il checksum torna**.

> Questo controllo è deliberatamente **incluso** in `valida_partita_iva`.
> Motivo pratico: è quello che fa anche `python-stdnum` (`stdnum.it.iva`), la
> libreria di riferimento dell'oracolo #3. Se lo omettessimo, il confronto
> differenziale su input casuali divergerebbe in continuazione e diventerebbe
> rumore invece che segnale.

## 4. Cifra di controllo — cifra 11

Algoritmo di **Luhn**, applicato alle prime 10 cifre.

1. Si numerano le cifre **da 1 a 10, da sinistra**.
2. Le cifre in posizione **dispari** (1ª, 3ª, 5ª, 7ª, 9ª) si sommano così
   come sono.
3. Le cifre in posizione **pari** (2ª, 4ª, 6ª, 8ª, 10ª) si **raddoppiano**;
   se il doppio supera 9, gli si sottrae 9 (equivale a sommare le due cifre
   del risultato: `14` → `1+4` = `5` = `14-9`).
4. Si sommano tutti i valori ottenuti → totale `T`.
5. La cifra di controllo è **`(10 − (T mod 10)) mod 10`**.

Il `mod 10` finale non è un dettaglio: senza di esso, quando `T` è già multiplo
di 10 il risultato verrebbe `10` invece di `0`.

### Esempio svolto — `00743110157`

Prime 10 cifre: `0 0 7 4 3 1 1 0 1 5`

| pos | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| cifra | 0 | 0 | 7 | 4 | 3 | 1 | 1 | 0 | 1 | 5 |
| trattamento | — | ×2 | — | ×2 | — | ×2 | — | ×2 | — | ×2 |
| grezzo | 0 | 0 | 7 | 8 | 3 | 2 | 1 | 0 | 1 | 10 |
| valore | 0 | 0 | 7 | 8 | 3 | 2 | 1 | 0 | 1 | **1** |

`10 > 9` → `10 − 9 = 1`.

Totale `T` = 0+0+7+8+3+2+1+0+1+1 = **23**.
Cifra di controllo = `(10 − (23 mod 10)) mod 10` = `(10 − 3) mod 10` = **7**. ✔

---

## 5. Vettori di prova

> Tutti incrociati con `python-stdnum 2.2` (`stdnum.it.iva`) prima di essere
> scritti qui.

### Noti-BUONI — devono risultare validi

| numero | ufficio | note |
|---|---|---|
| `00743110157` | `015` | esempio svolto al §4 |
| `07643520567` | `056` | |
| `13378520152` | `015` | |
| `12345670017` | `001` | confine inferiore dell'intervallo uffici |
| `99999991203` | `120` | ufficio speciale |
| `50000008883` | `888` | ufficio speciale |
| `00000019992` | `999` | ufficio speciale, progressivo minimo (`0000001`) |

Formati equivalenti che devono essere accettati e ricondotti a
`00743110157`: `IT00743110157`, `IT 00743110157`, `007-431-101-57`,
`" 00743110157 "`.

### Noti-CATTIVI — devono risultare invalidi

| numero | perché |
|---|---|
| `00743110158` | cifra di controllo errata (quella giusta è `7`) |
| `0074311015` | 10 cifre |
| `007431101570` | 12 cifre |
| `0074311015X` | carattere non numerico |
| *(stringa vuota)* | lunghezza 0 |
| `00000000000` | progressivo `0000000`, mai assegnato — **il checksum torna** |
| `00000010007` | ufficio `000` inesistente — **il checksum torna** |
| `01234567897` | ufficio `789` inesistente — **il checksum torna** |
| `12345678903` | ufficio `890` inesistente — **il checksum torna** |

> Gli ultimi quattro sono i vettori che contano: un'implementazione che si
> ferma al checksum li accetta tutti. Sono il motivo per cui i controlli sul
> progressivo e sull'ufficio non sono facoltativi.

---

## 6. Cosa questa fonte NON copre

- **Codice fiscale delle persone giuridiche.** È un numero di 11 cifre con lo
  stesso identico checksum, ma **non** ha il vincolo dell'ufficio: può avere
  qualunque terzina in posizione 8-10. Sono due funzioni diverse, e vanno
  tenute separate proprio perché sembrano uguali.
- **Validazione VIES** (esistenza reale del soggetto presso l'anagrafe
  europea). Richiede una chiamata di rete: fuori dallo scopo di questa
  libreria, che contiene **solo funzioni pure**.
- **Partite IVA di gruppo** e regimi speciali.
