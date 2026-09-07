# Chart Pattern Scout

Scanner saptamanal de pattern-uri chartiste, inspirat de conceptul Grok Bot al lui Jordi Visser.
Descarca date de la Yahoo Finance pentru o watchlist de ~90 tickere + 6 crypto, detecteaza geometric
9 tipuri de pattern-uri (Head & Shoulders, Double Top/Bottom, Round Bottom, Cup & Handle, triunghiuri,
Rectangle/Range, linii de trend), confirma cu volum, deseneaza chart-uri, publica un raport HTML.

## Cum functioneaza

- Ruleaza automat in fiecare **vineri** dupa close-ul pietei americane (GitHub Actions, gratuit)
- Poate fi rulat si manual din tab-ul **Actions** al repo-ului (buton "Run workflow")
- Rezultatul e publicat ca pagina web (GitHub Pages) — link fix, accesibil de pe orice telefon/tableta
- Retine starea intre rulari (`docs/scan_state.json`), ca sa marcheze ce e nou fata de saptamana trecuta

## Setup (o singura data)

1. **Creeaza un repo nou** pe GitHub (poate fi privat), de exemplu `chart-pattern-scout`
2. **Incarca toate fisierele din acest folder** in repo (pastreaza structura de directoare, inclusiv `.github/workflows/scan.yml`)
3. In repo, mergi la **Settings → Pages** → sub "Build and deployment", la "Source" alege **GitHub Actions**
4. Mergi la tab-ul **Actions** → daca vezi workflow-ul "Chart Pattern Scout - scan saptamanal", apasa **Run workflow** ca sa testezi manual prima data
5. Dupa ce ruleaza (~5-10 minute), link-ul raportului apare in Settings → Pages (ceva de forma `https://<user>.github.io/chart-pattern-scout/`)

## Structura fisierelor

- `tickers.py` — watchlist-ul (~90 tickere + 6 crypto), cu maparea sector→ETF de referinta
- `pivots.py` — detectare pivot points (extreme locale) si confirmare volum
- `patterns.py` — cei 9 detectori de pattern-uri geometrice
- `plotting.py` — deseneaza chart-uri candlestick cu pattern-ul suprapus
- `scan.py` — orchestreaza tot: descarca, detecteaza, deseneaza
- `report.py` — genereaza raportul HTML final
- `.github/workflows/scan.yml` — configurarea rularii automate

## Ajustare prag calitate

In `scan.py`, variabila `MIN_QUALITY = 55` controleaza pragul minim de calitate (0-100) pentru ca
un pattern sa apara in raport. Creste-l daca vrei mai putine hit-uri (mai stricte), scade-l pentru mai multe.

## Limitari cunoscute

- **SK Hynix** (`000660.KS`) e listat pe bursa din Seul; datele Yahoo pot avea intarzieri sau lipsuri ocazionale
- Detectia e euristica, nu perfecta — un pattern "confirmat" e un semnal de research, nu o garantie
- Research-ul de stiri/sentiment social (mentionat in conversatia initiala) NU e inclus in acest script —
  ramane un pas separat, facut manual (in chat cu Claude) pornind de la hit-urile din raport
