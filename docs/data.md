# Ocena danych i źródła

## Opis wybranego źródła

| Element | Wynik sprawdzenia |
|---|---|
| Źródło i właściciel | Publiczne ogłoszenia serwisu Otomoto.pl (Grupa OLX). Dane pozyskane własnym eksportem opartym na skrypcie `MrKabas/Otomoto-Scraper` (MIT) autorstwa Kacpra Stopy z zespołu Marabuty. Właścicielem ofert i danych jest Otomoto/OLX, nie zespół; licencja MIT dotyczy kodu skryptu, a nie danych. |
| Link | Portal: https://www.otomoto.pl/ ; scraper: https://github.com/MrKabas/Otomoto-Scraper ; plik w repozytorium: `data/full-2026-11-01.csv` |
| Wymaganie dostępu | Publiczny dostęp do ogłoszeń przez GraphQL, bez klucza API. Wymagane uruchomienie scrapera (Node.js ≥ 20, npm) i eksport z SQLite do CSV/Parquet/JSON. |
| Data pobrania | Eksport oznaczony w nazwie pliku jako 2026-11-01. `first_seen` = 2026-11-01T22:49:37.293Z dla wszystkich rekordów; `created_at` od 2026-09-03T05:24:24Z do 2026-11-02T15:33:24Z. |
| Format | CSV, UTF-8 z BOM, separator przecinek, 103 kolumny, 233 040 rekordów (233 041 wierszy z nagłówkiem), rozmiar ok. 154 MB. |
| Liczba rekordów | 233 040 rekordów; 233 040 unikalnych `id` i 233 040 unikalnych `url`; 0 pełnych duplikatów wierszy. |
| Pola | Identyfikacja i metadane: `id`, `url`, `title`, `created_at`, `updated_at`, `first_seen`, `last_seen`, `status`, `state`, `attempts`, `last_error`, `enriched_at`. Pojazd: `make`, `model`, `generation`, `year`, `mileage_km`, `price_pln`, `currency`, `fuel_type`, `gearbox`, `transmission`, `engine_cc`, `engine_power_km`, `body_type`, `door_count`, `seats`, `color`, `color_type`, `country_origin`, `new_used`, `damaged`, `registered_pl`, `first_owner`, `no_accident`, `service_aso`, `imported`, `vin`, `first_registration`. Sprzedawca i lokalizacja: `seller_type`, `seller_id`, `seller_name`, `city`, `region`, `district`. Wyposażenie: m.in. `has_ac`, `ac_type`, `has_cruise`, `has_camera`, `has_navi`, `has_leather`, `has_alloy_wheels`, `has_4wd`, `drive_type`, `airbags_count`, `headlights_type` oraz pozostałe pola `has_*`/`is_*`. Pełna lista znajduje się w nagłówku pliku; słownik do uzupełnienia w kolejnym kroku. |
| Daty i jednostki | `created_at` i `updated_at`: ISO 8601 UTC `YYYY-MM-DDTHH:MM:SSZ`; `first_seen`, `last_seen`, `enriched_at`: ISO 8601 UTC z milisekundami. `price_pln`: PLN (232 829 rekordów) lub EUR (211 rekordów); `mileage_km`: km; `engine_cc`: cm³; `engine_power_km`: KM; `year`: rok `YYYY`. |
| Braki danych | `status`, `make`, `model`, `year`, `mileage_km`, `fuel_type`, `body_type`, `new_used`: 4 014 rekordów (1,72%); `gearbox`: 4 057 (1,74%); `price_pln`: 180 (0,08%); `transmission` i `drive_type`: 33 593 (14,42%); `seats`: 23 457 (10,07%); `generation`: 70 158 (30,11%); `country_origin`: 85 023 (36,48%); `district`: 170 665 (73,23%); `vin` i `first_registration`: 233 040 (100%). Szczegóły poniżej. |
| Limit | Brak znanego twardego limitu w samym pliku. Scraping podlega `robots.txt` i regulaminowi Otomoto. W `robots.txt` obowiązuje `Allow: /` poza listą wyłączonych ścieżek (m.in. `/api/`, `/ajax/`, `/account/`); nagłówek `Content-Signal` ustawia `ai-train=yes, search=yes, ai-input=yes`. Dokładne limity zapytań i mechanizmy antyscrapingowe: do sprawdzenia. |
| Klucz | `id` — unikalny identyfikator ogłoszenia; alternatywnie unikalny `url`. |
| Koszt | Brak opłaty za dane. Koszt własny: czas pobierania, utrzymanie scrapera i ryzyko zmian HTML/antyscrapingowych. |
| Licencja | Kod `MrKabas/Otomoto-Scraper`: MIT (autor: Kacper Stopa). Dane Otomoto nie są objęte MIT; warunki wykorzystania i publikacji wynikają z regulaminu serwisu — do sprawdzenia przed publikacją. Zakładamy użycie dydaktyczne, bez publikowania danych osobowych sprzedawców. |
| Próba ponownego pobrania | Nie wykonano w ramach tego etapu. `data/full-2026-11-01.csv` jest pojedynczym eksportem. Kolejne pobranie wymaga uruchomienia scrapera z wybranym zakresem dat i porównania liczebności, zakresu dat oraz kluczy z obecnym plikiem. |
| Brakujące dane | Całkowicie puste: `vin`, `first_registration`. Bardzo wysokie braki: `district` (73,23%), `color_type` (47,13%), `first_owner` (44,59%), `service_aso` (42,81%), `has_alloy_wheels` (41,72%), `registered_pl` (37,53%), `country_origin` (36,48%), `has_cruise` (34,98%), `no_accident` (32,55%), `generation` (30,11%). Decyzja o odrzuceniu lub imputacji po EDA. |
| Plan awaryjny | Ponowne uruchomienie scrapera z mniejszym zakresem dat lub `--max-pages`; alternatywnie publiczny zbiór Kaggle „Poland cars for sale dataset” (starsza migawka, 208 304 rekordy) wyłącznie do porównania i testowania pipeline'u, nie do zastąpienia aktualnego źródła. |

