# Słownik danych

Dokument opisuje dwa pliki:

- **`data/raw/sample.csv`** — źródłowa próbka eksportu Otomoto: 25 rekordów, 103 kolumny, UTF-8 z BOM, separator przecinek. Kolumny i przykłady w tabelach 1–4 pochodzą z tego pliku.
- **`data/processed/sample-clean.csv`** — wynik `scripts/prepare_data.py`: 25 rekordów, 81 kolumn, 0 braków. Różnice względem źródła opisuje sekcja „Plik wynikowy”.

Pełny eksport `data/full-2026-11-01.csv` ma ten sam schemat co próbka: 233 040 rekordów i 103 kolumny.

## Plik źródłowy: `data/raw/sample.csv`

### 1. Identyfikacja i metadane (13 kolumn)

| Pole | Znaczenie | Typ | Jednostka/format | Przykładowa wartość | Czy może być puste? |
|---|---|---|---|---|---|
| `id` | Identyfikator ogłoszenia nadany przez Otomoto | liczba całkowita | — | `6151256817` | Nie (0/25) |
| `url` | Adres ogłoszenia w serwisie Otomoto | tekst | URL | `https://www.otomoto.pl/osobowe/oferta/mercedes-benz-klasa-s-...` | Nie (0/25) |
| `title` | Tytuł ogłoszenia | tekst | — | `Mercedes-Benz Klasa S` | Nie (0/25) |
| `created_at` | Data utworzenia ogłoszenia | data | ISO 8601, UTC | `2026-11-02T10:06:00Z` | Nie (0/25) |
| `updated_at` | Data ostatniej aktualizacji ogłoszenia | data | ISO 8601, UTC | `2026-11-02T10:06:15Z` | Nie (0/25) |
| `first_seen` | Czas pierwszego zapisu rekordu przez scraper | data | ISO 8601, UTC, z milisekundami | `2026-11-01T22:49:37.293Z` | Nie (0/25) |
| `last_seen` | Czas ostatniego zapisu rekordu przez scraper | data | ISO 8601, UTC, z milisekundami | `2026-11-01T22:49:37.293Z` | Nie (0/25) |
| `status` | Status ogłoszenia w bazie scrapera | tekst | `active` lub `gone` | `active` | Nie (0/25) |
| `currency` | Waluta ceny ofertowej | tekst | kod ISO 4217 | `PLN` | Nie (0/25) |
| `state` | Stan przetwarzania rekordu przez scraper | tekst | `enriched` lub `gone` | `enriched` | Nie (0/25) |
| `attempts` | Liczba prób pobrania szczegółów ogłoszenia | liczba całkowita | — | `0` | Nie (0/25) |
| `last_error` | Ostatni błąd zapisany przy pobieraniu szczegółów | tekst | — | — | Tak (25/25, wszystkie puste) |
| `enriched_at` | Data uzupełnienia szczegółów ogłoszenia | data | ISO 8601, UTC, z milisekundami | `2026-11-02T12:41:03.387Z` | Nie (0/25) |

### 2. Sprzedawca i lokalizacja (6 kolumn)

| Pole | Znaczenie | Typ | Jednostka/format | Przykładowa wartość | Czy może być puste? |
|---|---|---|---|---|---|
| `seller_type` | Typ sprzedawcy | tekst | `prywatny` lub `firma` | `firma` | Nie (0/25) |
| `seller_id` | Identyfikator sprzedawcy w Otomoto | liczba całkowita | — | `10418928` | Nie (0/25) |
| `seller_name` | Nazwa sprzedawcy | tekst | — | `UŻYWANE GARCAREK` | Nie (0/25) |
| `city` | Miejscowość, w której stoi pojazd | tekst | — | `Ociąż` | Nie (0/25) |
| `region` | Województwo | tekst | — | `Wielkopolskie` | Nie (0/25) |
| `district` | Dzielnica lub powiat | tekst | — | `Włochy` | Tak (18/25) |

### 3. Parametry pojazdu (27 kolumn)

