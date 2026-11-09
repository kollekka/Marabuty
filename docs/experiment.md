# Eksperyment: prognozowanie ceny ofertowej samochodu używanego

## Kontrakt eksperymentu

| Element | Ustalenie |
|---|---|
| Pytanie badawcze | Czy regresja log-liniowa przewiduje cenę ofertową samochodu używanego w Polsce dokładniej niż mediana ceny dla marki i modelu? |
| Wymaganie | R6: model na zbiorze testowym osiąga lepsze MAE, RMSE i R² niż baseline oraz MAPE ≤ ok. 15%. |
| Dane i wersja | `data/processed/sample-clean.csv`, wersja z commita `feat: wynik czyszczenia` (25 rekordów, 81 kolumn); źródło `data/raw/sample.csv`, wersja z commita `przeniesienie próbki do data/raw/`; pełny eksport `data/full-2026-11-01.csv` (233 040 rekordów, 103 kolumny, migawka z 2026-11-01). |
| Zakres i liczba obserwacji | 25 ogłoszeń z jednej migawki (2026-11-01); 20 treningowych i 5 testowych; tylko ceny ofertowe w PLN; próbka techniczna, nie reprezentatywna. |
| Metoda i punkt odniesienia | Regresja liniowa z karą L2 (Ridge, `alpha=1.0`) na `log1p(price_pln)`; baseline: mediana `price_pln` dla pary `make`+`model`, z fallbackiem do mediany `make`, a potem globalnej mediany z train. |
| Metryki | MAE (główna, PLN), RMSE (PLN), R², MAPE (%, tylko ceny > 0). |
| Kryterium praktyczne | R6: MAE i RMSE niższe, R² wyższe niż baseline na tym samym teście oraz MAPE ≤ 15%; przy 25 rekordach wynik jest orientacyjny. |
| Warunki porównania | Ten sam podział 80/20 (20/5), ziarno 42; baseline i model uczone wyłącznie na train; metryki na teście; test nie służy do strojenia. |
| Próba wrażliwości | Powtórzenie dla podziału 70/30 (17/8), ziarno 42; ocena, czy ranking metod i R6 się utrzymują. |
| Odtworzenie | Wykonane 2026-11-02 na commitcie `docs: README Lab 4`; wyniki identyczne z plikami Osoby B; szczegóły i wnioski w sekcji Odtworzenie. |

## Pytanie i wymaganie

Pytanie badawcze dotyczy tego, czy prosty model regresyjny wykorzystujący parametry pojazdu poprawia orientacyjną wycenę względem najsilniejszego prostego punktu odniesienia, jakim jest mediana ceny dla marki i modelu.

Wymaganie R6 z `docs/problem.md` mówi, że model na zbiorze testowym ma osiągnąć lepsze MAE, RMSE i R² niż baseline oraz MAPE nie większe niż ok. 15%. Próg MAPE jest założeniem, a nie potwierdzonym wynikiem. Na próbce 25 rekordów test ma tylko 5 obserwacji, więc pojedynczy błąd mocno zmienia metryki. Eksperyment traktujemy jako test poprawności procedury, a nie rozstrzygnięcie o jakości modelu na rynku.

Hipoteza: dodanie roku, przebiegu, marki/modelu i parametrów technicznych powinno obniżyć MAE i RMSE oraz podnieść R² względem mediany dla marki i modelu. Nie zakładamy z góry, że MAPE ≤ 15% zostanie osiągnięte na tak małej próbce.

## Dane

Eksperyment korzysta z `data/processed/sample-clean.csv` (25 rekordów, 81 kolumn, wersja z commita `feat: wynik czyszczenia`). Plik powstał przez uruchomienie `scripts/prepare_data.py` na `data/raw/sample.csv` (25 rekordów, 103 kolumny, wersja z commita `przeniesienie próbki do data/raw/`), czyli na losowej próbce technicznej z pełnego eksportu Otomoto (ziarno 42). Kontrole `scripts/quality_checks.py` przechodzą 10 z 10 kontroli, a w pliku nie ma braków w komórkach.

