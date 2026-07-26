# IBAN — internazionale (ISO 13616) e italiano (CIN)

**Norme:**
- **ISO 13616-1:2020** — struttura dell'IBAN e cifre di controllo.
- **ISO 7064:2003, MOD 97-10** — l'algoritmo delle cifre di controllo.
- **CBI / ABI** — struttura del BBAN italiano e **CIN**, il carattere di
  controllo nazionale, eredità delle vecchie coordinate bancarie.

Attenzione: sono **due controlli distinti e indipendenti**. Un IBAN italiano
può superare il mod-97 internazionale e avere il CIN nazionale sbagliato.
Vedi §5, è il punto che quasi tutte le implementazioni sbagliano.

---

## 1. Struttura generale (ISO 13616)

```
  I T   6 0   X 05428 11101 000000123456
  └┬┘   └┬┘   └──────────┬─────────────┘
 paese  check           BBAN
   2      2         (fino a 30)
```

- **Paese:** 2 lettere maiuscole, ISO 3166-1 alpha-2.
- **Cifre di controllo:** 2 cifre.
- **BBAN:** da 11 a 30 caratteri alfanumerici, **struttura e lunghezza fisse
  per ciascun paese**.
- Lunghezza totale: **massimo 34 caratteri**.
- Nella forma elettronica non ci sono spazi. In quella cartacea si scrive a
  gruppi di 4; in ingresso gli spazi si tollerano e si eliminano.
- Solo maiuscole e cifre: `A-Z0-9`. Un `-`, un `_` o un accento invalidano.

### Lunghezze dei paesi più frequenti

| paese | lunghezza | | paese | lunghezza |
|---|---|---|---|---|
| `IT` Italia | **27** | | `ES` Spagna | 24 |
| `DE` Germania | 22 | | `NL` Paesi Bassi | 18 |
| `FR` Francia | 27 | | `BE` Belgio | 16 |
| `GB` Regno Unito | 22 | | `CH` Svizzera | 21 |
| `SM` San Marino | 27 | | `AT` Austria | 20 |

Il registro completo dei 80+ paesi è un **dato tabellare aggiornabile**, non
un algoritmo: sta in una fonte separata, da scrivere quando servirà.
`valida_iban` controlla la lunghezza solo per i paesi che conosce; su un
paese sconosciuto verifica formato e mod-97 e lo dichiara comunque.

## 2. Cifre di controllo internazionali — MOD 97-10

1. Si spostano i **primi 4 caratteri in fondo**:
   `IT60X0542…456` → `X0542…456IT60`.
2. Ogni **lettera** diventa un numero: `A`=10, `B`=11, … `Z`=35
   (cioè `ord(lettera) − 55`). Le cifre restano.
3. Si legge il risultato come un unico intero e se ne prende il **resto della
   divisione per 97**.
4. **L'IBAN è valido se e solo se il resto è `1`.**

L'intero può superare i 30 caratteri: in Python `int` è illimitato e si può
calcolare direttamente. In linguaggi con interi a dimensione fissa serve la
riduzione a blocchi, qui non necessaria.

### Esempio svolto — `IT60X0542811101000000123456`

```
riordinato : X0542811101000000123456IT60
numerico   : 330542811101000000123456182960     (X→33, I→18, T→29)
mod 97     : 1        ✔ valido
```

### Calcolare le cifre di controllo da zero

Si mettono `00` al posto delle cifre di controllo, si applicano i passi 1-2,
e le cifre sono **`98 − (n mod 97)`**, scritte su due posizioni con lo zero
iniziale se serve.

Per il BBAN `X0542811101000000123456`: `98 − 38` = **`60`**. ✔

## 3. Struttura del BBAN italiano

I 23 caratteri dopo `IT` e le due cifre di controllo:

| campo | lunghezza | tipo | esempio |
|---|---|---|---|
| **CIN** | 1 | lettera `A-Z` | `X` |
| **ABI** | 5 | cifre | `05428` |
| **CAB** | 5 | cifre | `11101` |
| **numero di conto** | 12 | alfanumerico `A-Z0-9` | `000000123456` |

Il numero di conto è **alfanumerico**, non solo numerico: alcune banche usano
lettere. Un'implementazione che pretende 12 cifre rifiuta IBAN validi.

`1 + 5 + 5 + 12 = 23`, più `IT` e le 2 cifre di controllo fa **27**.

## 4. CIN italiano — il controllo nazionale

Si calcola sui **22 caratteri di ABI + CAB + conto**, cioè sul BBAN **senza**
il CIN stesso.

L'algoritmo è **lo stesso del codice fiscale** (vedi
[`codice_fiscale.md` §7](codice_fiscale.md)), applicato a 22 caratteri
invece che a 15:

1. Posizioni contate **da 1**: le dispari usano la colonna *dispari*, le pari
   la colonna *pari*.
2. Somma dei 22 valori.
3. Resto della divisione per **26**.
4. `0`→`A`, `1`→`B`, …, `25`→`Z`.

