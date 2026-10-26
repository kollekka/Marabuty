# Problem projektu

## Temat

Prognozowanie cen używanych samochodów osobowych na polskim rynku ogłoszeń z wykorzystaniem modelu regresyjnego.

## Opis

Cena samochodu używanego zależy od wielu parametrów, między innymi marki, modelu, rocznika, przebiegu, silnika, paliwa i skrzyni biegów. Ceny ofert podobnych aut mogą się różnić, dlatego kupujący i sprzedający nie zawsze wiedzą, czy konkretna oferta jest bliska cenie rynkowej.

Projekt sprawdzi, jak dokładnie można przewidywać cenę ofertową na podstawie danych o pojeździe oraz które cechy najsilniej wiążą się z ceną. Wynik ma mieć charakter orientacyjny: dostępny zbiór zawiera ceny z ogłoszeń, a nie potwierdzone ceny transakcyjne.

## Odbiorcy

Osoby kupujące lub sprzedające samochód używany w Polsce, a dodatkowo małe komisy i handlarze potrzebujący punktu odniesienia przy wycenie.

## Planowany rezultat

Prototyp ma przyjmować parametry samochodu i zwracać przewidywaną cenę w PLN. W dalszej części projektu zespół planuje porównać modele regresyjne oraz opisać jakość prognoz i ograniczenia danych.

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

- dane na żywo z portali ogłoszeniowych,
- konta użytkowników,
- prognoza zmian cen w czasie,
- ceny transakcyjne.

Miary jakości: MAE, RMSE, MAPE, R². Wstępny cel MAPE ok. 15%, do weryfikacji po EDA.

## Potrzebne dane

- Źródło: „Poland cars for sale dataset”, plik lokalny `data/Car_sale_ads.csv`; CSV, 25 kolumn, 208 304 rekordy (na podstawie `docs/data.md`).
- Zmienna objaśniana: `Price` w PLN.
- Predyktory: m.in. `Vehicle_brand`, `Vehicle_model`, `Production_year`, `Mileage_km`, `Power_HP`, `Displacement_cm3`, `Fuel_type`, `Transmission`, `Type`, `Offer_location`; pełny zestaw po EDA.
- Ograniczenia: braki danych, możliwe duplikaty, wartości odstające i błędy wpisywania; ceny ofertowe, nie transakcyjne; migawka z jednego okresu (w próbce daty IV–V 2021).
- Szczegóły źródła, braków i licencji: `docs/data.md`.

## Założenia i pytania otwarte

Założenia:

- prognoza dotyczy polskiego rynku i samochodów osobowych,
- dane z jednego okresu wystarczą do prototypu,
- cena ofertowa jest akceptowalnym przybliżeniem ceny rynkowej,
- model będzie trenowany na danych po czyszczeniu, z ustalonym ziarnem losowości,
- na start stosujemy losowy podział train/test i walidację krzyżową; decyzja o podziale czasowym po EDA.

Pytania otwarte:

- Jaki jest dokładny adres źródłowy, właściciel, licencja i data pobrania zbioru?
- Jaka jest jednostka `CO2_emissions` i czy kolumna jest użyteczna?
- Czy `Features`, `Vehicle_version` i `Vehicle_generation` mają wystarczające pokrycie, by ich użyć?
- Czy `Condition`, `Currency` i `Origin_country` są wystarczająco spójne do modelowania?
- Czy docelowy próg MAPE ok. 15% jest realny po EDA?
- Jaki zakres i ujednolicenie `Offer_location` jest sensowne?

## Wymagania

Funkcjonalne:

1. Użytkownik podaje parametry pojazdu i otrzymuje prognozę ceny w PLN z przedziałem niepewności.
2. Aplikacja ocenia ofertę względem prognozy (poniżej / w okolicach / powyżej ceny rynkowej).
3. API `POST /predict` zwraca prognozę dla poprawnych danych i błąd 422 dla niepoprawnych.
4. Dostępny jest ranking/wykres ważności cech.
5. Model jest porównany z punktem odniesienia (średnia lub mediana ceny dla marki i modelu) oraz co najmniej trzema metodami.

