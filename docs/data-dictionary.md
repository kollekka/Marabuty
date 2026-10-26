# Słownik danych

Szkic opracowany na podstawie `data/raw/sample.csv`, `data/processed/sample-clean.csv`, `scripts/prepare_data.py` oraz `docs/data.md`.

Próbka obejmuje 25 rekordów. Liczba w nawiasie oznacza liczbę pustych wartości w tej próbce; wpis `nie (0/25)` nie gwarantuje braku braków w całym zbiorze 208 304 rekordów. Znaczenia oznaczone jako „(potwierdzić w dokumentacji źródła)” wymagają weryfikacji.

## `data/raw/sample.csv`

| Pole | Znaczenie | Typ | Jednostka/format | Przykładowa wartość | Czy może być puste? |
|---|---|---|---|---|---|
| `Index` | Techniczny identyfikator wiersza; unikalność i rola klucza do potwierdzenia. | liczba całkowita | identyfikator | `0` | nie (0/25) |
| `Price` | Cena ofertowa pojazdu. | liczba | PLN | `86200` | nie (0/25) |
| `Currency` | Waluta ceny ofertowej. | tekst | kod waluty; obserwowane `PLN` | `PLN` | nie (0/25) |
| `Condition` | Stan pojazdu. | tekst/kategoria | obserwowane `New`, `Used` | `New` | nie (0/25) |
| `Vehicle_brand` | Marka pojazdu. | tekst | — | `Abarth` | nie (0/25) |
| `Vehicle_model` | Model pojazdu. | tekst | — | `595` | nie (0/25) |
| `Vehicle_version` | Wersja/wariant pojazdu (potwierdzić w dokumentacji źródła). | tekst | — | `1.4 MultiAir` | tak (24/25) |
| `Vehicle_generation` | Generacja modelu (potwierdzić w dokumentacji źródła). | tekst | — | — (brak w próbce) | tak (25/25) |
| `Production_year` | Rok produkcji. | liczba całkowita | rok `YYYY` | `2021` | nie (0/25) |
| `Mileage_km` | Przebieg pojazdu. | liczba | km | `1.0` | nie (0/25) |
| `Power_HP` | Moc silnika. | liczba | HP | `145.0` | nie (0/25) |
| `Displacement_cm3` | Pojemność skokowa silnika. | liczba | cm³ | `1400.0` | nie (0/25) |
| `Fuel_type` | Rodzaj paliwa. | tekst/kategoria | obserwowane `Gasoline` | `Gasoline` | nie (0/25) |
| `CO2_emissions` | Emisja CO2; jednostka i norma pomiaru (potwierdzić w dokumentacji źródła). | liczba | jednostka do potwierdzenia | `139.0` | tak (20/25) |
| `Drive` | Rodzaj napędu. | tekst/kategoria | obserwowane `Front wheels`, `Rear wheels` | `Front wheels` | tak (3/25) |
| `Transmission` | Rodzaj skrzyni biegów. | tekst/kategoria | obserwowane `Manual`, `Automatic` | `Manual` | nie (0/25) |
| `Type` | Typ nadwozia. | tekst/kategoria | obserwowane `small_cars`, `coupe`, `city_cars`, `convertible` | `small_cars` | nie (0/25) |
| `Doors_number` | Liczba drzwi. | liczba | liczba drzwi | `3.0` | nie (0/25) |
| `Colour` | Kolor pojazdu. | tekst/kategoria | obserwowane `gray`, `silver`, `blue` itd. | `gray` | nie (0/25) |
| `Origin_country` | Kraj pochodzenia pojazdu (potwierdzić w dokumentacji źródła). | tekst/kategoria | obserwowane `Germany`, `Poland`, `France` | `Germany` | tak (13/25) |
| `First_owner` | Informacja o pierwszym właścicielu; kodowanie wartości (potwierdzić w dokumentacji źródła). | tekst/kategoria | obserwowane `Yes` | `Yes` | tak (18/25) |
| `First_registration_date` | Data pierwszej rejestracji. | data (tekst) | `DD/MM/YYYY` | `15/03/2016` | tak (17/25) |
| `Offer_publication_date` | Data publikacji ogłoszenia. | data (tekst) | `DD/MM/YYYY` | `04/05/2021` | nie (0/25) |
| `Offer_location` | Lokalizacja ogłoszenia/oferty. | tekst | adres lub lokalizacja nieustrukturyzowana | `ul. Jubilerska 6 - 04-190 Warszawa, Mazowieckie (Polska)` | nie (0/25) |
| `Features` | Lista wyposażenia pojazdu; pełny słownik i format (potwierdzić w dokumentacji źródła). | tekst (serializowana lista) | lista w nawiasach kwadratowych | `['ABS', 'Electric front windows']` | nie (0/25); pusta lista `[]` to wartość |