## Zakres i jakość danych

Profilowanie wykonano na całym pliku `data/full-2026-11-01.csv` (233 040 rekordów) skryptem w Pythonie z modułem `csv`, z kodowaniem `utf-8-sig`. Sprawdzono nazwy i liczbę pól, typy wartości, formaty dat, jednostki, braki, duplikaty oraz podejrzane wartości. Dane nie były poprawiane na tym etapie.

### Podstawowe statystyki

| Pole | Zakres / statystyka |
|---|---|
| `price_pln` | min 400, mediana 56 500, max 4 522 000; 18 wartości poniżej 1 000; brak wartości ≤ 0; 0 wartości powyżej 5 000 000 |
| `year` | min 1914, mediana 2018, max 2027; 25 409 rekordów z rokiem ≥ 2026 |
| `mileage_km` | min 0, mediana 130 000, max 2 610 075; 27 rekordów z przebiegiem 0; 7 wartości powyżej 2 000 000 |
| `engine_cc` | min 56, mediana 1 798, max 9 000 |
| `engine_power_km` | min 1, mediana 150, max 9 700 |
| `make` / `model` | 150 marek i 1 520 modeli; najczęstsze marki: BMW (18 945), Volkswagen (18 382), Audi (17 517), Mercedes-Benz (16 539), Ford (16 253) |
| `currency` | PLN 232 829, EUR 211 |
| `new_used` | Używane 204 256, Nowość 24 770, brak 4 014 |
| `status` | active 229 026, brak 4 014 |

### Braki w najważniejszych polach

| Pole | Liczba braków | Udział |
|---|---:|---:|
| `price_pln` | 180 | 0,08% |
| `make`, `model`, `year`, `mileage_km`, `fuel_type`, `body_type`, `new_used` | 4 014 | 1,72% |
| `gearbox` | 4 057 | 1,74% |
| `engine_cc` | 7 366 | 3,16% |
| `door_count` | 4 800 | 2,06% |
| `seats` | 23 457 | 10,07% |
| `transmission`, `drive_type` | 33 593 | 14,42% |
| `generation` | 70 158 | 30,11% |
| `country_origin` | 85 023 | 36,48% |
| `district` | 170 665 | 73,23% |
| `vin`, `first_registration` | 233 040 | 100,00% |

Rekordy z brakami `make`/`model`/`year` (4 014) mają jednak wypełnione `price_pln`, więc nie są to puste wiersze. Prawdopodobnie są to ogłoszenia, dla których nie udało się pobrać lub zmapować podstawowych parametrów; wymagają decyzji po EDA.