Niefunkcjonalne:

- powtarzalność: stałe ziarno losowości, jeden skrypt/notebook,
- czas odpowiedzi API: kilka sekund,
- walidacja danych wejściowych w formularzu i API,
- testy `pytest` przechodzą; dokumentacja API w Swagger/OpenAPI,
- README ze sposobem uruchomienia całości.

### Tabela wymagań

| ID | Wymaganie | Kryterium sprawdzenia | Źródło lub uzasadnienie | Status | Osoba                                |
|---|---|---|---|---|--------------------------------------|
| W-01 | Użytkownik otrzymuje orientacyjną cenę pojazdu w PLN wraz z przedziałem niepewności na podstawie podanych parametrów. | Dla poprawnych danych użytkownik widzi prognozę i przedział; wynik jest jasno opisany jako orientacyjny. | Karta, pkt 4 i 6; potrzeba z pkt 2 | potwierdzone | Frontend — Bartłomiej Taper |
| W-02 | Użytkownik widzi, czy oferta jest poniżej, w okolicach, czy powyżej ceny rynkowej. | Interfejs pokazuje jedną z trzech ocen; sposób i progi oceny są jawnie opisane. | Karta, pkt 4 | potwierdzone | Frontend — Bartłomiej Taper |
| W-03 | Prognoza jest wiarygodniejsza niż proste porównanie z medianą lub średnią ceny dla marki i modelu. | MAE, RMSE i R² na zbiorze testowym są lepsze niż dla punktu odniesienia. | Karta, pkt 7.1 | potwierdzone | Model — Kacper Stopa |
| W-04 | Błąd względny prognozy nie przekracza ok. 15%. | MAPE na zbiorze testowym wynosi ≤ 15%; próg zostaje potwierdzony po EDA. | Karta, pkt 7.2 | założenie | Model — Kacper Stopa |
| W-05 | Błędne lub niekompletne dane nie prowadzą do prognozy; użytkownik otrzymuje czytelny komunikat. | Formularz blokuje wysłanie błędnych danych, a API zwraca błąd 422; przypadki błędne są pokryte testami. | Karta, pkt 7.4 | potwierdzone | Dane/backend + Frontend — Adrian Świeca |
| W-06 | Użytkownik rozumie, które cechy najmocniej wpływają na cenę. | Widoczny jest ranking lub wykres ważności cech wraz z opisem metody i ograniczeń. | Karta, pkt 4 i 6 | potwierdzone | Model + Frontend — Adrian Świeca |

## Potrzeby informacyjne

| Informacja | Do czego | Minimalny zakres | Format/częstotliwość | Czy dostępna |
|---|---|---|---|---|
| Cena ofertowa pojazdu (`Price`) | Zmienna objaśniana; punkt odniesienia dla prognozy | Cena w PLN dla każdego ogłoszenia | CSV; jednorazowa migawka | tak |
| Parametry pojazdu: marka, model, rok, przebieg, moc, pojemność, paliwo, skrzynia, nadwozie | Predyktory modelu | Pola wymienione w karcie; pełny zestaw po EDA | CSV; jednorazowo | tak |
| Lokalizacja oferty (`Offer_location`) | Ocena różnic regionalnych | Ujednolicona lokalizacja, np. miasto lub województwo | CSV; jednorazowo | częściowo — format i zakres do ujednolicenia |
| Data publikacji oferty | Ocena aktualności i ewentualny podział czasowy | Data dla większości ogłoszeń oraz zakres dat | CSV; jednorazowo | częściowo — w próbce IV–V 2021, pełny zakres do sprawdzenia |
| Licencja i źródło zbioru | Legalność wykorzystania i opis ograniczeń | Potwierdzona licencja, właściciel, link i data pobrania | Dokumentacja/metadane; jednorazowo | nie |
| Ceny transakcyjne | Weryfikacja, czy cena ofertowa odpowiada rzeczywistej | Cena transakcyjna lub dane porównawcze | Poza zbiorem; brak | nie |