| Pole | Znaczenie | Typ | Jednostka/format | Przykładowa wartość | Czy może być puste? |
|---|---|---|---|---|---|
| `make` | Marka pojazdu | tekst | — | `Mercedes-Benz` | Nie (0/25) |
| `model` | Model pojazdu | tekst | — | `Klasa S` | Nie (0/25) |
| `generation` | Generacja modelu wraz z latami produkcji | tekst | — | `W223 (2020-)` | Tak (6/25) |
| `year` | Rok produkcji | liczba całkowita | rok | `2023` | Nie (0/25) |
| `mileage_km` | Przebieg | liczba całkowita | km | `93525` | Nie (0/25) |
| `price_pln` | Cena ofertowa | liczba całkowita | PLN | `830900` | Nie (0/25) |
| `fuel_type` | Rodzaj paliwa | tekst | — | `Hybryda` | Nie (0/25) |
| `gearbox` | Rodzaj skrzyni biegów | tekst | `Manualna` lub `Automatyczna` | `Automatyczna` | Nie (0/25) |
| `transmission` | Napęd | tekst | — | `4x4 (dołączany automatycznie)` | Tak (4/25) |
| `engine_cc` | Pojemność silnika | liczba całkowita | cm³ | `3982` | Nie (0/25) |
| `engine_power_km` | Moc silnika | liczba całkowita | KM | `612` | Nie (0/25) |
| `body_type` | Typ nadwozia | tekst | — | `Sedan` | Nie (0/25) |
| `door_count` | Liczba drzwi | liczba całkowita | — | `4` | Nie (0/25) |
| `seats` | Liczba miejsc | liczba całkowita | — | `5` | Tak (1/25) |
| `color` | Kolor nadwozia | tekst | — | `Czarny` | Nie (0/25) |
| `color_type` | Rodzaj lakieru | tekst | `Metalik`, `Perłowy` lub `Matowy` | `Metalik` | Tak (10/25) |
| `country_origin` | Kraj pochodzenia pojazdu | tekst | — | `Polska` | Tak (8/25) |
| `new_used` | Stan pojazdu | tekst | `Nowość` lub `Używane` | `Używane` | Nie (0/25) |
| `damaged` | Informacja o uszkodzeniu z ogłoszenia | flaga 0/1 | 0/1 | `0` | Tak (5/25) |
| `registered_pl` | Informacja o rejestracji w Polsce | flaga 0/1 | 0/1 | `1` | Tak (11/25) |
| `first_owner` | Informacja o pierwszym właścicielu | flaga 0/1 | 0/1 | `1` | Tak (13/25) |
| `no_accident` | Informacja o braku wypadków | flaga 0/1 | 0/1 | `1` | Tak (7/25) |
| `service_aso` | Informacja o serwisowaniu w ASO | flaga 0/1 | 0/1 | `1` | Tak (9/25) |
| `imported` | Informacja o sprowadzeniu z zagranicy | flaga 0/1 | 0/1 | `0` | Tak (3/25) |
| `vin` | Numer VIN | tekst | — | — | Tak (25/25, wszystkie puste) |
| `first_registration` | Data pierwszej rejestracji | data | `RRRR-MM-DD` | — | Tak (25/25, wszystkie puste) |
| `photo_count` | Liczba zdjęć w ogłoszeniu | liczba całkowita | — | `20` | Nie (0/25) |

### 4. Wyposażenie (57 kolumn)