Pełny eksport `data/full-2026-11-01.csv` ma 233 040 rekordów i 103 kolumny (migawka z 2026-11-01). Według README pełne przetworzenie daje 228 318 rekordów i 81 kolumn, ale ten plik nie jest obecnie w repozytorium. Dlatego eksperyment wykonujemy na dostępnej próbce 25 rekordów i nie uogólniamy wyników na cały rynek. Po udostępnieniu pełnego pliku przetworzonego należy powtórzyć procedurę.

W próbce `price_pln` wynosi od 4 699 do 830 900 PLN, a mediana to 49 700 PLN. `year` zawiera się w przedziale 2008–2026, a `mileage_km` w przedziale 10–304 000 km. Wiele par `make`+`model` występuje tylko raz; zaledwie kilka grup ma co najmniej dwie obserwacje. To utrudnia baseline i zwiększa wariancję wyniku.

Predyktory w kontrakcie: `make`, `model`, `year`, `mileage_km`, `engine_cc`, `engine_power_km`, `fuel_type`, `gearbox`, `transmission`, `body_type`, `new_used` i `region`. `city` dopuszczamy jako wariant, jeśli po kodowaniu nie rozjeżdża wymiaru. `generation` i `district` pomijamy w pierwszym modelu z powodu braków i wysokiej liczebności poziomów. Flag `has_*` nie używamy w pierwszym modelu, bo przy 20 wierszach train ich liczba groziłaby przeuczeniem.

Do modelu nie wchodzą `id`, `url`, `seller_id`, `seller_name`, `created_at`, `updated_at`, `first_seen`, `last_seen`, `enriched_at`, `status`, `state`, `attempts`, `last_error` ani cechy pochodne od ceny. `title` pomijamy, bo duplikuje informacje o marce i modelu. `currency` po filtrze PLN jest stała. `vin` i `first_registration` są puste, a `district` ma ponad 70% braków.

## Warunki porównania

Podział: `train_test_split(test_size=0.2, random_state=42)` daje 20 wierszy train i 5 wierszy test. Baseline i model dostają dokładnie ten sam zbiór treningowy i testowy. Ze względu na małą próbę nie stratyfikujemy podziału.

Baseline: dla każdego wiersza testowego bierzemy medianę `price_pln` z train dla pary `make`+`model`. Jeśli pary nie ma w train, bierzemy medianę dla `make`. Jeśli nadal brak, bierzemy globalną medianę `price_pln` z train. Mediany liczymy wyłącznie na train.

Model: `Pipeline` z imputacją liczb medianą, imputacją kategorii najczęstszą wartością i one-hot encodingiem z `handle_unknown="ignore"` oraz grupowaniem rzadkich poziomów (`min_frequency=2`). Kodowanie i imputacja są dopasowywane tylko na train. Cel jest przekształcany przez `log1p`, a predykcje wracamy przez `expm1`; metryki liczymy na PLN. Używamy regresji Ridge z `alpha=1.0`, bo przy 20 wierszach train i wielu poziomach `make`/`model` zwykła regresja OLS może być niestabilna. `alpha` jest ustalona z góry i nie jest strojona na teście.

Metryki na zbiorze testowym:

- MAE = średnia z |`price_pln` − prognoza|, w PLN; metryka główna.
- RMSE = pierwiastek ze średniej kwadratów błędów, w PLN.
- R² = 1 − suma kwadratów reszt / suma kwadratów odchyleń od średniej testu.
- MAPE = średnia z |(`price_pln` − prognoza) / `price_pln`| × 100%; liczymy tylko dla cen > 0.

Nie stroimy modelu ani baseline na teście. Jeśli w przyszłości pojawi się strojenie hiperparametrów, odbywa się ono wyłącznie w walidacji krzyżowej na train.

## Weryfikacja ręczna

Wartości oczekiwane policzono niezależnie od kodu i wyników Osoby B. Obliczenia wykonano w osobnym `git worktree` na commicie `bfbb9b6`, który zawiera kontrakt i `data/processed/sample-clean.csv`, ale nie zawiera jeszcze `results/lab4/`. Katalog roboczy nie miał dostępu do plików wynikowych. Użyto Pythona 3.9.13, pandas 2.3.3 i scikit-learn 1.6.1.

