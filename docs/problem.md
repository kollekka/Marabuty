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

- szybka orientacyjna wycena ceny w PLN na podstawie parametrów pojazdu,
- przedział niepewności przy każdej prognozie,
- ocena oferty względem prognozy: poniżej, w okolicach lub powyżej,
- ranking cech najsilniej wpływających na cenę,
- czytelna obsługa błędnych lub niekompletnych danych wejściowych,
- jakość modelu lepsza niż prosty punkt odniesienia.
