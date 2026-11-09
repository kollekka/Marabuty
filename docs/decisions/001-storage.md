# ADR-001: Zapis wyników analizy i artefaktu modelu

**Status:** przyjęta dla MVP (2026-11-09)

## Kontekst

Projekt jest aplikacją webową z formularzem React i API FastAPI. Model jest trenowany offline na jednej migawce ogłoszeń, a podczas żądania API system oblicza wycenę jednego samochodu. Wymagania R1–R3 opisują wynik prognozy i ocenę ceny oferty, ale nie wymagają kont użytkowników, wspólnej historii wycen, filtrowania wcześniejszych wyników ani równoczesnego zapisu wielu prognoz.

W repozytorium działają już skrypty przetwarzające i ewaluujące pliki CSV. `scripts/compare_methods.py` zapisuje wyniki ewaluacji, ale nie zapisuje wytrenowanego modelu do późniejszej predykcji. Artefakt dla aplikacji będzie więc nowym rezultatem treningu offline. Dane źródłowe to jedna migawka 233 040 rekordów i 103 kolumn; przetworzony zbiór ma 81 kolumn. Model i wyniki są niewielkie w porównaniu z typową bazą wielu użytkowników.

Zespół liczy trzy osoby i pracuje w Pythonie z pandas i scikit-learn. Nie ma dedykowanej osoby do administracji bazą, migracji, kopii zapasowych i monitoringu. Czas laboratorium jest ograniczony, a zakres MVP jest celowo mały. Koszt utrzymania i możliwości zespołu są istotne, ale nie są jedynym argumentem: decyduje przede wszystkim brak wymagań, które uzasadniałyby relacyjną bazę.

## Decyzja

- Wytrenowany pipeline modelu i jego metadane przechowujemy jako pliki: `models/price-ridge.joblib` oraz `models/manifest.json`.
- Manifest identyfikuje model i dane treningowe oraz zawiera wymagane przez runtime pola: `model_version`, `data_version`, `method`, `target_transform="log1p"`, `features` w kolejności `MODEL_FEATURES`, `scope="Używane"`, `interval_method` i `interval_coverage` w `(0,1)`. Pola `schema_version`, `trained_at`, `training_rows`, `input_sha256`, `source_file`, `snapshot_date`, `row_count`, `column_count` i `code_commit` są opcjonalnymi metadanymi wersjonowania; obecny runtime ich nie wymaga.
- Wyniki analiz zapisujemy w plikach CSV. Dla nowych uruchomień docelowy jest katalog `results/runs/<data_version>/<run_id>/` z `run.json`, `comparison.csv` i `observations.csv`. `run.json` zawiera wersję danych, parametry, SHA256 wejścia, commit kodu i datę uruchomienia.
- Migawka źródłowa i wersje modelu są niezmienne. Nowa migawka, nowy model lub nowy run dostają nowy identyfikator wersji; nie nadpisują poprzednich wyników. Zapis odbywa się przez plik tymczasowy i atomową podmianę.
- FastAPI wczytuje i weryfikuje zestaw plików **leniwie, przy pierwszym żądaniu** (`get_prediction_runtime` w `app/main.py`); opcjonalny startup check może to zmienić w przyszłości. Brak artefaktu, kalibratora lub zgodności wymaganych pól manifestu oznacza brak gotowości usługi; API zwraca `503 model_not_ready` i nie udaje prognozy.
- Pojedyncze żądania i odpowiedzi prognozy nie są trwale zapisywane w MVP. Wynik wraca do klienta jako JSON. CSV z `results/lab4/` pozostają artefaktami ewaluacji, a nie historią użytkowników.
- Model musi być wytrenowany i oceniony na pełnym zbiorze aut `Używane`; próbka 25 rekordów jest wyłącznie techniczna.
- W tym projekcie nie tworzymy `forecast.csv` z kolumnami `data`, `wartość`, `jednostka`, bo UC-01 nie jest prognozą szeregu czasowego. Odpowiednikiem wyniku są `comparison.csv` i `observations.csv`. Gdyby pojawił się wymóg eksportu predykcji, może powstać opcjonalny `predictions.csv`, ale nie jest to część MVP.

## Alternatywa

