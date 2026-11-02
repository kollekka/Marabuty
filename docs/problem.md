# Problem projektu

## Temat

Prognozowanie cen używanych samochodów osobowych na polskim rynku ogłoszeń z wykorzystaniem modelu regresyjnego.

## Opis

Cena samochodu używanego zależy od wielu parametrów, między innymi marki, modelu, rocznika, przebiegu, silnika, paliwa, skrzyni biegów i lokalizacji. Ceny ofert podobnych aut mogą się różnić, dlatego kupujący i sprzedający nie zawsze wiedzą, czy konkretna oferta jest bliska cenie rynkowej.

Projekt sprawdzi, jak dokładnie można przewidywać cenę ofertową na podstawie danych o pojeździe oraz które cechy najsilniej wiążą się z ceną. Wynik ma mieć charakter orientacyjny: zbiór zawiera ceny z ogłoszeń, a nie potwierdzone ceny transakcyjne.

## Odbiorcy

Osoby kupujące lub sprzedające samochód używany w Polsce, a dodatkowo małe komisy i handlarze potrzebujący punktu odniesienia przy wycenie.

## Planowany rezultat

Prototyp aplikacji webowej: backend w Pythonie (FastAPI, scikit-learn) udostępnia model przez REST API, a frontend w React zawiera formularz parametrów pojazdu i zwraca prognozę ceny w PLN z przedziałem niepewności oraz oceną oferty. Do tego krótki raport analityczny: eksploracja danych, porównanie metod regresyjnych, metryki jakości i ranking ważności cech.

## Użytkownik i decyzja

Główny użytkownik: osoba kupująca lub sprzedająca używany samochód osobowy w Polsce. Dodatkowo: małe komisy i handlarze wyceniający auta przy skupie i wystawianiu ogłoszeń.

Decyzja wspierana przez rozwiązanie: czy konkretna oferta jest zawyżona, zaniżona, czy zbliżona do ceny rynkowej; jaką cenę zaproponować w negocjacjach lub za ile wystawić własne auto. Wynik ma charakter orientacyjny, a nie wiążącej wyceny.

## Obecna trudność

- Cena zależy jednocześnie od wielu cech: marki i modelu, roku produkcji, przebiegu, silnika, paliwa, skrzyni biegów, nadwozia i lokalizacji.
- Rynek jest rozproszony, a ceny podobnych aut mocno się różnią.
- Kupujący i sprzedający porównują ogłoszenia ręcznie — jest to czasochłonne i subiektywne.
- Skutki: przepłacanie, długie wystawianie oferty po zawyżonej cenie, sprzedaż poniżej wartości.
- Brak prostego punktu odniesienia dla konkretnej oferty.

## Zakres problemu

W zakresie:

- prognoza ceny ofertowej w PLN na podstawie parametrów pojazdu,
- przedział niepewności prognozy i ocena oferty względem prognozy,
- ranking ważności cech,
- porównanie co najmniej trzech metod (regresja liniowa/log-liniowa, model drzewiasty).

Poza zakresem pierwszej wersji:

- dane na żywo z portali ogłoszeniowych w aplikacji,
- konta użytkowników,
- prognoza zmian cen w czasie,
- ceny transakcyjne.

Miary jakości: MAE, RMSE, MAPE, R². Wstępny cel MAPE ok. 15%, do weryfikacji po EDA.

## Potrzebne dane

- Źródło główne: publiczne ogłoszenia Otomoto.pl pozyskane własnym eksportem opartym na `simonloach/car-scraper` (MIT); pełny eksport `data/full-2026-11-01.csv` ma 233 040 rekordów i 103 kolumny.
- Źródło pomocnicze: publiczny zbiór Kaggle „Poland cars for sale dataset” (starsza migawka, 208 304 rekordy) — tylko do porównania i testowania pipeline'u.
- Zmienna objaśniana: `price_pln` w PLN (w danych występuje też 211 ogłoszeń w EUR).
- Predyktory: m.in. `make`, `model`, `year`, `mileage_km`, `engine_cc`, `engine_power_km`, `fuel_type`, `gearbox`, `transmission`, `body_type`, `city`, `region`; pełny zestaw po EDA.
- Ograniczenia: braki danych, możliwe wartości odstające i błędy wpisywania; ceny ofertowe, nie transakcyjne; migawka z jednego okresu (eksport 2026-11-01/02).
- Szczegóły źródła, braków i zasad użycia: `docs/data.md`.

## Założenia i pytania otwarte

Założenia:

- prognoza dotyczy polskiego rynku i samochodów osobowych,
- dane z jednego okresu wystarczą do prototypu,
- cena ofertowa jest akceptowalnym przybliżeniem ceny rynkowej,
- model będzie trenowany na danych po czyszczeniu, z ustalonym ziarnem losowości,
- na start stosujemy losowy podział train/test i walidację krzyżową; decyzja o podziale czasowym po EDA.

Pytania otwarte:

- Jakie są dokładne warunki wykorzystania danych Otomoto i czy publikacja prototypu jest zgodna z regulaminem?
- Czy wersja językowa i jednostki (`engine_power_km`, `engine_cc`) są spójne w całym zbiorze?
- Czy rekordy bez `make`/`model`/`year` (4 014) należy odrzucić, czy da się je uzupełnić?
- Czy ogłoszenia w EUR (211) przeliczać na PLN, czy wyłączyć z modelowania?
- Czy pola `vin` i `first_registration` (100% braków) oraz `district` (73% braków) są użyteczne?
- Czy docelowy próg MAPE ok. 15% jest realny po EDA?

## Kryteria sukcesu

1. Model osiąga na zbiorze testowym lepsze wyniki niż prosty punkt odniesienia (średnia lub mediana ceny dla marki i modelu), mierzone MAE, RMSE i R².
2. Błąd względny (MAPE) na zbiorze testowym mieści się w założonym progu; wstępnie cel to ok. 15%, do weryfikacji po EDA.
3. Porównanie co najmniej 3 metod jest odtwarzalne (jeden skrypt/notebook, ustalone ziarno losowości) i uzasadnia wybór modelu końcowego.
4. Aplikacja (React + API w Pythonie) zwraca prognozę dla poprawnych danych wejściowych w kilka sekund i poprawnie obsługuje błędne dane (walidacja formularza i API).
