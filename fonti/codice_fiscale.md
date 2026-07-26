# Codice fiscale delle persone fisiche

**Norma:** Decreto del Ministero delle Finanze **23 dicembre 1976**,
*"Sistemi di codificazione dei soggetti da iscrivere all'anagrafe tributaria"*
(G.U. n. 345 del 29/12/1976), in attuazione del **DPR 605/1973**, art. 6.

Il codice è di **16 caratteri alfanumerici maiuscoli**, così composti:

```
  R S S M R A   8 5   M   0 1   H 5 0 1   Q
  └──┬──┘└─┬─┘  └┬┘   │   └┬┘   └──┬──┘   │
  cognome nome  anno mese giorno comune  CIN
   3        3     2    1     2      4      1
```

---

## 1. Cognome — 3 caratteri (posizioni 1-3)

Si lavora sul cognome ridotto alle sole lettere A-Z maiuscole: via spazi,
apostrofi, trattini; le vocali accentate diventano la vocale semplice
(`È`→`E`, `Ò`→`O`); i cognomi composti si concatenano
(`De Luca` → `DELUCA`).

1. Si prendono le **consonanti**, nell'ordine in cui compaiono.
2. Si accodano le **vocali**, nell'ordine in cui compaiono.
3. Si prendono i primi 3 caratteri della stringa così ottenuta.
4. Se il cognome ha meno di 3 lettere, si completa a destra con `X`.

| cognome | consonanti + vocali | risultato |
|---|---|---|
| `ROSSI` | `RSS` + `OI` | `RSS` |
| `DE LUCA` → `DELUCA` | `DLC` + `EUA` | `DLC` |
| `ESPOSITO` | `SPST` + `EOIO` | `SPS` |
| `AIELLO` | `LL` + `AIEO` | `LLA` |
| `FO` | `F` + `O` | `FOX` (padding) |

## 2. Nome — 3 caratteri (posizioni 4-6)

Stessa normalizzazione del cognome, **ma con una regola in più**:

1. Si prendono le consonanti nell'ordine.
2. **Se le consonanti sono 4 o più: si prendono la 1ª, la 3ª e la 4ª**
   (si salta la seconda).
3. Se sono 3 o meno: consonanti, poi vocali, primi 3 caratteri.
4. Padding con `X` se si resta sotto i 3 caratteri.

| nome | consonanti | regola | risultato |
|---|---|---|---|
| `MARIO` | `MR` (2) | cons.+vocali `MRAIO` | `MRA` |
| `GIUSEPPE` | `GSPP` (4) | 1ª,3ª,4ª → `G`,`P`,`P` | `GPP` |
| `MARIA LUISA` → `MARIALUISA` | `MRLS` (4) | 1ª,3ª,4ª → `M`,`L`,`S` | `MLS` |
| `ANNA` | `NN` (2) | cons.+vocali `NNAA` | `NNA` |
| `AL` | `L` (1) | `L`+`A` | `LAX` (padding) |

> Il salto della 2ª consonante vale **solo per il nome**, mai per il cognome.
> È l'errore più frequente in chi reimplementa questo algoritmo.

## 3. Anno di nascita — 2 caratteri (posizioni 7-8)

Le ultime due cifre dell'anno. `1985` → `85`, `2000` → `00`.

Il secolo **non è codificato**: `85` è tanto 1885 quanto 1985 quanto 2085.
Una funzione di validazione non può quindi dedurre l'anno esatto, e non deve
provarci.

## 4. Mese di nascita — 1 carattere (posizione 9)

| mese | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **lettera** | `A` | `B` | `C` | `D` | `E` | `H` | `L` | `M` | `P` | `R` | `S` | `T` |

Sequenza da ricordare: **`A B C D E H L M P R S T`**. Le lettere `F G I J K N O Q`
non compaiono mai in questa posizione: sono state saltate perché troppo simili
ad altre nella lettura ottica dei moduli.

## 5. Giorno di nascita e sesso — 2 caratteri (posizioni 10-11)

- **Maschi:** il giorno, su due cifre. Da `01` a `31`.
- **Femmine:** il giorno **+ 40**. Da `41` a `71`.

È l'unico punto in cui il sesso entra nel codice. Valori ammessi: `01`-`31` e
`41`-`71`. Tutto il resto (`00`, `32`-`40`, `72`-`99`) è invalido.

> Non si controlla la coerenza col mese: `30` febbraio è formalmente ammesso
> dal codice fiscale. Chi vuole quel controllo lo fa a parte, con il calendario.

## 6. Comune o Stato estero — 4 caratteri (posizioni 12-15)

**Codice Belfiore**: una lettera seguita da tre cifre.

- Comuni italiani: la lettera va da `A` a `M` (`H501` Roma, `F205` Milano,
  `L219` Torino, `F839` Napoli).