## `data/processed/sample-clean.csv`

| Pole | Znaczenie | Typ | Jednostka/format | Przykładowa wartość | Czy może być puste? |
|---|---|---|---|---|---|
| `Index` | Techniczny identyfikator wiersza. | liczba całkowita | identyfikator | `0` | nie (0/25) |
| `Price` | Cena ofertowa pojazdu. | liczba zmiennoprzecinkowa | PLN; zapis np. `86200.0` | `86200.0` | tak (0/25 po czyszczeniu; reguła `Price <= 0`) |
| `Currency` | Waluta ceny ofertowej. | tekst | `PLN` | `PLN` | nie (0/25) |
| `Condition` | Stan pojazdu. | tekst/kategoria | `New`, `Used` | `New` | nie (0/25) |
| `Vehicle_brand` | Marka pojazdu. | tekst | — | `Abarth` | nie (0/25) |
| `Vehicle_model` | Model pojazdu. | tekst | — | `595` | nie (0/25) |
| `Vehicle_version` | Wersja/wariant pojazdu (potwierdzić w dokumentacji źródła). | tekst | — | `1.4 MultiAir` | tak (24/25) |
| `Vehicle_generation` | Generacja modelu (potwierdzić w dokumentacji źródła). | tekst | — | — (brak w próbce) | tak (25/25) |
| `Production_year` | Rok produkcji. | liczba całkowita | rok `YYYY` | `2021` | tak (0/25; reguła zakresu 1900–rok odniesienia + 1) |
| `Mileage_km` | Przebieg pojazdu. | liczba zmiennoprzecinkowa | km | `1.0` | tak (0/25; reguła `< 0`) |
| `Power_HP` | Moc silnika. | liczba zmiennoprzecinkowa | HP | `145.0` | tak (0/25; reguła `<= 0`) |
| `Displacement_cm3` | Pojemność skokowa silnika. | liczba zmiennoprzecinkowa | cm³ | `1400.0` | tak (0/25; reguła `<= 0`) |
| `Fuel_type` | Rodzaj paliwa. | tekst/kategoria | `Gasoline` | `Gasoline` | nie (0/25) |
| `CO2_emissions` | Emisja CO2; jednostka i norma pomiaru (potwierdzić w dokumentacji źródła). | liczba zmiennoprzecinkowa | jednostka do potwierdzenia | `139.0` | tak (20/25; reguła `< 0`) |
| `Drive` | Rodzaj napędu. | tekst/kategoria | `Front wheels`, `Rear wheels` | `Front wheels` | tak (3/25) |
| `Transmission` | Rodzaj skrzyni biegów. | tekst/kategoria | `Manual`, `Automatic` | `Manual` | nie (0/25) |
| `Type` | Typ nadwozia. | tekst/kategoria | `small_cars`, `coupe` itd. | `small_cars` | nie (0/25) |
| `Doors_number` | Liczba drzwi. | liczba całkowita | liczba drzwi | `3` | tak (0/25; reguła `<= 0`) |
| `Colour` | Kolor pojazdu. | tekst/kategoria | `gray`, `silver` itd. | `gray` | nie (0/25) |
| `Origin_country` | Kraj pochodzenia pojazdu (potwierdzić w dokumentacji źródła). | tekst/kategoria | `Germany`, `Poland`, `France` | `Germany` | tak (13/25) |
| `First_owner` | Informacja o pierwszym właścicielu; kodowanie wartości (potwierdzić w dokumentacji źródła). | tekst/kategoria | `Yes` | `Yes` | tak (18/25) |
| `First_registration_date` | Data pierwszej rejestracji. | data (ISO) | `YYYY-MM-DD` | `2016-03-15` | tak (17/25) |
| `Offer_publication_date` | Data publikacji ogłoszenia. | data (ISO) | `YYYY-MM-DD` | `2021-05-04` | nie (0/25) |
| `Offer_location` | Lokalizacja ogłoszenia/oferty. | tekst | adres lub lokalizacja nieustrukturyzowana | `ul. Jubilerska 6 - 04-190 Warszawa, Mazowieckie (Polska)` | nie (0/25) |
| `Features` | Lista wyposażenia pojazdu; pełny słownik i format (potwierdzić w dokumentacji źródła). | tekst (serializowana lista) | lista w nawiasach kwadratowych | `['ABS', 'Electric front windows']` | nie (0/25); pusta lista `[]` to wartość |
| `Displacement_l` | Pojemność skokowa w litrach. | liczba zmiennoprzecinkowa | l | `1.4` | tak (0/25; gdy brak `Displacement_cm3`) |
| `Vehicle_age` | Wiek pojazdu w roku publikacji oferty. | liczba całkowita | lata | `0` | tak (0/25; gdy brak roku lub daty publikacji) |

