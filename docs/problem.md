# Problem projektu

## Użytkownik i decyzja

Główny użytkownik: osoba kupująca lub sprzedająca używany samochód osobowy w Polsce. Dodatkowo: małe komisy i handlarze wyceniający auta przy skupie i wystawianiu ogłoszeń.

Decyzja wspierana przez rozwiązanie: czy konkretna oferta jest zawyżona, zaniżona, czy bliska ceny rynkowej; jaką cenę zaproponować w negocjacjach i za ile wystawić własne auto. Wynik ma charakter orientacyjny, a nie wiążący.

## Obecna trudność

- Cena zależy jednocześnie od wielu cech: marki i modelu, roku produkcji, przebiegu, silnika, paliwa, skrzyni biegów, nadwozia i lokalizacji.
- Rynek jest rozproszony, a ceny podobnych aut mocno się różnią.
- Kupujący i sprzedający porównują ogłoszenia ręcznie, co jest czasochłonne i subiektywne.
- Skutki: przepłacanie, długie wystawianie oferty po zawyżonej cenie, sprzedaż poniżej wartości.
- Brak prostego punktu odniesienia dla konkretnej oferty.

## Zakres problemu

W zakresie:

- prognoza ceny ofertowej w PLN na podstawie parametrów pojazdu,
- przedział niepewności prognozy i ocena oferty względem prognozy,
- ranking ważności cech,
- porównanie co najmniej trzech metod: regresja liniowa/log-liniowa oraz model drzewiasty.

Poza zakresem pierwszej wersji:

- dane na żywo z portali ogłoszeniowych w aplikacji,
- konta użytkowników,
- prognoza zmian cen w czasie,
- ceny transakcyjne.

Miary jakości: MAE, RMSE, MAPE, R². Wstępny cel MAPE ok. 15% jest założeniem do weryfikacji po EDA.

## Potrzebne dane

- Źródło główne: publiczne ogłoszenia Otomoto.pl pozyskane własnym eksportem opartym na `MrKabas/Otomoto-Scraper` (MIT, autor: Kacper Stopa); plik `data/full-2026-11-01.csv` zawiera 233 040 rekordów i 103 kolumny.
- Źródło pomocnicze: zbiór Kaggle „Poland cars for sale dataset” (migawka z 2021 r., 208 304 rekordy) do testowania pipeline'u i porównania.
- Zmienna objaśniana: `price_pln` w PLN; w zbiorze jest też 211 ogłoszeń w EUR.
- Predyktory: m.in. `make`, `model`, `year`, `mileage_km`, `engine_cc`, `engine_power_km`, `fuel_type`, `gearbox`, `transmission`, `body_type`, `city`, `region`; ostateczny zestaw po EDA.
- Ograniczenia: braki danych, wartości odstające i błędy wpisywania; ceny ofertowe, nie transakcyjne; jedna migawka z 2026-11-01.
- Szczegóły źródła i zasad użycia: `docs/data.md`.

## Założenia i pytania otwarte

Założenia:

- prognoza dotyczy polskiego rynku i samochodów osobowych,
- cena ofertowa jest akceptowalnym przybliżeniem ceny rynkowej,
- jedna migawka danych wystarczy do prototypu,
- model będzie trenowany na danych po czyszczeniu, z ustalonym ziarnem losowości,
- na start stosujemy losowy podział train/test i walidację krzyżową.

Pytania otwarte:

- Jakie są warunki wykorzystania danych Otomoto i czy publikacja prototypu jest z nimi zgodna?
- Czy rekordy bez `make`/`model`/`year` (4 014) odrzucić, czy uzupełnić?
- Czy 211 ogłoszeń w EUR przeliczać na PLN, czy wyłączyć z modelowania?
- Czy pola `vin` i `first_registration` (100% braków) oraz `district` (73% braków) są użyteczne?
- Czy docelowy próg MAPE ok. 15% jest realny po EDA?

## Wymagania