Podział jest zgodny z kontraktem: `train_test_split(test_size=0.2, random_state=42)` daje 20 wierszy train i 5 wierszy test o indeksach 8, 16, 0, 23 i 11.

### Baseline

Dla przypadku `row_index=8` (Peugeot 2008, 2013, 140 315 km, cena 24 900 PLN) stosujemy wzór:

```text
ŷ = mediana_train(price_pln | make, model)
jeśli brak pary: ŷ = mediana_train(price_pln | make)
jeśli brak marki: ŷ = mediana_train(price_pln)
```

Kroki:

1. Pary `Peugeot`+`2008` nie ma w train.
2. Marki `Peugeot` nie ma w train.
3. Globalna mediana `price_pln` w train wynosi 51 849,50 PLN.
4. Prognoza baseline: 51 849,50 PLN.
5. Błąd bezwzględny: |24 900,00 − 51 849,50| = 26 949,50 PLN.
6. APE: 26 949,50 / 24 900,00 × 100% = 108,23%.

### Ridge

Model jest uczony na `log1p(price_pln)`, a prognozę wracamy wzorem:

```text
z = w0 + Σ wj·xj
ŷ = expm1(z)
```

Po imputacji, one-hot encoding i grupowaniu rzadkich poziomów przypadek ma 39 cech. Wyraz wolny wynosi −265,5810068059, a suma iloczynów cech i współczynników daje `z = 9,2995532916`. Po odwróceniu logarytmu:

```text
ŷ = expm1(9,2995532916) = 10 932,13 PLN
```

Błąd bezwzględny: |24 900,00 − 10 932,13| = 13 967,87 PLN. APE: 13 967,87 / 24 900,00 × 100% = 56,10%.

Największy wkład w `z` ma `num__year` (+274,821320), a następnie `num__engine_power_km` (+0,448968). Pozostałe cechy mają mniejsze wkłady.

### Miara zbiorcza

MAE liczymy ze wzoru:

```text
MAE = (1/n) · Σ |yi − ŷi|
```

Dla 5 przypadków testowych suma błędów bezwzględnych baseline wynosi 928 499,50 PLN, więc MAE = 928 499,50 / 5 = 185 699,90 PLN. Dla Ridge suma błędów wynosi 197 653,12 PLN, więc MAE = 197 653,12 / 5 = 39 530,62 PLN.

### Wartości oczekiwane

| Element | Wartość oczekiwana |
|---|---:|
| Baseline — prognoza dla `row_index=8` | 51 849,50 PLN |
| Baseline — błąd bezwzględny | 26 949,50 PLN |
| Baseline — APE | 108,23% |
| Ridge — prognoza dla `row_index=8` | 10 932,13 PLN |
| Ridge — błąd bezwzględny | 13 967,87 PLN |
| Ridge — APE | 56,10% |
| Baseline — MAE na 5 testach | 185 699,90 PLN |
| Ridge — MAE na 5 testach | 39 530,62 PLN |

Wartości są zaokrąglone do 2 miejsc po przecinku. Służą jako punkt odniesienia w sekcji „Porównanie i interpretacja”; nie kopiowano ich z `results/lab4/`.

## Źródła literaturowe i uzasadnienie metody

Wybór regresji log-liniowej wynika z charakteru zmiennej: cena jest ciągła, dodatnia i silnie skośna, a logarytm stabilizuje wariancję i ogranicza wpływ skrajnych cen. Regresja liniowa daje też interpretowalne współczynniki i jest naturalnym punktem wyjścia przed modelami drzewiastymi. Baseline mediany dla marki i modelu jest mocnym, prostym odniesieniem, bo w danych o samochodach marka i model silnie różnicują cenę.