- Stati esteri: la lettera è sempre **`Z`** (`Z404` Regno Unito,
  `Z129` Argentina).

**Per la validazione formale si controlla solo il formato** `[A-Z][0-9]{3}`.
Verificare che il codice esista davvero richiede la tabella Belfiore
dell'Agenzia delle Entrate, che è un dato aggiornabile e non un algoritmo:
è un task separato, con una fonte separata.

## 7. Carattere di controllo (CIN) — 1 carattere (posizione 16)

Si calcola sui **primi 15 caratteri**.

1. Ogni carattere vale un numero, e **il valore dipende dalla posizione**
   (contata **da 1**): posizioni dispari (1ª, 3ª, 5ª, …, 15ª) usano la colonna
   *dispari*, posizioni pari (2ª, 4ª, …, 14ª) la colonna *pari*.
2. Si sommano i 15 valori.
3. Si prende il **resto della divisione per 26**.
4. Il resto è la lettera: `0`→`A`, `1`→`B`, …, `25`→`Z`.

### Tabella di conversione

| carattere | dispari | pari | | carattere | dispari | pari |
|---|---|---|---|---|---|---|
| `0` o `A` | 1 | 0 | | `J` o `9` | 21 | 9 |
| `1` o `B` | 0 | 1 | | `K` | 2 | 10 |
| `2` o `C` | 5 | 2 | | `L` | 4 | 11 |
| `3` o `D` | 7 | 3 | | `M` | 18 | 12 |
| `4` o `E` | 9 | 4 | | `N` | 20 | 13 |
| `5` o `F` | 13 | 5 | | `O` | 11 | 14 |
| `6` o `G` | 15 | 6 | | `P` | 3 | 15 |
| `7` o `H` | 17 | 7 | | `Q` | 6 | 16 |
| `8` o `I` | 19 | 8 | | `R` | 8 | 17 |
| | | | | `S` | 12 | 18 |
| | | | | `T` | 14 | 19 |
| | | | | `U` | 16 | 20 |
| | | | | `V` | 10 | 21 |
| | | | | `W` | 22 | 22 |
| | | | | `X` | 25 | 23 |
| | | | | `Y` | 24 | 24 |
| | | | | `Z` | 23 | 25 |

Nella colonna **pari** il valore è semplicemente l'indice alfabetico
(`A`=0 … `Z`=25) e la cifra vale sé stessa. Solo la colonna **dispari** è
una tabella arbitraria da riportare per intero.

### Esempio svolto — `RSSMRA80A01H501U`

| pos | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| car | R | S | S | M | R | A | 8 | 0 | A | 0 | 1 | H | 5 | 0 | 1 |
| tab | D | P | D | P | D | P | D | P | D | P | D | P | D | P | D |
| val | 8 | 18 | 12 | 12 | 8 | 0 | 19 | 0 | 1 | 0 | 0 | 7 | 13 | 0 | 0 |

Somma = **98**. 98 mod 26 = **20**. 20 → **`U`**. ✔

Si noti la posizione 12: la `H` vale **7**, non 17. È in posizione **pari**,
quindi si legge la colonna *pari* (indice alfabetico). Scambiare le due colonne
è l'errore più insidioso di questo algoritmo, perché su molti codici il
risultato resta plausibile.

## 8. Omocodia

Quando due persone diverse otterrebbero lo stesso codice, l'Agenzia delle
Entrate ne differenzia uno **sostituendo le cifre con lettere**, partendo dalla
cifra **più a destra** e risalendo.

| cifra | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| **lettera** | `L` | `M` | `N` | `P` | `Q` | `R` | `S` | `T` | `U` | `V` |

Le posizioni numeriche sono 7, nell'ordine di sostituzione (da destra):
**15, 14, 13, 11, 10, 8, 7**.

Dopo ogni sostituzione **il CIN si ricalcola**. Un validatore corretto deve
accettare i codici omocodici: hanno lettere dove ci si aspettano cifre, ma il
CIN torna.

Esempio: da `RSSMRA85M01H501Q`, sostituendo l'ultima cifra (`1` in posizione 15)
si ottiene `RSSMRA85M01H50M` + CIN ricalcolato = **`RSSMRA85M01H50MI`**.

---

## 9. Vettori di prova

> Tutti calcolati e incrociati con `python-stdnum 2.2`
> (`stdnum.it.codicefiscale`) prima di essere scritti qui.

### Noti-BUONI — devono risultare validi