| Pole | Znaczenie | Typ | Jednostka/format | Przykładowa wartość | Czy może być puste? |
|---|---|---|---|---|---|
| `has_ac` | Klimatyzacja | flaga 0/1 | 0/1 | `1` | Tak (3/25) |
| `ac_type` | Rodzaj klimatyzacji | tekst | — | `Klimatyzacja automatyczna` | Tak (3/25) |
| `has_rain_sensor` | Czujnik deszczu | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_cruise` | Tempomat | flaga 0/1 | 0/1 | `1` | Tak (10/25) |
| `cruise_type` | Rodzaj tempomatu | tekst | — | `Tempomat` | Tak (10/25) |
| `has_adaptive_cruise` | Tempomat adaptacyjny (ACC) | flaga 0/1 | 0/1 | `0` | Tak (10/25) |
| `has_front_sensors` | Czujniki parkowania z przodu | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_rear_sensors` | Czujniki parkowania z tyłu | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_camera` | Kamera cofania | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `has_navi` | Nawigacja | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_bluetooth` | Bluetooth | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_usb` | Złącze USB | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_touchscreen` | Ekran dotykowy | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_wireless_charging` | Ładowanie bezprzewodowe | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `has_sound_system` | System audio | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_leather` | Tapicerka skórzana | flaga 0/1 | 0/1 | `0` | Tak (5/25) |
| `has_heated_seats` | Podgrzewane fotele | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_heated_steering` | Podgrzewana kierownica | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `has_sport_seats` | Fotele sportowe | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `has_multifunction_sw` | Kierownica wielofunkcyjna | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_alloy_wheels` | Felgi aluminiowe | flaga 0/1 | 0/1 | `1` | Tak (6/25) |
| `alloy_wheels_type` | Rozmiar felg aluminiowych | tekst | — | `Felgi aluminiowe 20` | Tak (6/25) |
| `has_towbar` | Hak holowniczy | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `has_sunroof` | Dach otwierany | flaga 0/1 | 0/1 | `1` | Tak (21/25) |
| `has_tinted_windows` | Przyciemniane szyby | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_heated_windshield` | Podgrzewana szyba przednia | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `has_blind_spot` | Asystent martwego pola | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `has_lane_assist` | Asystent pasa ruchu | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `has_sign_recognition` | Rozpoznawanie znaków drogowych | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `has_distance_control` | Aktywny tempomat z kontrolą odległości | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `has_adaptive_lights` | Reflektory adaptacyjne | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `headlights_type` | Rodzaj reflektorów | tekst | — | `Lampy przednie w technologii LED` | Tak (15/25) |
| `has_led_lights` | Reflektory LED | flaga 0/1 | 0/1 | `1` | Tak (15/25) |
| `has_led_daytime` | Światła do jazdy dziennej LED | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `has_fog_lights` | Światła przeciwmgielne | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `has_cornering_lights` | Światła doświetlające zakręty | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `has_esp` | ESP | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_abs` | ABS | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_isofix` | Mocowanie ISOFIX | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `airbags_count` | Liczba poduszek powietrznych | liczba całkowita | — | `6` | Nie (0/25) |
| `has_start_stop` | System start-stop | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_tire_pressure` | Kontrola ciśnienia w oponach | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `has_electric_brake` | Hamulec elektryczny | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_hill_hold` | Asystent ruszania na wzniesieniu | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `has_4wd` | Napęd na cztery koła | flaga 0/1 | 0/1 | `1` | Tak (4/25) |
| `drive_type` | Rodzaj napędu | tekst | — | `4x4 (dołączany automatycznie)` | Tak (4/25) |
| `has_keyless` | System bezkluczykowy | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_electric_mirrors` | Elektryczne lusterka | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_folding_mirrors` | Składane lusterka | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_heated_mirrors` | Podgrzewane lusterka | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `has_imported` | Informacja o imporcie | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `has_vin` | Ogłoszenie podaje numer VIN | flaga 0/1 | 0/1 | `1` | Tak (1/25) |
| `has_registration` | Informacja o rejestracji | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `has_service_record` | Informacja o historii serwisowej | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `is_damaged` | Pojazd uszkodzony (wersja uzupełniona zerem) | flaga 0/1 | 0/1 | `0` | Nie (0/25) |
| `is_original_owner` | Pierwszy właściciel (wersja uzupełniona zerem) | flaga 0/1 | 0/1 | `1` | Nie (0/25) |
| `is_no_accident` | Bez wypadków (wersja uzupełniona zerem) | flaga 0/1 | 0/1 | `1` | Nie (0/25) |

## Plik wynikowy: `data/processed/sample-clean.csv`