| Źródło | Co uzasadnia | Weryfikacja |
|---|---|---|
| James, Witten, Hastie, Tibshirani, *An Introduction to Statistical Learning*, 2nd ed., 2021, rozdz. 3 „Linear Regression”, `https://www.statlearning.com/` | Podstawy regresji liniowej, ocena jakości dopasowania, MSE i R², interpretacja współczynników. | Sprawdzono stronę wydania i spis treści; rozdział 3 jest dostępny w legalnym PDF wydania. |
| Bukvić, Pašagić Škrinjar, Fratrović, Abramović, *Price Prediction and Classification of Used-Vehicles Using Supervised Machine Learning*, *Sustainability* 14(24), 17034, 2022, `https://doi.org/10.3390/su142417034` | Zastosowanie regresji liniowej do predykcji cen używanych samochodów na rynku chorwackim; cechy roku produkcji i przebiegu; porównanie z random forest i SVM. | Sprawdzono pełny tekst PDF (17 s., CC BY). W tabeli 3 regresja liniowa miała R² 0,95, RMSE 2104,7 i MAE 1373,2; random forest R² 0,24, a SVM R² 0,59. |

W przywołanym badaniu regresja liniowa wypadła lepiej niż random forest i SVM na tablicowych danych o używanych samochodach. Nie przenosimy jednak tych liczb na nasz zbiór: rynek, cechy i podział danych są inne, a nasza próbka ma 25 rekordów. Wynik ten uzasadnia jedynie wybór prostego modelu liniowego jako pierwszego, a nie twierdzenie o powtarzalności R² 0,95.

Odrzucona alternatywa na tym etapie: random forest. Przy 20 wierszach train model drzewiasty łatwo przeucza się i jest mniej interpretowalny, a przywołane badanie nie daje podstaw, by zaczynać od niego na tablicowych danych z małą liczbą obserwacji. Random forest pozostaje w zakresie projektu jako późniejszy model porównawczy, zgodnie z wymaganiem R4.

## Plan próby wrażliwości i kryterium praktyczne

Próba wrażliwości polega na powtórzeniu całej procedury dla podziału 70/30 zamiast 80/20, z tym samym ziarnem 42. Przy 25 rekordach daje to 17 wierszy train i 8 wierszy test. Baseline i model są ponownie uczone od zera na nowym train, a metryki liczone na nowym teście. Nie zmieniamy `alpha` ani zestawu cech, żeby zmiana dotyczyła tylko podziału.

Raport powinien zawierać tabelę z metrykami baseline i modelu dla obu podziałów oraz różnicę względną MAE. Interpretacja:

- Jeśli model wygrywa z baseline w obu podziałach i MAPE w obu przypadkach nie przekracza 15%, wniosek jest odporny na zmianę proporcji podziału w ramach tej próbki.
- Jeśli model wygrywa tylko przy 80/20, wynik jest wrażliwy na podział i nie daje podstaw do twierdzenia, że R6 jest spełnione.
- Jeśli ranking metod się odwraca, baseline jest lepszy i model liniowy nie jest uzasadniony na tych danych.
- Przy 5–8 wierszach testowych każdy wniosek jest słaby; pełne rozstrzygnięcie wymaga powtórzenia na przetworzonym pełnym zbiorze 228 318 rekordów.

Kryterium praktyczne to spełnienie R6: MAE i RMSE niższe oraz R² wyższe niż baseline, a MAPE ≤ 15%. Sama minimalna poprawa jednej metryki nie wystarcza do decyzji wdrożeniowej. Przy tak małej próbce raportujemy również bezwzględne wartości błędów, żeby nie ukrywać niepewności za samym rankingiem.

## Porównanie i interpretacja

Kontrola `scripts/check_results.py` przeszła 10 z 10 kontroli dla `results/lab4/` i 10 z 10 dla `results/lab4/sensitivity/`; kod wyjścia wyniósł 0. Pełny log znajduje się w `data/test/lab4-check-results.log`. Sekcja A4 potwierdziła wcześniej odtwarzalność plików, więc poniżej nie powtarzamy testu bajtowego.

### Zgodność wartości oczekiwanych z wynikami