## Różnice między plikami

| Element | `sample.csv` | `sample-clean.csv` |
|---|---|---|
| Liczba wierszy | 25 | 25 |
| Liczba kolumn | 25 | 27 |
| Duplikaty bez `Index` | 0 | 0 |
| Nowe pola | — | `Displacement_l`, `Vehicle_age` |
| Usunięte pola | — | — |
| Daty | `DD/MM/YYYY` | `YYYY-MM-DD` |
| `Doors_number` | `3.0` | `3` |
| `Price` i inne liczby | np. `86200` | np. `86200.0` |
| Białe znaki w polach tekstowych | bez normalizacji | przycięte na końcach |
| Wartości niemożliwe | bez reguł | zamienione na puste |
| Braki w próbce | 7 kolumn z brakami | te same 7 kolumn, bez zmian liczby braków |

Kolumny z brakami w próbce: `Vehicle_version`, `Vehicle_generation`, `CO2_emissions`, `Drive`, `Origin_country`, `First_owner`, `First_registration_date`.

Reguły czyszczenia: `Price <= 0`, `Mileage_km < 0`, `Power_HP <= 0`, `Displacement_cm3 <= 0`, `Doors_number <= 0`, `CO2_emissions < 0` oraz `Production_year < 1900` lub `> rok_odniesienia + 1` stają się brakami. Błędne daty stają się brakami. Wiersze nie są usuwane poza duplikatami.

## Nowe pola i wzory

Nowe pola w pliku wynikowym: `Displacement_l`, `Vehicle_age`.

| Pole | Wzór | Uwagi |
|---|---|---|
| `Displacement_l` | `round(Displacement_cm3 / 1000, 3)` | `1400.0` → `1.4`; `1368.0` → `1.368`; puste, gdy źródło puste. |
| `Vehicle_age` | `year(Offer_publication_date) - Production_year` | Puste, gdy brak daty publikacji w wierszu. Gdy w całym zbiorze brak ważnych dat, używane jest `2021 - Production_year`. Wartość nie jest obcinana do zera. |

Rok odniesienia to maksymalny rok z `Offer_publication_date`; w próbce wynosi 2021. Przy braku wszystkich ważnych dat skrypt używa wartości zapasowej 2021.
