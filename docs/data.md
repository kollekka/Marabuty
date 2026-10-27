# Ocena danych i źródła

## Opis wybranego źródła

| Element | Wynik sprawdzenia |
|---|---|
| Źródło i właściciel | „Poland cars for sale dataset” - Bartosz Pieniak |
| Link | https://www.kaggle.com/datasets/bartoszpieniak/poland-cars-for-sale-dataset |
| Wymaganie dostępu | Plik CSV jest dostępny lokalnie w `data/Car_sale_ads.csv` |
| Data pobrania | 13.10.2026 |
| Format | CSV, 25 kolumn, przecinek jako separator; polskie znaki są poprawnie odczytywane. |
| Liczba rekordów | 208 304 rekordy danych (208 305 wierszy razem z nagłówkiem). |
| Pola | `Index`, `Price`, `Currency`, `Condition`, `Vehicle_brand`, `Vehicle_model`, `Vehicle_version`, `Vehicle_generation`, `Production_year`, `Mileage_km`, `Power_HP`, `Displacement_cm3`, `Fuel_type`, `CO2_emissions`, `Drive`, `Transmission`, `Type`, `Doors_number`, `Colour`, `Origin_country`, `First_owner`, `First_registration_date`, `Offer_publication_date`, `Offer_location`, `Features`. |
| Daty i jednostki | Daty w próbce mają format `DD/MM/YYYY`; widoczne daty publikacji pochodzą z kwietnia i maja 2021 r. `Price` jest podana w PLN, `Mileage_km` w km, `Power_HP` w HP, a `Displacement_cm3` w cm³. Jednostka `CO2_emissions` do sprawdzenia. |
| Braki danych | W próbce 25 rekordów: `Vehicle_version` 24, `Vehicle_generation` 25, `CO2_emissions` 20, `Drive` 3, `Origin_country` 13, `First_owner` 18, `First_registration_date` 17 pustych wartości; w pozostałych polach próbki nie stwierdzono pustych wartości. Pełne braki dla wszystkich kolumn wymagają profilowania w EDA. |
| Limit | Brak |
| Klucz | `Index` |
| Koszt | Brak |
| Licencja | CC0: Public Domain |
| Brakujące dane | Nieznany jest pełny profil braków w całym zbiorze; w próbce występują braki opisane wyżej. |
| Plan awaryjny | Wybrany wariant alternatywny: skrypt open source `simonloach/car-scraper` (MIT) scrapujący Otomoto.pl do CSV/JSON; szczegóły oraz odrzucone warianty w sekcji „Warianty pozyskania danych”. |

## Próbka

`data/raw/sample.csv` zawiera pierwsze 25 rekordów danych z `data/Car_sale_ads.csv` (indeksy 0–24), wraz z nagłówkiem. Jest to wycinek techniczny, a nie próba losowa ani reprezentatywna; nie należy na jego podstawie uogólniać rozkładów w całym zbiorze. W tych 25 rekordach nie znaleziono powtórzonych kompletnych wierszy.

## Warianty pozyskania danych — decyzja

Decyzja zespołu (dane/backend, uzgodniona z A): jako drugie, niezależne źródło wybieramy **eksport przez skrypt open source `simonloach/car-scraper`** scrapujący Otomoto.pl. Poniżej wybrany wariant oraz dwa odrzucone, z uzasadnieniem opartym na dostępności i ograniczeniach danych. Żaden wariant nie jest uznany za dostępny, dopóki zespół nie wykona faktycznej próby pobrania.

### Wybrany: `simonloach/car-scraper` (GitHub, MIT)

- **Co to jest:** CLI w Pythonie (licencja MIT) scrapujący publiczne oferty Otomoto.pl do CSV/JSON; konfigurowalny przez `targets.json` (dowolny URL wyszukiwania), z opcjonalnym codziennym GitHub Actions i historią cen.
- **Uzasadnienie:** Wariant jest darmowy i nie wymaga klucza API — wystarczy uruchomić go lokalnie (Python 3.10+, Poetry/Docker), więc nie generuje kosztu ani zależności od zewnętrznego dostawcy. Zwraca ceny w PLN oraz podstawowe cechy pojazdu (rok, przebieg, paliwo, skrzynia), czyli pokrywa zmienną objaśnianą i kluczowe predyktory potrzebne w projekcie. Licencja MIT pozwala na użycie dydaktyczne i modyfikację kodu, a publiczne repo daje pełną dokumentację uruchomienia.
- **Ograniczenia:** Scraping podlega regulaminowi Otomoto i wymaga respektowania `robots.txt` oraz opóźnień między żądaniami; możliwe są zmiany HTML/anty-bot, więc skrypt trzeba utrzymywać. Brak gwarancji, że działa „od razu” — wymagana jest próba uruchomienia.
- **Status weryfikacji:** Potwierdzona licencja MIT, obsługiwane pola (w tym `price` w PLN) i wyjście CSV/JSON;

### Odrzucony 1: Apify — „Otomoto.pl Scraper” (automation-lab)

- **Powód:** Płatny model pay-per-event (od ok. 0,60 USD za 1000 ofert) oraz wymagany token i konto Apify; darmowy kredyt wystarcza tylko na test, a przy większym zbiorze koszt rośnie. Dane są dobrej jakości, ale dla projektu dydaktycznego koszt i zależność od zewnętrznej platformy są nieuzasadnione. Dodatkowo obowiązują warunki Apify i Otomoto, więc ryzyko zgodności jest wyższe niż przy własnym skrypcie.

## Plan pozyskania danych

| Element | Ustalenie zespołu |
|---|---|
| Źródło | „Poland cars for sale dataset” |
| Właściciel | Bartosz Pieniak |
| Zakres | Ogłoszenia sprzedaży samochodów z cechami pojazdu i ceną ofertową |
| Okres i częstotliwość | W próbce daty publikacji obejmują 23/04/2021–04/05/2021. |
| Jednostka obserwacji | Pojedynczy wiersz odpowiada ogłoszeniu samochodu. |
| Dobór i liczebność | Plik zawiera 208 304 rekordy. Metoda doboru rekordów w zbiorze źródłowym jest do ustalenia. `data/raw/sample.csv` to pierwsze 25 rekordów, wydzielone wyłącznie jako próbka techniczna, niereprezentatywna. |
| Sposób pobrania | Pobrano z Kaggle |
| Data pobrania | 13.10.2026 |
| Adres źródłowy | https://www.kaggle.com/datasets/bartoszpieniak/poland-cars-for-sale-dataset |
| Limity, koszt i uprawnienia | Do ustalenia w warunkach źródła; plik lokalny nie udostępnia API ani znanych limitów zapytań. |
| Licencja i zasady publikacji | CC0: Public Domain |
| Osoba odpowiedzialna | Adrian Świeca |
| Plan awaryjny | Rozważony skrypt `simonloach/car-scraper` do eksportu publicznych ofert Otomoto.pl |