| Alternatywa | Zaleta | Powód odrzucenia na MVP |
|---|---|---|
| SQLite dla prognoz i historii uruchomień | Jeden plik, transakcje, klucze, łatwe filtrowanie historii | Wymagania nie przewidują historii, kont ani wspólnego dostępu. Doszłyby migracje, schemat, obsługa blokad i testy współbieżności bez korzyści użytkowej. |
| PostgreSQL jako usługa | Współbieżny zapis, trwałość, zapytania po wielu użytkownikach | Większy koszt operacyjny: serwer, konfiguracja, kopie zapasowe, monitoring, uprawnienia i wdrożenie. Przy trzech osobach i jednej migawce to nadmiar. |
| Trenowanie modelu przy każdym żądaniu | Brak osobnego artefaktu | Zwiększa opóźnienie, powtarza koszt obliczeń i utrudnia stabilne przypisanie wyniku do wersji modelu oraz danych. |
| Zapis każdej prognozy do pliku CSV | Prosty audit trail | Nie jest potrzebny do R1/R3 i gromadziłby parametry aut oraz ceny ofertowe bez funkcji przeglądu historii. |
| Baza SQLite tylko na potrzeby diagramu ERD | Łatwiej narysować tabele | To byłaby fikcyjna baza: aplikacja jej nie używa, a wymagania jej nie uzasadniają. |

## Powód wyboru

- **Dopasowanie do wymagań.** UC-01 kończy się odpowiedzią API, a nie zapisem rekordu. Nie ma wymagania historii, kont, wspólnego dostępu ani zapytań po wielu uruchomieniach.
- **Wzorzec odczytu i zapisu.** Trening i ewaluacja są wsadowe, offline, na jednym pliku. Predykcja jest pojedyncza i bezstanowa. Pliki CSV i joblib pasują do tego wzorca lepiej niż baza transakcyjna.
- **Powtarzalność.** `data_version`, `model_version`, `run_id`, SHA256 i `code_commit` pozwalają odtworzyć wynik i porównać uruchomienia bez serwera bazy.
- **Koszt i możliwości zespołu.** Trzy osoby, Python/pandas/scikit-learn, brak osoby od administracji bazą. Utrzymanie plików jest tańsze i prostsze niż utrzymanie PostgreSQL; SQLite byłby możliwy, ale nadal wymagałby schematu, migracji i obsługi współbieżności, których MVP nie potrzebuje.
- **Odporność na błędy.** Zapis atomowy i niezmienne katalogi runów rozwiązują najważniejsze ryzyko: nadpisanie lub utratę poprzedniego wyniku. Baza nie jest do tego konieczna.
- **Znajomość narzędzia.** SQLite jest znany zespołowi ze scrapera, ale sama znajomość nie wystarcza. Wybór plików wynika z braku wymagań bazodanowych, a nie z nieznajomości SQL.

## Konsekwencja

Pozytywne:

- prosty, przenośny zapis bez serwera i bez migracji,
- łatwe przeglądanie i diffowanie CSV oraz JSON w repozytorium,
- powtarzalne uruchomienia dzięki wersjom i sumom kontrolnym,
- brak kosztu operacyjnego bazy w MVP.

Negatywne:

- brak historii wycen i zapytań po wielu użytkownikach,
- brak transakcji i kluczy obcych wymuszanych przez silnik; walidację trzeba zaimplementować w aplikacji,
- brak współbieżnego zapisu; dwa procesy nie mogą pisać do tego samego katalogu runu,
- trzeba pilnować unikalności `run_id`, wersji modelu i zgodności schematu,
- pliki mogą urosnąć, jeśli w przyszłości pojawi się wiele migawek lub wyników.

## Warunek ponownego rozważenia

Wrócić do decyzji o bazie danych, jeśli pojawi się którykolwiek z warunków:

- wymaganie historii wycen, kont użytkowników, wspólnego dostępu lub audytowalnego rejestru prognoz,
- równoczesny zapis wielu użytkowników lub wielu procesów,
- potrzeba zapytań i raportowania po wielu uruchomieniach, migawkach lub modelach,
- wiele migawek danych wymagających relacji i spójności transakcyjnej,
- wzrost liczby wyników, który sprawia, że pliki przestają być wygodne w utrzymaniu,
- zmiana składu zespołu lub pojawienie się osoby odpowiedzialnej za utrzymanie bazy.