Plik ma 25 rekordów i 81 kolumn. Zawiera wszystkie kolumny źródłowe poza 22 usuniętymi, z ujednoliconymi typami i bez braków. **Nie zawiera żadnych nowych pól ani wskaźników pochodnych.**

Kolejność kolumn w wyniku:

```text
id, created_at, make, model, generation, year, mileage_km, price_pln, fuel_type,
gearbox, transmission, engine_cc, engine_power_km, body_type, door_count, seats,
color, color_type, country_origin, new_used, damaged, registered_pl, first_owner,
no_accident, service_aso, imported, seller_type, city, region, photo_count,
has_ac, ac_type, has_rain_sensor, has_cruise, cruise_type, has_adaptive_cruise,
has_front_sensors, has_rear_sensors, has_camera, has_navi, has_bluetooth, has_usb,
has_touchscreen, has_wireless_charging, has_sound_system, has_leather,
has_heated_seats, has_heated_steering, has_sport_seats, has_multifunction_sw,
has_alloy_wheels, alloy_wheels_type, has_towbar, has_sunroof, has_tinted_windows,
has_heated_windshield, has_blind_spot, has_lane_assist, has_sign_recognition,
has_distance_control, has_adaptive_lights, headlights_type, has_led_lights,
has_led_daytime, has_fog_lights, has_cornering_lights, has_esp, has_abs,
has_isofix, airbags_count, has_start_stop, has_tire_pressure, has_electric_brake,
has_hill_hold, drive_type, has_keyless, has_electric_mirrors, has_folding_mirrors,
has_heated_mirrors, has_vin, has_registration
```

### Kolumny usunięte w wyniku (22)

| Kolumna | Powód usunięcia |
|---|---|
| `url` | Adres ogłoszenia, unikalny dla każdego wiersza |
| `title` | Tekst ogłoszenia, powtarza markę i model |
| `seller_id` | Identyfikator sprzedawcy, nie opisuje pojazdu |
| `seller_name` | Nazwa sprzedawcy, dane identyfikujące |
| `updated_at` | Data aktualizacji rekordu w bazie scrapera |
| `first_seen` | Znacznik uruchomienia scrapera, stały w całym eksporcie |
| `last_seen` | Znacznik uruchomienia scrapera, stały w całym eksporcie |
| `enriched_at` | Data uzupełnienia szczegółów przez scraper |
| `state` | Stan przetwarzania rekordu przez scraper |
| `attempts` | Liczba prób pobrania szczegółów |
| `status` | Status ogłoszenia w bazie scrapera |
| `currency` | Po filtrze zawiera wyłącznie PLN |
| `vin` | 100% braków; API Otomoto zwraca numer zaszyfrowany |
| `first_registration` | 100% braków; API Otomoto zwraca datę zaszyfrowaną |
| `last_error` | 100% braków |
| `district` | 18/25 braków w próbce, 170 665/233 040 (73,23%) w pełnym eksporcie |
| `has_imported` | Kopia `imported`; po uzupełnieniu braków zerem zgodność 100% |
| `is_damaged` | Kopia `damaged`; po uzupełnieniu braków zerem zgodność 100% |
| `is_original_owner` | Kopia `first_owner`; zgodność 100% po uzupełnieniu zerem |
| `is_no_accident` | Kopia `no_accident`; zgodność 100% po uzupełnieniu zerem |
| `has_service_record` | Kopia `service_aso`; zgodność 100% po uzupełnieniu zerem |
| `has_4wd` | Kopia informacji z `transmission` (napęd 4x4); zgodność 100% |

### Zmiany typów i formatów

| Zakres | W źródle | W wyniku |
|---|---|---|
| `id`, `year`, `mileage_km`, `price_pln`, `engine_cc`, `engine_power_km`, `door_count`, `seats`, `photo_count`, `airbags_count` | liczby wczytywane jako `int64` lub `float64` | `int64` |
| flagi (`damaged`, `registered_pl`, `first_owner`, `no_accident`, `service_aso`, `imported`, wszystkie `has_*`) | `float64` lub `int64`, wartości `0`/`1` i braki | `int64`, wartości wyłącznie `0`/`1` |
| `created_at` | tekst ISO 8601 | tekst ISO 8601 w formacie `RRRR-MM-DDTHH:MM:SSZ`, niepoprawne daty zamieniane na brak |
| kolumny tekstowe | tekst z ewentualnymi spacjami | tekst bez skrajnych spacji, pusty napis zamieniany na brak |
| `mileage_km`, `engine_cc`, `engine_power_km`, `door_count`, `airbags_count` | mogły zawierać tekst lub wartości niemożliwe | liczba całkowita albo brak |

