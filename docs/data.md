# Ocena danych i źródła

## Opis wybranego źródła

| Element | Wynik sprawdzenia |
|---|---|
| Źródło i właściciel | „Poland cars for sale dataset” (nazwa przekazana w opisie projektu); właściciel lub publikujący do sprawdzenia w dokumentacji źródła. |
| Link | Do sprawdzenia; adres źródłowy nie został zapisany w repozytorium. |
| Wymaganie dostępu | Plik CSV jest dostępny lokalnie w `data/Car_sale_ads.csv`; wymagania pobrania i ewentualnej atrybucji do sprawdzenia. |
| Data pobrania | Do sprawdzenia; nieustalona na podstawie pliku. |
| Format | CSV, 25 kolumn, przecinek jako separator; polskie znaki są poprawnie odczytywane. |
| Liczba rekordów | 208 304 rekordy danych (208 305 wierszy razem z nagłówkiem). |
| Pola | `Index`, `Price`, `Currency`, `Condition`, `Vehicle_brand`, `Vehicle_model`, `Vehicle_version`, `Vehicle_generation`, `Production_year`, `Mileage_km`, `Power_HP`, `Displacement_cm3`, `Fuel_type`, `CO2_emissions`, `Drive`, `Transmission`, `Type`, `Doors_number`, `Colour`, `Origin_country`, `First_owner`, `First_registration_date`, `Offer_publication_date`, `Offer_location`, `Features`. |
| Daty i jednostki | Daty w próbce mają format `DD/MM/YYYY`; widoczne daty publikacji pochodzą z kwietnia i maja 2021 r. `Price` jest podana w PLN, `Mileage_km` w km, `Power_HP` w HP, a `Displacement_cm3` w cm³. Jednostka `CO2_emissions` do sprawdzenia. |
| Braki danych | W próbce 25 rekordów: `Vehicle_version` 24, `Vehicle_generation` 25, `CO2_emissions` 20, `Drive` 3, `Origin_country` 13, `First_owner` 18, `First_registration_date` 17 pustych wartości; w pozostałych polach próbki nie stwierdzono pustych wartości. Pełne braki dla wszystkich kolumn wymagają profilowania w EDA. |
| Limit | Zbiór jest lokalnym plikiem, nie API; ograniczenia pobierania lub wykorzystania do sprawdzenia u publikującego. |
| Klucz | `Index` wygląda na techniczny indeks wiersza; jego unikalność i przydatność jako klucza wymagają potwierdzenia. |
| Koszt | Do sprawdzenia w warunkach źródła. |
| Licencja | Do sprawdzenia przed dalszym udostępnianiem lub wykorzystaniem. |
| Próba ponownego pobrania | Nie wykonano; brak potwierdzonego adresu źródłowego. |
| Brakujące dane | Nieznany jest pełny profil braków w całym zbiorze; w próbce występują braki opisane wyżej. |
| Plan awaryjny | W razie niedostępności źródła znaleźć inny zbiór polskich ogłoszeń z udokumentowaną licencją; alternatywnego zbioru jeszcze nie wybrano. |

## Próbka

`data/sample.csv` zawiera pierwsze 25 rekordów danych z `data/Car_sale_ads.csv` (indeksy 0–24), wraz z nagłówkiem. Jest to wycinek techniczny, a nie próba losowa ani reprezentatywna; nie należy na jego podstawie uogólniać rozkładów w całym zbiorze. W tych 25 rekordach nie znaleziono powtórzonych kompletnych wierszy.