| ID | Wymaganie | Kryterium sprawdzenia | Źródło lub uzasadnienie | Status | Osoba |
|---|---|---|---|---|---|
| R1 | Użytkownik szybko otrzymuje orientacyjną cenę rynkową po podaniu parametrów pojazdu. | Dla poprawnych danych z formularza aplikacja zwraca prognozę ceny w PLN w kilka sekund. | Karta projektu, pkt 4 i 7. | potwierdzone | Bartłomiej Taper |
| R2 | Prognoza jest przedstawiona z przedziałem niepewności, a nie jako jedna liczba. | Każda prognoza zawiera dolną i górną granicę przedziału widoczną w interfejsie. | Karta projektu, pkt 4; ryzyko cen ofertowych i migawki. | potwierdzone | Kacper Stopa |
| R3 | Użytkownik widzi, czy podana cena ofertowa jest poniżej, w okolicach czy powyżej prognozy. | Aplikacja porównuje cenę ofertową z prognozą i wyświetla jedną z trzech etykiet. | Karta projektu, pkt 4. | potwierdzone | Bartłomiej Taper |
| R4 | Użytkownik poznaje cechy najsilniej wpływające na cenę. | Raport i aplikacja pokazują ranking ważności cech oraz wykres dla co najmniej trzech porównanych metod. | Karta projektu, pkt 4, 6 i 7. | potwierdzone | Kacper Stopa |
| R5 | Aplikacja czytelnie obsługuje błędne lub niekompletne dane wejściowe. | Formularz pokazuje błąd walidacji, a API zwraca 422 dla niepoprawnych danych i prognozę dla poprawnych. | Karta projektu, pkt 7 i 8. | potwierdzone | Adrian Świeca |
| R6 | Wycena jest wystarczająco dokładna, by wspierać decyzję użytkownika. | Model na zbiorze testowym osiąga lepsze MAE, RMSE i R² niż mediana ceny dla marki i modelu oraz MAPE nie przekracza ok. 15%. | Karta projektu, pkt 7; próg MAPE jest założeniem. | założenie | Kacper Stopa |

## Potrzeby informacyjne

| Informacja | Do czego | Minimalny zakres | Format/częstotliwość | Czy dostępna (tak/częściowo/nie) |
|---|---|---|---|---|
| Cena ofertowa i podstawowe parametry pojazdu | trenowanie modelu i generowanie prognozy | cena w PLN oraz marka, model, rok, przebieg, silnik, paliwo, skrzynia i nadwozie | CSV, jedna migawka | tak; 233 040 rekordów i 103 kolumny w `data/full-2026-11-01.csv` |
| Wyposażenie pojazdu | analiza ważności cech i poprawa prognozy | flagi `has_*`/`is_*`, m.in. klimatyzacja, tempomat, kamera i nawigacja | CSV, jedna migawka | częściowo; dane są deklaracjami sprzedawcy, np. `has_cruise` ma 34,98% braków, a `has_alloy_wheels` 41,72% |
| Lokalizacja oferty | uwzględnienie różnic rynku lokalnego | `city` i `region` | CSV, jedna migawka | tak; `district` ma 73,23% braków, więc nie jest wymagany |
| Ceny transakcyjne | sprawdzenie, czy prognoza odpowiada rzeczywistym cenom | finalne ceny sprzedaży dla próby ogłoszeń | brak | nie; dostępne są wyłącznie ceny ofertowe |
| Historia cen w czasie | ocena aktualności wyceny i zmian cen | co najmniej dwie migawki w odstępie czasu | cykliczny eksport | nie; dostępna jest jedna migawka z 2026-11-01 |
| Warunki wykorzystania danych Otomoto | ocena zgodności publikacji prototypu z regulaminem | regulamin serwisu i zasady publikacji danych | dokumentacja, jednorazowo | częściowo; `robots.txt` i regulamin sprawdzono wstępnie, publikacja nie jest potwierdzona |