| codice | persona | note |
|---|---|---|
| `MRTMTT25D09F205Z` | MARTI MATTEO, M, 09/04/1925, Milano | caso base |
| `RSSMRA80A01H501U` | ROSSI MARIO, M, 01/01/1980, Roma | esempio svolto al §7 |
| `RSSMRA85M01H501Q` | ROSSI MARIO, M, 01/08/1985, Roma | |
| `MLLSNT82P65Z404U` | MOLLO SANTA, F, 25/09/1982, Regno Unito | femmina (65 = 25+40) + estero (`Z`) |
| `DLCNNA90B52L219V` | DE LUCA ANNA, F, 12/02/1990, Torino | cognome composto |
| `SPSGPP62S24F839V` | ESPOSITO GIUSEPPE, M, 24/11/1962, Napoli | nome con 4 consonanti (`GPP`) |
| `FOXDAA00T71H501U` | FO ADA, F, 31/12/2000, Roma | cognome di 2 lettere (padding `X`) |
| `RSSMRA85M01H50MI` | omocodia di `RSSMRA85M01H501Q` | 1 sostituzione |

### Noti-CATTIVI — devono risultare invalidi

**Errori di checksum e lunghezza**

| codice | perché |
|---|---|
| `RSSMRA85M01H501Z` | CIN errato: quello vero è `Q`. **Esempio falso diffusissimo in rete** |
| `RSSMRA85M01H501A` | CIN errato |
| `RSSMRA85M01H501` | 15 caratteri |
| `RSSMRA85M01H501QQ` | 17 caratteri |
| *(stringa vuota)* | lunghezza 0 |

**Errori di struttura — attenzione: qui il CIN è ricalcolato ed è corretto.**
Servono a verificare che la funzione controlli la *forma* e non si limiti al
checksum. Un'implementazione che fa solo il CIN li accetta tutti, ed è rotta.

| codice | perché |
|---|---|
| `RSSMRA85X01H501X` | `X` non è una lettera di mese valida |
| `RSSMRA85M00H501R` | giorno `00` |
| `RSSMRA85M32H501Y` | giorno `32` (maschi: max 31) |
| `RSSMRA85M72H501C` | giorno `72` (femmine: max 71) |
| `RSS1RA85M01H501F` | cifra dentro le prime 6 lettere |
| `RSSMRA8AM01H501L` | lettera dentro l'anno |
| `RSSMRA85M01HA01E` | lettera dentro le 3 cifre del Belfiore |

**Controprova** (per evitare che il validatore diventi troppo severo):
`RSSMRA85M41H501U` è **valido** — giorno 41 significa femmina nata il giorno 1.

---

## 10. Confronto differenziale: quale riferimento per quale funzione

L'oracolo #3 regge a una condizione sola: **il riferimento deve implementare la
stessa regola, non una più grande.** `stdnum.it.codicefiscale.validate`
controlla formato, mese, giorno, Belfiore *e* CIN tutti insieme: confrontarlo
con una nostra funzione che ne fa uno solo produce fallimenti che non sono
difetti.

| nostra funzione | riferimento corretto | note |
|---|---|---|
| `cin_codice_fiscale` | `stdnum.it.codicefiscale.calc_check_digit(primi15)` | stessa regola: solo §7. **Restituisce una stringa** (`'U'`) |
| `valida_codice_fiscale` | `stdnum.it.codicefiscale.validate(x)` | l'unica che implementa tutta la regola. Corrispondenza piena attesa |
| `normalizza_codice_fiscale` | `stdnum.it.codicefiscale.compact(x)` | pulisce e basta, non valida |
| `estrai_data_nascita` | `stdnum.it.codicefiscale.get_birth_date(x)` | **attenzione**: `stdnum` restituisce una data completa e *indovina il secolo*. Noi no, di proposito (§3). Confrontare solo giorno e mese |
| `estrai_sesso` | `stdnum.it.codicefiscale.get_gender(x)` | restituisce `'M'`/`'F'` come noi |
| `iniziali_cognome`, `iniziali_nome`, `sciogli_omocodia`, `genera_codice_fiscale` | *(nessuno)* | `stdnum` non li espone: solo vettori del §9 e proprietà |

**Non riscrivere l'algoritmo dentro il test** per poi confrontarlo con la
funzione: se chi ha scritto il test ha letto male questo documento, le due
copie sbagliano insieme e il verde conferma l'errore. L'oracolo sono i vettori
del §9 e la libreria di riferimento, non una seconda implementazione fatta in
casa.

---

## 11. Cosa questa fonte NON copre

Sono domini a sé, ognuno con la propria fonte da scrivere prima del task:

- **Tabella Belfiore** completa (codice ↔ comune/stato).
- **Codice fiscale dei soggetti diversi dalle persone fisiche** (11 cifre,
  numericamente identico a una partita IVA — vedi `partita_iva.md`).
- **Ricostruzione del comune di nascita** da un codice esistente.
- **Coerenza tra giorno e mese** rispetto al calendario reale.
