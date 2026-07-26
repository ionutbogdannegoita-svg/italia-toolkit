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

### 5.1 Vettori per la sola cifra di controllo (10 cifre in ingresso)

Le tabelle sopra sono per il numero **intero**, da 11 cifre. Una funzione che
calcola *solo* la cifra di controllo prende in ingresso le **prime 10**, e ha
bisogno dei suoi vettori: eccoli già derivati e verificati con
`stdnum.luhn.calc_check_digit`. **Copiali, non ricavarli** — ricavarli a mano
è il modo più facile di sbagliare.

**Ingressi validi** → la cifra che deve uscire:

| 10 cifre | cifra | da quale P.IVA |
|---|---|---|
| `0074311015` | **7** | `00743110157` — esempio svolto al §4 |
| `0764352056` | **7** | `07643520567` |
| `1337852015` | **2** | `13378520152` |
| `1234567001` | **7** | `12345670017` |
| `9999999120` | **3** | `99999991203` |
| `5000000888` | **3** | `50000008883` |
| `0000001999` | **2** | `00000019992` |
| `0000000000` | **0** | *nessuna* — vedi la nota qui sotto |

> **`0000000000` → `0` è un ingresso VALIDO per questa funzione.** Il numero
> completo `00000000000` non è una partita IVA valida (progressivo `0000000`,
> §2), ma quello è un problema di `valida_partita_iva`, non del calcolo del
> checksum. Una funzione che calcola una cifra non ha titolo per rifiutare un
> input di 10 cifre: le calcola e basta. È il vettore che separa le due
> responsabilità, e va tenuto.

**Ingressi da rifiutare** (`ValueError`) — e nessun altro:

| ingresso | perché |
|---|---|
| `""` | 0 cifre |
| `"007431101"` | 9 cifre |
| `"00743110157"` | 11 cifre |
| `"007431101A"` | carattere non numerico |
| `"007431 015"` | contiene uno spazio |
| `"0074311015 "` | spazio in coda: **10 cifre più uno spazio, non 10 caratteri** |

> Attenzione a non finire fuori strada: **`0074311015` sta fra i validi.**
> Metterlo fra quelli da rifiutare perché "assomiglia" a una P.IVA incompleta
> è un errore già capitato. Dieci cifre sono dieci cifre.

### 5.2 Vettori per la sola normalizzazione

| ingresso | risultato |
|---|---|
| `"00743110157"` | `"00743110157"` (invariato) |
| `"IT00743110157"` | `"00743110157"` |
| `"IT 00743110157"` | `"00743110157"` |
| `"007-431-101-57"` | `"00743110157"` |
| `" 00743110157 "` | `"00743110157"` |
| `"007.431.101.57"` | `"00743110157"` ⚠ vedi nota |

Da rifiutare con `ValueError`: `""`, `"0074311015"` (10 cifre),
`"007431101570"` (12 cifre), `"0074311015X"` (lettera in mezzo alle cifre).

> ⚠ **Sui punti siamo più tolleranti del riferimento.**
> `stdnum.it.iva.compact` toglie spazi, trattini e due punti, **ma non i
> punti**: su `"007.431.101.57"` restituisce la stringa invariata. Noi i punti
> li togliamo, perché in Italia il numero si scrive anche così.
> Conseguenza per l'oracolo #3: il confronto differenziale con `compact` vale
> **solo sugli ingressi che non contengono punti**. Sui punti decidono i
> vettori di questa tabella, non la libreria.

> La normalizzazione **non guarda il checksum**: `"00743110158"` ha la cifra
> di controllo sbagliata e va restituito invariato lo stesso. Rifiutarlo è
> compito di `valida_partita_iva`.

---

## 6. Confronto differenziale: quale riferimento per quale funzione

L'oracolo #3 confronta le nostre funzioni con `python-stdnum` su input casuali.
Funziona a una condizione sola, e non è negoziabile:

> **Il riferimento deve implementare la STESSA regola, non una più grande.**

`stdnum.it.iva.validate` applica **tutte e quattro** le regole di questo
documento: formato, progressivo, ufficio e checksum. Confrontarlo con una
nostra funzione che ne implementa una sola produce fallimenti che non sono
difetti — sono due domande diverse a cui si risponde in modo diverso.

| nostra funzione | riferimento corretto | note |
|---|---|---|
| `cifra_controllo_partita_iva` | `stdnum.luhn.calc_check_digit(dieci_cifre)` | stessa identica regola: solo §4. **Restituisce una stringa** (`'7'`), la nostra un intero: confrontare `str(nostro) == riferimento` |
| `normalizza_partita_iva` | `stdnum.it.iva.compact(x)` | solo §1. `compact` pulisce e basta, **non valida**: confronta solo sugli ingressi che la nostra funzione accetta. E **mai su ingressi con un punto**: `compact` i punti non li toglie, noi sì (§5.2) |
| `valida_partita_iva` | `stdnum.it.iva.validate(x)` | l'unica nostra funzione che implementa **tutta** la regola. Qui la corrispondenza dev'essere piena |
| `ufficio_partita_iva` | *(nessuno)* | `stdnum` non espone il codice ufficio: solo vettori e proprietà |
| `valida_codice_fiscale_ente` | *(nessuno)* | `stdnum.it.iva` impone il vincolo sull'ufficio, che qui **non** vale |

### L'errore da non fare, con nome e cognome

```python
# SBAGLIATO — proprietà falsa, Hypothesis la smonta in un secondo
@given(st.text(min_size=10, max_size=10, alphabet="0123456789"))
def test_checksum_corretto_rende_valido(dieci):
    completo = dieci + str(cifra_controllo_partita_iva(dieci))
    assert iva.validate(completo) == completo      # <- '0000000000' → InvalidFormat
```

`0000000000` più la sua cifra di controllo dà `00000000000`: il checksum torna,
ma il progressivo è `0000000` e `iva.validate` giustamente rifiuta. La
proprietà afferma qualcosa che `cifra_controllo_partita_iva` **non promette**.

```python
# GIUSTO — la proprietà dice solo quello che questa funzione garantisce
@given(st.text(min_size=10, max_size=10, alphabet="0123456789"))
def test_coincide_col_luhn_di_riferimento(dieci):
    assert str(cifra_controllo_partita_iva(dieci)) == luhn.calc_check_digit(dieci)
```

### E non riscrivere l'algoritmo dentro il test

Un test che ricalcola il checksum con un secondo pezzo di codice scritto lì
per lì, e poi confronta le due implementazioni, non verifica niente: se chi ha
scritto il test ha letto male questo documento, **le due copie sbagliano
insieme** e il verde conferma l'errore.

L'oracolo sono i vettori del §5, che sono stati verificati a mano, e la
libreria di riferimento. Non una seconda implementazione fatta in casa.

---

## 7. Cosa questa fonte NON copre

- **Codice fiscale delle persone giuridiche.** È un numero di 11 cifre con lo
  stesso identico checksum, ma **non** ha il vincolo dell'ufficio: può avere
  qualunque terzina in posizione 8-10. Sono due funzioni diverse, e vanno
  tenute separate proprio perché sembrano uguali.
- **Validazione VIES** (esistenza reale del soggetto presso l'anagrafe
  europea). Richiede una chiamata di rete: fuori dallo scopo di questa
  libreria, che contiene **solo funzioni pure**.
- **Partite IVA di gruppo** e regimi speciali.