### Uzupełnianie braków

| Metoda | Kolumny | Uzasadnienie |
|---|---|---|
| Mediana | `engine_cc`, `engine_power_km`, `door_count`, `seats`, `photo_count`, `airbags_count` | Mediana jest odporna na wartości odstające i zachowuje rozkład zmiennej |
| Etykieta `Nieznana` | `generation`, `transmission`, `color_type`, `country_origin`, `seller_type`, `ac_type`, `cruise_type`, `alloy_wheels_type`, `headlights_type`, `drive_type` | Brak informacji jest osobną kategorią, a nie zgadywaną wartością |
| Wartość `0` | `damaged`, `registered_pl`, `first_owner`, `no_accident`, `service_aso`, `imported`, wszystkie `has_*` | Zgodne z semantyką źródła: `0` znaczy „nie zadeklarowano w ogłoszeniu” |

Brak nowych pól, więc nie ma wzorów do opisania — skrypt nie liczy żadnych wskaźników pochodnych.

## Operacje czyszczenia

| Operacja | Reguła | Próbka (25 wierszy) | Pełny eksport (233 040 wierszy) |
|---|---|---|---|
| Duplikaty | zostaje pierwszy wiersz dla danego `id` | 0 usuniętych | 0 usuniętych |
| Waluta | usuwane wiersze z `currency` innym niż `PLN` | 0 | 211 |
| Brak ceny | usuwane wiersze bez `price_pln` | 0 | 180 |
| Duże braki | usuwane wiersze z ponad 50% braków w 17 polach rdzeniowych | 0 | 4 012 |
| Cena | usuwane `price_pln < 1000` | 0 | 18 |
| Przebieg | usuwane `mileage_km > 2 000 000` | 0 | 7 |
| Rok produkcji | usuwane `year < 1950` lub `year > rok eksportu + 1` | 0 | 19 |
| Pojemność | usuwane `engine_cc` poza 500–8000 cm³ | 0 | 133 |
| Moc | usuwane `engine_power_km` poza 20–2000 KM | 0 | 142 |
| **Razem** | — | **25 → 25** | **233 040 → 228 318** |

Pola rdzeniowe do progu braków: `make`, `model`, `year`, `mileage_km`, `price_pln`, `fuel_type`, `gearbox`, `transmission`, `engine_cc`, `engine_power_km`, `body_type`, `door_count`, `seats`, `color`, `new_used`, `city`, `region`.

## Uwagi

- **Flagi 0/1.** Wartość `0` oznacza „cecha nie została zadeklarowana w ogłoszeniu”, a nie „pojazd jej nie ma”. Dotyczy to zarówno kolumn `has_*`, jak i `damaged`, `registered_pl`, `first_owner`, `no_accident`, `service_aso`, `imported`.
- **Cena.** `price_pln` to cena ofertowa z ogłoszenia, nie cena transakcyjna.
- **`new_used`.** W danych występują wartości `Nowość` i `Używane`.
- **`vin` i `first_registration`.** W całym eksporcie 233 040 rekordów oba pola są puste, bo API Otomoto zwraca je zaszyfrowane.
- **Ceny w EUR.** 211 ogłoszeń w pełnym eksporcie ma cenę w EUR. Nie ma w danych kursu wymiany, więc te wiersze są odrzucane, a nie przeliczane.
- **`created_at`.** Pozostaje w wyniku, bo pozwala podzielić dane na zbiór treningowy i testowy w czasie.
- **`id`.** Pozostaje w wyniku jako klucz wiersza; nie jest cechą używaną przez model.