### Duplikaty i wartości podejrzane

- Pełne duplikaty wierszy: 0.
- Duplikaty `id`: 0; duplikaty `url`: 0.
- `price_pln` bez wartości liczbowych: 0; wartości poniżej 1 000: 18 (np. 400, 499, 500, 700, 900, 950, 990, 999) — do weryfikacji, czy nie są to ogłoszenia części lub błędy.
- `mileage_km` bez wartości liczbowych: 0; wartości powyżej 2 000 000: 7 (maks. 2 610 075) — do weryfikacji.
- `year` bez wartości liczbowych: 0; wartości poza zakresem 1900–2027: 0.
- 211 ogłoszeń ma cenę w EUR; przed modelowaniem trzeba je przeliczyć lub wyłączyć.

## Próbka

`data/sample.csv` zawiera 25 losowych rekordów z pełnego eksportu (ziarno 42), ze wszystkimi 103 kolumnami, zapisanych w UTF-8 z BOM. Jest to próbka techniczna, a nie próba reprezentatywna; nie należy na jej podstawie uogólniać rozkładów w całym zbiorze ani szacować pokrycia rynku.

## Plan pozyskania danych

| Element | Ustalenie zespołu |
|---|---|
| Źródło | Publiczne ogłoszenia Otomoto.pl |
| Właściciel danych | Otomoto/OLX |
| Narzędzie | Własny eksport oparty na `MrKabas/Otomoto-Scraper` (MIT, autor: Kacper Stopa); dane w SQLite, eksport do CSV/Parquet/JSON |
| Zakres | Ogłoszenia sprzedaży używanych samochodów osobowych w Polsce wraz z ceną ofertową i parametrami pojazdu |
| Okres i częstotliwość | Pojedyncza migawka: `first_seen` 2026-11-01, `created_at` 2026-09-03–2026-11-02. Kolejne eksporty możliwe po ustaleniu harmonogramu. |
| Jednostka obserwacji | Jeden wiersz = jedno ogłoszenie samochodu |
| Dobór i liczebność | Pełny eksport obejmuje 233 040 ogłoszeń; sposób doboru zależy od zakresu dat, filtrów scrapera i paginacji. `data/sample.csv` to 25 losowych rekordów do prac technicznych. |
| Sposób pobrania | Uruchomienie scrapera na publicznym endpointcie GraphQL Otomoto.pl i eksport z SQLite do CSV |
| Data pobrania | 2026-11-01/02 |
| Limity, koszt i uprawnienia | Brak opłaty; scraping zgodnie z `robots.txt` i regulaminem serwisu, z opóźnieniami między żądaniami. Dokładne limity i zasady publikacji: do sprawdzenia. |
| Licencja i zasady publikacji | Kod scrapera MIT; dane podlegają regulaminowi Otomoto. Dane wykorzystujemy dydaktycznie, nie publikujemy danych osobowych sprzedawców ani pełnych ogłoszeń. |
| Osoba odpowiedzialna | Adrian Świeca (dane/backend) |
| Plan awaryjny | Ponowne pobranie mniejszego zakresu; alternatywnie zbiór Kaggle „Poland cars for sale dataset” do porównania |

## Ograniczenia i legalność

- Dostępne są ceny ofertowe, a nie transakcyjne; nie można na tej podstawie wyznaczyć rzeczywistej ceny transakcyjnej.
- Dane są migawką z jednego okresu; nie pozwalają prognozować zmian cen w czasie.
- Plik zawiera `seller_name`, `seller_id` i `url`; nie wykorzystujemy ich jako predyktorów i nie publikujemy w aplikacji.
- Scraping podlega regulaminowi Otomoto i wymaga respektowania `robots.txt`, opóźnień oraz ewentualnych limitów. Struktura strony i zabezpieczenia antyscrapingowe mogą się zmienić, więc skrypt trzeba utrzymywać.
- Możliwe są braki, duplikaty, wartości odstające i błędy wpisywania (np. przebieg lub cena); część z nich wymaga decyzji po EDA.
- Licencji kodu (MIT) nie utożsamiamy z licencją danych. Przed publikacją prototypu należy potwierdzić warunki wykorzystania danych w regulaminie Otomoto.