| Element | C1 — wartość oczekiwana | B — wynik | Różnica |
|---|---:|---:|---:|
| Baseline — prognoza `row_index=8` | 51 849,50 PLN | 51 849,50 PLN | 0,00 PLN |
| Ridge — prognoza `row_index=8` | 10 932,13 PLN | 10 932,13 PLN | 0,00 PLN |
| Baseline — błąd `row_index=8` | 26 949,50 PLN | 26 949,50 PLN | 0,00 PLN |
| Ridge — błąd `row_index=8` | 13 967,87 PLN | 13 967,87 PLN | 0,00 PLN |
| Baseline — APE `row_index=8` | 108,23% | 108,23% | 0,00 p.p. |
| Ridge — APE `row_index=8` | 56,10% | 56,10% | 0,00 p.p. |
| Baseline — MAE | 185 699,90 PLN | 185 699,90 PLN | 0,00 PLN |
| Ridge — MAE | 39 530,62 PLN | 39 530,62 PLN | 0,00 PLN |

Różnice mieszczą się w tolerancji przyjętej dla zaokrągleń. Oznacza to, że niezależne obliczenie C1 i wynik skryptu B opisują tę samą procedurę.

### Wyniki i kryterium R6

| Podział | Metoda | MAE [PLN] | RMSE [PLN] | R² | MAPE [%] | Różnica MAE vs baseline |
|---|---|---:|---:|---:|---:|---:|
| 80/20 | baseline | 185 699,90 | 350 138,20 | −0,2127 | 149,84 | — |
| 80/20 | ridge | 39 530,62 | 65 989,83 | 0,9569 | 33,35 | −146 169,28 (−78,71%) |
| 70/30 | baseline | 135 692,44 | 280 966,13 | −0,1587 | 137,49 | — |
| 70/30 | ridge | 20 386,01 | 30 384,92 | 0,9864 | 25,84 | −115 306,43 (−84,98%) |

### Odpowiedzi na pytania interpretacyjne

1. **Który wariant jest lepszy i o ile?** Ridge jest lepszy w obu podziałach. Przy 80/20 obniża MAE o 146 169,28 PLN, czyli o 78,71%, a przy 70/30 o 115 306,43 PLN, czyli o 84,98%. Ma też niższe RMSE i wyższe R² niż baseline.
2. **Czy spełnia kryterium R6?** Tylko częściowo. MAE, RMSE i R² są lepsze od baseline w obu podziałach, ale MAPE wynosi 33,35% dla 80/20 i 25,84% dla 70/30, więc przekracza próg ok. 15%. R6 nie jest spełnione w zakresie MAPE.
3. **Czy zmiana parametru zmienia wniosek?** Nie zmienia rankingu. Po przejściu z 80/20 na 70/30 Ridge nadal wygrywa, a MAPE nadal przekracza 15%. Wniosek kierunkowo się utrzymuje, choć zmienia się skala poprawy MAE.
4. **Czego nie wolno wywnioskować?** Nie można twierdzić o przyczynowym wpływie cech na cenę, o wynikach dla całego rynku ani o cenach transakcyjnych. Przy 25 rekordach i 5–8 obserwacjach testowych nie ma podstaw do uogólniania na pełny zbiór 228 318 rekordów ani do twierdzenia, że próg MAPE zostanie osiągnięty poza tą próbką. Wynik baseline zależy od fallbacku median dla par i marek.

## Ograniczenia

- Próba liczy 25 rekordów, a zbiór testowy 5 lub 8 obserwacji. Pojedynczy błąd mocno zmienia metryki, więc wynik jest orientacyjny.
- Dane pochodzą z jednej migawki z 2026-11-01. Nie pozwalają ocenić sezonowości ani zmian cen w czasie.
- Ceny są ofertowe, a nie transakcyjne. Model uczy się oczekiwań sprzedających, nie rzeczywistych cen sprzedaży.
- Brak niezależnego zbioru końcowego. Test posłużył do oceny, ale nie do strojenia; nie ma jednak zewnętrznej walidacji na innym okresie lub rynku.
- Baseline z fallbackiem `make+model → make → globalna mediana` jest czuły na pary i marki niewystępujące w train. Wiele par pojawia się tylko raz.
- Brakuje przetworzonego pełnego zbioru 228 318 rekordów, cen transakcyjnych i historii cen. Nie można uogólniać wyniku na cały rynek ani twierdzić, że próg MAPE 15% zostanie osiągnięty poza próbką.
- Dane są rzeczywiste, nie syntetyczne. Ograniczeniem jest mała, techniczna i niereprezentatywna próbka, a nie sposób ich wygenerowania.

