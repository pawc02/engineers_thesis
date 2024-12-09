# Instrukcja uruchomienia aplikacji

Projekt zawiera program demonstrujący działanie algorytmów opartych
na krzywych eliptycznych. Program zawiera trzy algorytmy: 
algorytm ElGamala na krzywych eliptycznych, algorytm ECDSA oraz
algorytm faktoryzacji Lenstry.

## Wymagania wstępne

Przed uruchomieniem aplikacji należy upewnić się,
że w systemie zainstalowane są następujące oprogramowanie:

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