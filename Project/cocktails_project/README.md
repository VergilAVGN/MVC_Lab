# Kolekcja Ulubionych Przepisów do Koktajli (Zadanie 8)

Aplikacja internetowa realizująca architekturę MVC napisana z użyciem frameworka Django (Python). Projekt został przygotowany jako zadanie zaliczeniowe przedmiotu **Wzorzec MVC w tworzeniu aplikacji internetowych**.

## Spis treści
1. [Przegląd możliwości i funkcjonalności](#przegląd-możliwości-i-funkcjonalności)
2. [Instrukcja obsługi (Jak uruchomić)](#instrukcja-obsługi)
   - [Opcja 1: Z użyciem Docker](#opcja-1-docker)
   - [Opcja 2: Lokalne środowisko Python](#opcja-2-lokalnie)
   - [Zasilenie bazy przykładowymi danymi](#zasilenie-bazy)
   - [Panel Administratora](#panel-administratora)
3. [Realizacja wymagań dodatkowych (na ocenę 5.0)](#wymagania-dodatkowe)

---

## Przegląd możliwości i funkcjonalności
- **Dodawanie, edycja i usuwanie przepisów (CRUD)**: pełne zarządzanie encją `Recipe` poprzez dedykowane, walidowane formularze. Operacje tworzenia i edycji wymagają zalogowania.
- **Powiązania między modelami:** zastosowano relację *Jeden-do-Wielu* między użytkownikiem a przepisami (`Recipe → User`), komentarzami (`Comment → Recipe`, `Comment → User`) oraz ulubionymi (`Favorite → Recipe`, `Favorite → User`).
- **Walidacja danych:** ograniczenia po stronie serwera w pliku `forms.py` — długość nazwy (3–100 znaków), wymagany format składników (`- składnik`) i instrukcji (`1. krok`), walidacja rozmiaru i typu przesyłanego obrazu (Pillow). Po stronie klienta skrypt `autoformat.js` automatycznie formatuje wpisywane składniki i kroki instrukcji.
- **Nowoczesny wygląd:** listy, formularze i widok szczegółów ostylowano własnymi stylami CSS (karty, cienie, responsywne obrazy), nadając projektowi schludny i czytelny kształt.
- **Integracja z zewnętrznym API:** import przepisów z bazy **TheCocktailDB** — wystarczy wpisać nazwę koktajlu (np. Mojito), a formularz zostanie wypełniony automatycznie (składniki, instrukcje, zdjęcie).
- **Ulubione i komentarze:** zalogowani użytkownicy mogą dodawać przepisy do ulubionych oraz komentować cudze przepisy. Administrator (staff) może moderować komentarze innych użytkowników.
- **Filtrowanie / wyszukiwanie:** widok główny umożliwia wyszukiwanie przepisów po nazwie (`q`) oraz sortowanie po dacie dodania, nazwie lub autorze. Lista jest paginowana (8 przepisów na stronę).
- **System logowania:** rejestracja nowych kont, logowanie oparte o sesje Django, ochrona operacji modyfikacji dekoratorem `@login_required`.

---

## Instrukcja obsługi

Należy pobrać kod źródłowy projektu. Można to zrobić pobierając archiwum ZIP lub klonując repozytorium:
```bash
git clone https://github.com/VergilAVGN/MVC_Lab.git
cd MVC_Lab/Project/cocktails_project
```

### Opcja 1: Docker
Najprostszym sposobem uruchomienia projektu (i wykazania integracji z nowoczesnymi środowiskami) jest użycie konteneryzacji.
Projekt korzysta z lekkiej bazy plikowej **SQLite3** uruchamianej wewnątrz kontenera.

1. Należy upewnić się, że na systemie zainstalowany i uruchomiony jest program *Docker Desktop* (lub demon Dockera).
2. W głównym folderze projektu (`cocktails_project`) należy otworzyć terminal i wykonać polecenie:
   ```bash
   docker compose up --build
   ```
3. Kontener pobierze zależności i zbuduje aplikację automatycznie (migracje uruchamiane są przy starcie). Po komunikacie o starcie serwera aplikacja będzie dostępna pod adresem: `http://localhost:8000/`.

### Opcja 2: Lokalnie
Aby uruchomić program przy użyciu wyłącznie lokalnego środowiska *Python*:
1. Należy utworzyć lokalne środowisko wirtualne:
   ```bash
   python -m venv venv
   ```
2. Następnie aktywować środowisko:
   ```bash
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
3. Zainstalować wymagane pakiety:
   ```bash
   pip install -r requirements.txt
   ```
4. Wykonać migracje bazodanowe (co utworzy strukturę lokalnej bazy plikowej SQLite3) oraz uruchomić serwer:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
5. Aplikacja będzie dostępna pod adresem: `http://localhost:8000/`.

### Zasilenie bazy
Aby zasilić aplikację początkowymi danymi pokazowymi, należy użyć poniższego skryptu ładującego dane (wymagane jest wcześniejsze wykonanie migracji):
```bash
python manage.py loaddata sample_data.json
# Lub w środowisku Docker:
docker compose exec web python manage.py loaddata sample_data.json
```
_Gotowe!_ Od teraz w aplikacji będą widoczne przykładowe przepisy (Mojito, Margarita, Old Fashioned, Piña Colada) wraz z komentarzami użytkownika `demo`.

Można również założyć własne konto przez link **Register** na stronie głównej.

### Panel Administratora
Django posiada wbudowany panel administratora, który został skonfigurowany dla tego projektu. Umożliwia on łatwe zarządzanie bazą danych (w tym dodawanie i edycję przepisów bez modyfikacji kodu).
1. Należy utworzyć konto superużytkownika (w nowym oknie terminala):
   ```bash
   python manage.py createsuperuser
   # Lub w środowisku Docker:
   docker compose exec web python manage.py createsuperuser
   ```
2. Przejść pod adres: `http://localhost:8000/admin/` i zalogować się utworzonymi danymi.

---
## Wymagania dodatkowe
- **Dodanie dodatkowych dwóch modeli** → Stworzone zostały modele `Comment` i `Favorite` obok głównego `Recipe`, powiązane relacjami kluczy obcych z `Recipe` i `User`.
- **Dodanie ostylowanego widoku** → Listy przepisów, widok szczegółów, formularze oraz strony logowania/rejestracji ostylowano własnymi stylami CSS (karty, sekcje komentarzy, responsywne obrazy).
- **Wdrożenie Dockera** → Projekt można zbudować i uruchomić za pomocą plików `Dockerfile` i `docker-compose.yml`.
- **Testy jednostkowe** → W pliku `recipes/tests.py` znajduje się 9 testów obejmujących m.in. paginację, autoryzację CRUD, ulubione, komentarze i walidację formularza. Uruchomienie: `python manage.py test recipes`.
- **Walidacja na serwerze i kliencie** → Formularz `RecipeForm` sprawdza długość nazwy, format składników i instrukcji oraz poprawność obrazu (server-side). Skrypt `autoformat.js` automatycznie formatuje pola tekstowe po stronie klienta (client-side).
- **Integracja z zewnętrznym API** → Moduł `cocktail_api.py` pobiera dane koktajli z API [TheCocktailDB](https://www.thecocktaildb.com/) i wypełnia formularz dodawania przepisu.
- **Filtrowanie / wyszukiwanie** → Widok listy obsługuje wyszukiwanie po nazwie (`name__icontains`) oraz sortowanie po dacie, nazwie i autorze.
- **System logowania** → Rejestracja (`/register/`), logowanie (`/accounts/login/`), sesje Django; tworzenie i edycja przepisów dostępne tylko po zalogowaniu.