## Użycie AI

| Narzędzie | Do czego użyto | Co zweryfikowano |
|---|---|---|
| Asystent AI (opencode) | Redakcja i uporządkowanie sekcji C1–C4, propozycja listy kontroli w `check_results.py`, pomoc w zapisie wzorów i języka dokumentacji. | Wszystkie liczby pochodzą z niezależnego obliczenia C1 i plików `results/lab4/`; skrypt kontroli uruchomiono na obu katalogach i na kopii z błędem. Źródeł literaturowych nie generowano ponownie — pozostały w sekcji. |
| Asystent AI (opencode) | Sprawdzenie spójności nagłówków, tabel i poleceń uruchomienia. | Porównano nagłówki z szablonem, uruchomiono `check_results.py`, sprawdzono kod wyjścia i brak zmian w plikach. |

AI nie było źródłem danych ani wyników. Nie tworzono nowych publikacji ani nie zmieniano parametrów po obejrzeniu wyników.

## Odtworzenie

A4 wykonano 2026-11-02 na commitcie `docs: README Lab 4`. Użyto `.venv` z Pythonem 3.13.5, pandas 3.1.0 i scikit-learn 1.9.1. Uruchomiono dokładnie polecenia z README Osoby B:

```powershell
python scripts/compare_methods.py data/processed/sample-clean.csv --output-dir results/lab4 --test-size 0.2 --seed 42
python scripts/compare_methods.py data/processed/sample-clean.csv --output-dir results/lab4/sensitivity --test-size 0.3 --seed 42
```

Wyniki na teście:

| Podział | Metoda | n_train | n_test | MAE [PLN] | RMSE [PLN] | R² | MAPE [%] |
|---|---|---:|---:|---:|---:|---:|---:|
| 80/20 | baseline | 20 | 5 | 185 699,90 | 350 138,20 | −0,2127 | 149,84 |
| 80/20 | ridge | 20 | 5 | 39 530,62 | 65 989,83 | 0,9569 | 33,35 |
| 70/30 | baseline | 17 | 8 | 135 692,44 | 280 966,13 | −0,1587 | 137,49 |
| 70/30 | ridge | 17 | 8 | 20 386,01 | 30 384,92 | 0,9864 | 25,84 |

Odtworzenie jest zgodne z wynikami: wszystkie cztery pliki (`results/lab4/comparison.csv`, `results/lab4/observations.csv`, `results/lab4/sensitivity/comparison.csv`, `results/lab4/sensitivity/observations.csv`) są identyczne co do bajtu (zgodne sumy SHA256). Różnica metryk wynosi 0, więc przyjęta tolerancja została spełniona.

### Wnioski

R6 jest spełnione częściowo. Model Ridge bije baseline w MAE, RMSE i R² w obu podziałach: przy 80/20 obniża MAE o 146 169,28 PLN (−78,71%), a przy 70/30 o 115 306,43 PLN (−84,98%). Jednocześnie MAPE nie schodzi poniżej progu 15% i wynosi 33,35% dla 80/20 oraz 25,84% dla 70/30.

Na 5–8 obserwacjach testowych jest to wynik orientacyjny, a nie rozstrzygnięcie o jakości modelu na rynku. Pojedyncza droga lub tania obserwacja może silnie zmienić MAPE, a baseline z medianą dla marki i modelu jest szczególnie wrażliwy na brak tej samej pary w train. Dodatni i wysoki R² modelu oraz ujemny R² baseline oznaczają, że na tej próbce model jest wyraźnie lepszy, ale nie dowodzą powtarzalności na pełnym zbiorze.

Wniosek praktyczny: model można traktować jako obiecujący punkt wyjścia, ale R6 nie jest w pełni spełnione, dopóki MAPE nie spadnie do ok. 15%. Kolejny krok to powtórzenie procedury na pełnym przetworzonym zbiorze 228 318 rekordów i sprawdzenie, czy poprawa względem baseline oraz poziom MAPE utrzymują się poza próbką 25 rekordów.
