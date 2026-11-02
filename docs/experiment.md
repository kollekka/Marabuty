# Eksperyment: prognozowanie ceny ofertowej samochodu używanego

## Kontrakt eksperymentu

| Element | Ustalenie |
|---|---|
| Pytanie badawcze | Czy regresja log-liniowa przewiduje cenę ofertową samochodu używanego w Polsce dokładniej niż mediana ceny dla marki i modelu? |
| Wymaganie | R6: model na zbiorze testowym osiąga lepsze MAE, RMSE i R² niż baseline oraz MAPE ≤ ok. 15%. |
| Dane i wersja | `data/processed/sample-clean.csv`, wersja `7e1d8d4` (25 rekordów, 81 kolumn); źródło `data/raw/sample.csv`, wersja `5de74b3`; pełny eksport `data/full-2026-11-01.csv`, wersja `1d61fa0`. |
| Zakres i liczba obserwacji | 25 ogłoszeń z jednej migawki (2026-11-01); 20 treningowych i 5 testowych; tylko ceny ofertowe w PLN; próbka techniczna, nie reprezentatywna. |
| Metoda i punkt odniesienia | Regresja liniowa z karą L2 (Ridge, `alpha=1.0`) na `log1p(price_pln)`; baseline: mediana `price_pln` dla pary `make`+`model`, z fallbackiem do mediany `make`, a potem globalnej mediany z train. |
| Metryki | MAE (główna, PLN), RMSE (PLN), R², MAPE (%, tylko ceny > 0). |
| Kryterium praktyczne | R6: MAE i RMSE niższe, R² wyższe niż baseline na tym samym teście oraz MAPE ≤ 15%; przy 25 rekordach wynik jest orientacyjny. |
| Warunki porównania | Ten sam podział 80/20 (20/5), ziarno 42; baseline i model uczone wyłącznie na train; metryki na teście; test nie służy do strojenia. |
| Próba wrażliwości | Powtórzenie dla podziału 70/30 (17/8), ziarno 42; ocena, czy ranking metod i R6 się utrzymują. |
| Odtworzenie | Po otrzymaniu README i `results/lab4/` od Osoby B; uruchomienie w `.venv`, porównanie `comparison.csv` i wyników wrażliwości; szczegóły w sekcji Odtworzenie. |

## Pytanie i wymaganie

Pytanie badawcze dotyczy tego, czy prosty model regresyjny wykorzystujący parametry pojazdu poprawia orientacyjną wycenę względem najsilniejszego prostego punktu odniesienia, jakim jest mediana ceny dla marki i modelu.

Wymaganie R6 z `docs/problem.md` mówi, że model na zbiorze testowym ma osiągnąć lepsze MAE, RMSE i R² niż baseline oraz MAPE nie większe niż ok. 15%. Próg MAPE jest założeniem, a nie potwierdzonym wynikiem. Na próbce 25 rekordów test ma tylko 5 obserwacji, więc pojedynczy błąd mocno zmienia metryki. Eksperyment traktujemy jako test poprawności procedury, a nie rozstrzygnięcie o jakości modelu na rynku.

Hipoteza: dodanie roku, przebiegu, marki/modelu i parametrów technicznych powinno obniżyć MAE i RMSE oraz podnieść R² względem mediany dla marki i modelu. Nie zakładamy z góry, że MAPE ≤ 15% zostanie osiągnięte na tak małej próbce.

## Dane

Eksperyment korzysta z `data/processed/sample-clean.csv` (25 rekordów, 81 kolumn, wersja `7e1d8d4`). Plik powstał przez uruchomienie `scripts/prepare_data.py` na `data/raw/sample.csv` (25 rekordów, 103 kolumny, wersja `5de74b3`), czyli na losowej próbce technicznej z pełnego eksportu Otomoto (ziarno 42). Kontrole `scripts/quality_checks.py` przechodzą 10 z 10 kontroli, a w pliku nie ma braków w komórkach.

Pełny eksport `data/full-2026-11-01.csv` ma 233 040 rekordów i 103 kolumny (wersja `1d61fa0`). Według README pełne przetworzenie daje 228 318 rekordów i 81 kolumn, ale ten plik nie jest obecnie w repozytorium. Dlatego eksperyment wykonujemy na dostępnej próbce 25 rekordów i nie uogólniamy wyników na cały rynek. Po udostępnieniu pełnego pliku przetworzonego należy powtórzyć procedurę.

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

## Odtworzenie

A4 nie zostało jeszcze wykonane, ponieważ Osoba B nie dostarczyła README z poleceniem uruchomienia porównania ani katalogu `results/lab4/` z plikami `comparison.csv`, `observations.csv` i wynikami próby wrażliwości. Nie wpisujemy wyników bez uruchomienia.

Lista kontrolna po otrzymaniu materiałów:

1. Sprawdzić wersję danych i kod z README B; zapisać commit, na którym wykonano odtworzenie.
2. Utworzyć i aktywować `.venv`, zainstalować zależności z `requirements.txt` oraz ewentualne zależności modelowania podane w README B.
3. Uruchomić dokładnie komendę z README B, bez modyfikowania parametrów podziału ani ziarna.
4. Sprawdzić, czy powstały `results/lab4/comparison.csv`, `results/lab4/observations.csv` oraz pliki próby wrażliwości.
5. Porównać liczby z kontraktem: 20/5 dla 80/20, 17/8 dla 70/30, ziarno 42, baseline mediany `make`+`model`, metryki MAE, RMSE, R² i MAPE.
6. Zapisać w tej sekcji datę, commit, użyte polecenie, uzyskane metryki i różnice względem wyników B.

Tolerancja odtworzenia: liczba rekordów i przypisanie wierszy do train/test muszą być identyczne. Metryki porównujemy z dokładnością do 0,01 PLN lub 0,01 p.p.; różnicę większą niż 1% względem wyniku B traktujemy jako rozbieżność wymagającą wyjaśnienia. Brak pliku wynikowego lub inna liczba wierszy oznacza, że A4 nie jest odtworzone.