La tabella di conversione è la stessa, e va riportata da
`codice_fiscale.md` §7 senza modifiche.

### Esempio svolto — BBAN `0542811101000000123456`

| pos | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| car | 0 | 5 | 4 | 2 | 8 | 1 | 1 | 1 | 0 | 1 | 0 |
| val | 1 | 5 | 9 | 2 | 19 | 1 | 0 | 1 | 1 | 1 | 1 |

| pos | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| car | 0 | 0 | 0 | 0 | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
| val | 0 | 1 | 0 | 1 | 0 | 0 | 2 | 7 | 4 | 13 | 6 |

Somma = **75**. 75 mod 26 = **23**. 23 → **`X`**. ✔
Coincide col CIN dichiarato nell'IBAN. Valido.

## 5. I due controlli sono indipendenti — il vettore che conta

> **`IT40S0542811101000000123456`**
>
> - mod-97 internazionale: **`1`** → ISO 13616 dice **valido**
> - CIN italiano calcolato sul BBAN: **`X`**, ma è dichiarato **`S`** → **non
>   valido** come IBAN italiano

Non è un caso costruito ad arte: è un esempio che circola in rete come IBAN
italiano di prova, e passa indenne da qualunque validatore che si fermi al
mod-97 — **compreso `python-stdnum`**, che per l'Italia non verifica il CIN.

**Conseguenza per il progetto.** Servono due funzioni, non una:

| funzione | cosa controlla | oracolo #3 |
|---|---|---|
| `valida_iban(iban)` | formato, lunghezza per paese, mod-97 | confronto differenziale con `stdnum.iban` — **corrispondenza piena attesa** |
| `valida_iban_italiano(iban)` | tutto quanto sopra, **più** paese `IT`, lunghezza 27, struttura CIN/ABI/CAB/conto, e **CIN corretto** | **niente confronto differenziale**: siamo più severi del riferimento. Solo vettori ufficiali e property-based |

Mettere entrambe le cose in una sola funzione è l'errore da non fare: o è
troppo lasca sugli IBAN italiani, o boccia gli esteri.

---

## 6. Vettori di prova

> Tutti calcolati e incrociati con `python-stdnum 2.2` (`stdnum.iban`) prima
> di essere scritti qui. Sono IBAN **sintetici**: struttura reale, conti
> inesistenti.

### Italiani noti-BUONI — mod-97 valido **e** CIN corretto

| IBAN | CIN | ABI | CAB | conto |
|---|---|---|---|---|
| `IT60X0542811101000000123456` | `X` | `05428` | `11101` | `000000123456` |
| `IT14M0306909400100000000001` | `M` | `03069` | `09400` | `100000000001` |
| `IT71L0200801600000000000001` | `L` | `02008` | `01600` | `000000000001` |
| `IT79G0100503200000000000000` | `G` | `01005` | `03200` | `000000000000` |

Formati equivalenti da accettare, tutti pari al primo della tabella:
`IT60 X054 2811 1010 0000 0123 456` (a gruppi di 4) e
`it60x0542811101000000123456` (minuscolo).

### Esteri noti-BUONI — validi per `valida_iban`, **rifiutati** da `valida_iban_italiano`

| IBAN | paese | lunghezza |
|---|---|---|
| `DE89370400440532013000` | Germania | 22 |
| `GB82WEST12345698765432` | Regno Unito | 22 |
| `FR1420041010050500013M02606` | Francia | 27 |
| `ES9121000418450200051332` | Spagna | 24 |

`FR14…` merita attenzione: è lungo **27** come un IBAN italiano. Serve a
smascherare chi controlla la lunghezza e si dimentica il codice paese.

### Noti-CATTIVI

| IBAN | mod-97 | perché |
|---|---|---|
| `IT61X0542811101000000123456` | 2 | cifre di controllo errate (quelle giuste: `60`) |
| **`IT40S0542811101000000123456`** | **1** | **CIN italiano errato: dev'essere `X`.** Passa il mod-97 |
| `IT60X054281110100000012345` | 68 | 26 caratteri |
| `IT60X05428111010000001234567` | 37 | 28 caratteri |
| `XX60X0542811101000000123456` | 51 | codice paese inesistente |
| `IT60X05428111010000001234!6` | — | carattere non alfanumerico |
| *(stringa vuota)* | — | lunghezza 0 |

---

## 7. Cosa questa fonte NON copre

- **Registro completo delle lunghezze e strutture BBAN** dei paesi IBAN. È un
  dato tabellare, non un algoritmo: fonte separata.
- **BIC/SWIFT** e la corrispondenza ABI → banca. Richiede una tabella
  aggiornabile.
- **Esistenza reale del conto.** Nessun algoritmo la può stabilire: un IBAN
  formalmente perfetto può non appartenere a nessuno.
- **Generazione** di IBAN validi. È utile solo per i test, e in quel contesto
  la fa Hypothesis a partire dall'algoritmo, non una funzione di libreria.
