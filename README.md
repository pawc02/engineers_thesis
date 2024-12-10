# Informacje dotyczące aplikacji

Program demonstruje działanie algorytmów opartych
na krzywych eliptycznych. Zawiera implementacje trzech algorytmów: 
ElGamala na krzywych eliptycznych, ECDSA oraz faktoryzacji Lenstry.

## Wymagania wstępne

Przed uruchomieniem aplikacji należy upewnić się,
że w systemie zainstalowane jest następujące oprogramowanie:

1. **Python**: Aplikacja została napisana w języku Python. Aby go zainstalować należy użyć poniższych poleceń:
    ```bash
    sudo apt update
    sudo apt install python3
    ```

2. **Matplotlib**: Biblioteka używana do wizualizacji krzywych eliptycznych. Aby ją zainstalować należy użyć poniższego polecenia:
    ```bash
    sudo apt install python3-matplotlib
    ```

3. **Django**: Framework webowy używany do tworzenia aplikacji. Aby go zainstalować należy użyć poniższego polecenia:
    ```bash
    sudo apt install python3-django
    ```

## Uruchomienie aplikacji

1. **Wejdź do katalogu projektu**: Należy upewnić się że jesteśmy w zewnętrznym folderze eccProject.

2. **Uruchomienie serwera**: Aby uruchomić serwer deweloperski Django i włączyć aplikację, należy użyć poniższego polecenia:
    ```bash
    python3 manage.py runserver
    ```

Po uruchomieniu serwera, aplikacja będzie dostępna pod adresem:
   ```bash
   http://127.0.0.1:8000/
   ```

Aby uruchomić testy, należy użyć poniższego polecenia:
```bash
python3 manage.py test
```

### Opis głównych plików aplikacji:

Poniższe pliki znajdują się w folderze eccApp.

1. **views.py**: Logika wyświetlania widoków i obsługi żądań.
2. **appModule.py**: Funkcje używane w widokach.
3. **urls.py**: Adresy URL aplikacji.
4. **forms.py**: Formularze aplikacji.
5. **models.py**: Definicje modeli bazy danych.
6. **tests.py**: Testy jednostkowe aplikacji.
7. **templates/**: Folder z szablonami HTML renderowanymi przez widoki.


### Dodatkowe informacje

Baza danych zawiera już przykładowych użytkowników aplikacji
(ich hasła są identyczne z nazwą danego użytkownika) oraz przykładowe 
zaszyfrowane i podpisane wiadomości. Można je wyświetlić na stronie 
algorytmu ElGamala po kliknięciu przycisku  „Zaszyfrowane wiadomości”
oraz na stronie algorytmu ECDSA po kliknięciu przycisku
„Podpisane wiadomości”. Ponadto widoki i funkcje zawierają dokładne 
komentarze wyjaśniające ich działanie.