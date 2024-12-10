import hashlib
import random
#import math
import matplotlib.pyplot as plt
import io
import base64

class Point:
    """
    @brief Klasa reprezentująca punkt na krzywej eliptycznej.
    Atrybuty:
        x (int): Współrzędna x punktu.
        y (int): Współrzędna y punktu.
        is_infinity (bool): Flaga wskazująca, czy punkt jest punktem w nieskończoności.
    """
    def __init__(self, x=0, y=0, is_infinity=True):
        """
        @brief Inicjalizuje obiekt punktu na krzywej eliptycznej.
        @param x Współrzędna x punktu (domyślnie 0).
        @param y Współrzędna y punktu (domyślnie 0).
        @param is_infinity Flaga określająca, czy punkt jest w nieskończoności (domyślnie True).
        """
        self.x = x
        self.y = y
        self.is_infinity = is_infinity

    def set_infinity(self):
        self.is_infinity = True

    def unset_infinity(self):
        self.is_infinity = False

    def __eq__(self, other):
        if isinstance(other, Point):
            if self.is_infinity and other.is_infinity:
                return True
            if self.is_infinity != other.is_infinity:
                return False
            return self.x == other.x and self.y == other.y
        return False

def mod(a, m):
    """
    @brief Funkcja oblicza resztę z dzielenia liczby `a` przez `m`.
    @param a Liczba, której resztę należy obliczyć.
    @param m Wykonujemy działanie modulo m
    @return Reszta z dzielenia `a` przez `m`.
    """
    res = a % m
    return res if res >= 0 else res + m

def mod_inverse(a, n):
    """
    @brief Funkcja oblicza odwrotność modulo `n` dla liczby `a` za pomocą rozszerzonego algorytmu Euklidesa.
    @param a Liczba, której odwrotność modulo `n` należy obliczyć.
    @param n Obliczamy odwrotność modulo `n`.
    @return Odwrotność liczby `a` modulo `n`.
    """
    t, newt = 0, 1
    r, newr = n, a
    while newr != 0:
        quotient = r // newr
        t, newt = newt, t - quotient * newt
        r, newr = newr, r - quotient * newr
    if r > 1:
        # Jeśli liczba jest nieodwracalna, gcd(a, n) jest dzielnikiem liczby n
        factor = gcd(a, n)
        raise ValueError(f"a nie jest odwracalne, dzielnik = {factor}")
    return t + n if t < 0 else t

def gcd(a, b):
    """
    @brief Funkcja oblicza największy wspólny dzielnik dwóch liczb.
    @param a Pierwsza liczba całkowita.
    @param b Druga liczba całkowita.
    @return Największy wspólny dzielnik liczb a i b.
    """
    while b != 0:
        a, b = b, a % b
    return a

def lcm(a, b):
    """
    @brief Funkcja oblicza najmniejszą wspólną wielokrotność dwóch liczb.
    @param a Pierwsza liczba całkowita.
    @param b Druga liczba całkowita.
    @return Najmniejsza wspólna wielokrotność liczb a i b.
    """
    return (a // gcd(a, b)) * b

def lcm_ext(numbers):
    """
    @brief Funkcja oblicza najmniejszą wspólną wielokrotność dla listy liczb.
    @param numbers Lista liczb całkowitych, dla których ma być obliczona najmniejsza wspólna wielokrotność.
    @return Najmniejsza wspólna wielokrotność wszystkich liczb w liście.
    """
    wynik = numbers[0]
    for num in numbers[1:]:
        wynik = lcm(wynik, num)
    return wynik

def is_prime(n):
    """
    @brief Funkcja sprawdza, czy dana liczba jest liczbą pierwszą.
    @param n Liczba całkowita do sprawdzenia.
    @return True, jeśli liczba n jest liczbą pierwszą; False w przeciwnym razie.
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True

def get_random_prime(min_val, max_val):
    """
    @brief Generuje losową liczbę pierwszą w podanym zakresie.
    @param min_val Początkowa wartość zakresu (włącznie).
    @param max_val Końcowa wartość zakresu (włącznie).
    @return Liczba pierwsza w zakresie [min_val, max_val].
    """
    while True:
        candidate = random.randint(min_val, max_val)
        if is_prime(candidate):
            return candidate

def elliptic_curve_add(p, q, a, n):
    """
    @brief Funkcja wykonuje operację dodawania dwóch punktów na krzywej eliptycznej.
    @param p Punkt P na krzywej eliptycznej (obiekt klasy Point).
    @param q Punkt Q na krzywej eliptycznej (obiekt klasy Point).
    @param a Współczynnik 'a' w równaniu krzywej eliptycznej.
    @param n Liczba odnosząca się do Z_n, nad którym zdefifiowana jest krzywa.
    @return Wynik dodawania dwóch punktów (obiekt klasy Point).
    """
    if p.is_infinity:
        return q
    if q.is_infinity:
        return p

    # Dodawanie punktów przeciwnych
    if p.x == q.x and (p.y + q.y) % n == 0:
        return Point()

    try:
        if p.x == q.x and p.y == q.y:
            # Podwajanie punktu
            temp1 = (2 * p.y) % n
            lambda_ = ((3 * p.x * p.x + a) * mod_inverse(temp1, n)) % n
        else:
            # Dodawanie różnych punktów
            temp1 = (q.x - p.x) % n
            temp2 = (q.y - p.y) % n
            lambda_ = temp2 * mod_inverse(temp1, n) % n
    except ValueError as e:
        raise e

    xr = (lambda_ * lambda_ - p.x - q.x) % n
    yr = (lambda_ * (p.x - xr) - p.y) % n
    r = Point(xr, yr, False)

    return r

def elliptic_curve_multiply(p, k, a, n):
    """
    @brief Funkcja oblicza wielokrotność punktu na krzywej eliptycznej.
    @param p Punkt P na krzywej eliptycznej (obiekt klasy Point).
    @param k Współczynnik, przez który punkt P jest mnożony.
    @param a Współczynnik 'a' w równaniu krzywej eliptycznej.
    @param n Liczba odnosząca się do Z_n, nad którym zdefifiowana jest krzywa.
    @return Wynik wielokrotności punktu (obiekt klasy Point).
    """
    result = Point()
    temp = p
    while k > 0:
        if k % 2 == 1:
            result = elliptic_curve_add(result, temp, a, n)
        temp = elliptic_curve_add(temp, temp, a, n)
        k //= 2
    return result

def generate_key_pair(curve_p, curve_a, curve_n, g_x, g_y):
    """
    @brief Funkcja generuje parę kluczy (prywatny i publiczny) na podstawie parametrów krzywej eliptycznej.
    @param curve_p Liczba odnosząca się do Z_p, nad którym zdefifiowana jest krzywa.
    @param curve_a Współczynnik 'a' w równaniu krzywej eliptycznej.
    @param curve_n Liczba punktów na krzywej eliptycznej.
    @param g_x Współrzędna x punktu bazowego.
    @param g_y Współrzędna y punktu bazowego.
    @return Krotka zawierająca:
        - privkey (int): Klucz prywatny.
        - pubkey (Point): Klucz publiczny jako punkt na krzywej eliptycznej.
    """
    privkey = random.randint(1, curve_n - 1)
    G = Point(g_x, g_y, False)
    pubkey = elliptic_curve_multiply(G, privkey, curve_a, curve_p)
    return privkey, pubkey

def hash_message(message):
    """
    @brief Funkcja oblicza hash wiadomości za pomocą algorytmu SHA-256.
    @param message Wiadomość wejściowa do zhashowania.
    @return Hash wiadomości w formacie heksadecymalnym.
    """
    return hashlib.sha256(message.encode('utf-8')).hexdigest()

def ecdsa_sign(privkey, hash, p, a, curve_n, g_x, g_y):
    """
    @brief Funkcja generuje podpis cyfrowy ECDSA dla podanego skrótu wiadomości.
    @param privkey Klucz prywatny użytkownika.
    @param hash Skrót wiadomości (SHA-256) w formacie heksadecymalnym.
    @param p Liczba odnosząca się do Z_p, nad którym zdefifiowana jest krzywa.
    @param a Współczynnik 'a' w równaniu krzywej eliptycznej.
    @param curve_n Liczba punktów na krzywej eliptycznej.
    @param g_x Współrzędna x punktu bazowego.
    @param g_y Współrzędna y punktu bazowego.
    @return Podpis cyfrowy składający się z dwóch liczb:
        - r (int): Pierwsza składowa podpisu.
        - s (int): Druga składowa podpisu.
    """
    G = Point(g_x, g_y, False)
    while True:
        k = random.randint(1, curve_n - 1)
        R = elliptic_curve_multiply(G, k, a, p)
        r = mod(R.x, curve_n)
        if r == 0:
            continue  # Rozpoczynamy od nowa, jeśli r = 0

        h = mod(int(hash, 16), curve_n)
        s = mod(mod_inverse(k, curve_n) * (h + privkey * r), curve_n)
        if s != 0:
            return r, s  # Zwróć podpis tylko jeśli r i s jest różne od 0

def ecdsa_verify(pubkey, hash, r, s, p, a, curve_n, g_x, g_y):
    """
    @brief Funkcja weryfikuje podpis cyfrowy ECDSA dla podanego skrótu wiadomości.
    @param pubkey Klucz publiczny użytkownika jako punkt na krzywej eliptycznej.
    @param hash Skrót wiadomości (SHA-256) w formacie heksadecymalnym.
    @param r Pierwsza składowa podpisu.
    @param s Druga składowa podpisu.
    @param p Liczba odnosząca się do Z_p, nad którym zdefifiowana jest krzywa.
    @param a Współczynnik 'a' w równaniu krzywej eliptycznej.
    @param curve_n Liczba punktów na krzywej eliptycznej.
    @param g_x Współrzędna x punktu bazowego.
    @param g_y Współrzędna y punktu bazowego.
    @return True, jeśli podpis jest prawidłowy, w przeciwnym razie False.
    """
    G = Point(g_x, g_y, False)
    h = mod(int(hash, 16), curve_n)
    w = mod_inverse(s, curve_n)
    u1 = mod(h * w, curve_n)
    u2 = mod(r * w, curve_n)

    u1G = elliptic_curve_multiply(G, u1, a, p)
    u2Q = elliptic_curve_multiply(pubkey, u2, a, p)
    R = elliptic_curve_add(u1G, u2Q, a, p)

    return mod(R.x, curve_n) == r

def elgamal_encrypt(pubkey, P, G, curve_a, curve_p):
    """
    @brief Funkcja szyfruje wiadomość za pomocą algorytmu ElGamala na krzywych eliptycznych.
    @param pubkey Klucz publiczny odbiorcy jako punkt na krzywej eliptycznej.
    @param P Punkt na krzywej eliptycznej reprezentujący szyfrowaną wiadomość.
    @param G Punkt bazowy.
    @param curve_a Współczynnik 'a' w równaniu krzywej eliptycznej.
    @param curve_p Liczba odnosząca się do Z_p, nad którym zdefifiowana jest krzywa.
    @return Para punktów (C1, C2), które stanowią zaszyfrowaną wiadomość:
        - C1 (Point): Pierwszy punkt szyfrogramu.
        - C2 (Point): Drugi punkt szyfrogramu.
    """
    r = random.randint(1, 10*curve_p)
    C1 = elliptic_curve_multiply(G, r, curve_a, curve_p)
    rkB = elliptic_curve_multiply(pubkey, r, curve_a, curve_p)
    C2 = elliptic_curve_add(P, rkB, curve_a, curve_p)
    return C1, C2

def elgamal_decrypt(privkey, C1, C2, curve_a, curve_p):
    """
    @brief Funkcja deszyfruje wiadomość zaszyfrowaną algorytmem ElGamala na krzywych eliptycznych.
    @param privkey Klucz prywatny odbiorcy.
    @param C1 Pierwszy punkt szyfrogramu.
    @param C2 Drugi punkt szyfrogramu.
    @param curve_a Współczynnik 'a' w równaniu krzywej eliptycznej.
    @param curve_p Liczba odnosząca się do Z_p, nad którym zdefifiowana jest krzywa.
    @return Punkt reprezentujący odszyfrowaną wiadomość.
    """
    kC1 = elliptic_curve_multiply(C1, privkey, curve_a, curve_p)
    kC1.y = -kC1.y % curve_p  # Negacja współrzędnej y
    return elliptic_curve_add(C2, kC1, curve_a, curve_p)

def ecm_factorization(n):
    """
    @brief Funkcja znajdująca dzielnik liczby za pomocą algorytmu faktoryzacji Lenstry.
    @param n Liczba, której próbujemy znaleźć dzielnik.
    @return Krotka zawierająca:
        - factor (int): Znaleziony dzielnik liczby n, jeżeli znaleziono.
        - attempts (int): Liczba losowań krzywych wykonanych podczas procesu faktoryzacji.
    """
    attempts = 0
    while True:
        a = random.randint(1, n - 1)
        x = random.randint(1, n - 1)
        y = random.randint(1, n - 1)
        b = (y * y - x * x * x - a * x) % n
        if b < 0:
            b += n

        # Jeśli gcd jest większy od 1 i mniejszy od n, znaleźliśmy dzielnik liczby n
        if 1 < gcd(4 * a * a * a + 27 * b * b, n) < n:
            factor = gcd(4 * a * a * a + 27 * b * b, n)
            return factor, attempts
        # Jeśli gcd jest równe n losujemy ponownie parametry krzywej
        elif gcd(4 * a * a * a + 27 * b * b, n) == n:
            continue

        attempts += 1
        P = Point(x, y, False)

        numbers = [i for i in range(2, 11)]
        k = lcm_ext(numbers)

        # Próba obliczenia wielokrotności P
        try:
            P = elliptic_curve_multiply(P, k, a, n)
        except ValueError as e:
            # Jeśli pojawi się błąd z `mod_inverse`, oznacza to, że znaleźliśmy dzielnik
            factor = int(str(e).split('=')[-1].strip())  # Pobieramy wartość dzielnika z komunikatu błędu
            return factor, attempts


def is_point_on_curve(x, y, a, b, p):
    """
    @brief Funkcja sprawdza, czy punkt (x, y) leży na krzywej eliptycznej.
    @param x Współrzędna x punktu.
    @param y Współrzędna y punktu.
    @param a Współczynnik 'a' w równaniu krzywej eliptycznej.
    @param b Współczynnik 'b' w równaniu krzywej eliptycznej.
    @param p Liczba odnosząca się do Z_p, nad którym zdefifiowana jest krzywa.
    @return Zwraca True, jeśli punkt (x, y) leży na krzywej, w przeciwnym razie False.
    """
    return pow(y, 2, p) == (pow(x, 3, p) + a * x + b) % p

def validate_curve_parameters(curve_p, curve_a, curve_b):
    """
    @brief Funkcja sprawdza, czy parametry krzywej eliptycznej są poprawne.
    @param curve_p Liczba odnosząca się do Z_p, nad którym zdefifiowana jest krzywa.
    @param curve_a Współczynnik 'a' w równaniu krzywej eliptycznej.
    @param curve_b Współczynnik 'b' w równaniu krzywej eliptycznej.
    @return Krotka, która zawiera:
        - (bool): True, jeśli parametry krzywej są poprawne, w przeciwnym razie False.
        - (str): Komunikat o błędzie, jeśli parametry są niepoprawne.
    """
    # Sprawdzamy, czy p jest liczbą pierwszą
    if not is_prime(curve_p):
        return False, f"Liczba p nie jest liczbą pierwszą."

    # Sprawdzamy, czy a i b są w przedziale [0, p-1]
    if not (0 <= curve_a < curve_p):
        return False, f"Współczynnik a nie mieści się w przedziale [0, {curve_p - 1}]."
    if not (0 <= curve_b < curve_p):
        return False, f"Współczynnik b nie mieści się w przedziale [0, {curve_p - 1}]."

    # Sprawdzamy warunek 4a^3 + 27b^2 ≠ 0 (mod p)
    term1 = (4 * pow(curve_a, 3, curve_p)) % curve_p
    term2 = (27 * pow(curve_b, 2, curve_p)) % curve_p
    if (term1 + term2) % curve_p == 0:
        return False, f"Parametry krzywej nie spełniają warunku: 4a^3 + 27b^2 ≠ 0 (mod {curve_p})."

    # Wszystkie testy przeszły pomyślnie
    return True, None

def draw_valid_curve_and_point():
    """
    @brief Funkcja losuje parametry krzywej eliptycznej oraz współrzędne losowego punktu (x, y).
    @return Krotka zawierająca parametry krzywej eliptycznej (p, a, b) oraz współrzędne punktu (x, y).
    """
    # Losowanie liczby pierwszej p
    curve_p = get_random_prime(1, 10**3)

    while True:
        # Losowanie współczynnika a
        curve_a = random.randint(1, curve_p - 1)

        # Losowanie współrzędnych punktu
        g_x = random.randint(1, curve_p - 1)
        g_y = random.randint(1, curve_p - 1)

        # Obliczenie współczynnika b
        curve_b = (g_y * g_y - g_x * g_x * g_x - curve_a * g_x) % curve_p

        # Sprawdzamy warunek 4a^3 + 27b^2 ≠ 0 (mod p)
        delta = (4 * pow(curve_a, 3, curve_p) + 27 * pow(curve_b, 2, curve_p)) % curve_p
        if delta != 0:
            return curve_p, curve_a, curve_b, g_x, g_y


def plot_points_on_curve(curve_p, curve_a, curve_b, points):
    """
    @brief Funkcja rysuje punkty na krzywej eliptycznej.
    @param curve_p Liczba odnosząca się do Z_p, nad którym zdefifiowana jest krzywa.
    @param curve_a Współczynnik 'a' w równaniu krzywej eliptycznej.
    @param curve_b Współczynnik 'b' w równaniu krzywej eliptycznej.
    @param points Lista punktów krzywej, które mają być narysowane.
    @return Wygenerowany obraz wykresu w formacie base64.
    """
    plt.figure(figsize=(6, 6))
    plt.grid(True)
    plt.title(f"Krzywa eliptyczna: y^2 ≡ x^3 + {curve_a}x + {curve_b} (mod {curve_p})")

    # Rozdzielenie punktów na osobne listy współrzędnych x i y
    x_coords, y_coords = zip(*points) if points else ([], [])
    plt.scatter(x_coords, y_coords, color='blue', label='Punkty krzywej')

    plt.xlim(-1, curve_p)
    plt.ylim(-1, curve_p)

    # Zapisanie obrazu w formacie base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    return base64.b64encode(image_png).decode('utf-8')

def plot_elliptic_curve_modulo(p, a, b, points, result_point, operation_type=None, multiplier=None, show_all_curve_points=False):
    """
    @brief Funkcja rysuje wykres krzywej eliptycznej i wynik operacji na punktach na tej krzywej.
    @param p Liczba odnosząca się do Z_p, nad którym zdefifiowana jest krzywa.
    @param a Współczynnik 'a' w równaniu krzywej eliptycznej.
    @param b Współczynnik 'b' w równaniu krzywej eliptycznej.
    @param points Lista punktów na krzywej, które mają być narysowane.
    @param result_point Punkt wynikowy, np. suma punktów P + Q lub wielokrotność punktu kP.
    @param operation_type Typ operacji, np. 'addition' (dodawanie punktów) lub 'multiplication' (wielokrotność punktu).
    @param multiplier Współczynnik używany przy obliczaniu wielokrotności punktu.
    @param show_all_curve_points Jeśli True, rysuje wszystkie punkty leżące na krzywej.
    @return Wygenerowany obraz wykresu w formacie base64.
    """
    plt.figure(figsize=(6, 6))
    plt.title(f"Wykres")

    # Opcjonalne rysowanie wszystkich punktów krzywej
    if show_all_curve_points:
        all_curve_points = []
        for x in range(p):
            for y in range(p):
                if (y ** 2) % p == (x ** 3 + a * x + b) % p:
                    all_curve_points.append((x, y))

        curve_x = [pt[0] for pt in all_curve_points]
        curve_y = [pt[1] for pt in all_curve_points]
        plt.scatter(curve_x, curve_y, c='blue', s=20, label="Punkty krzywej")

    # Rysowanie podanych punktów (P, Q)
    for idx, point in enumerate(points):
        if not point.is_infinity:
            if idx == 0:
                point_label = f"Punkt P ({point.x}, {point.y})"
                color = 'green'  # Kolor dla punktu P
            elif idx == 1:
                point_label = f"Punkt Q ({point.x}, {point.y})"
                color = 'orange'  # Kolor dla punktu Q
            else:
                point_label = f"{idx}P ({point.x}, {point.y})"
                color = 'red'

            plt.scatter(point.x, point.y, c=color, s=100, label=point_label)

    # Rysowanie punktu wynikowego (np. P+Q lub kP)
    if result_point and not result_point.is_infinity:
        if operation_type == "addition":
            result_label = f"P + Q ({result_point.x}, {result_point.y})"
        elif operation_type == "multiplication" and multiplier is not None:
            result_label = f"{multiplier}P ({result_point.x}, {result_point.y})"
        else:
            result_label = f"Wynik ({result_point.x}, {result_point.y})"

        plt.scatter(result_point.x, result_point.y, c='red', s=100, label=result_label)

    plt.xlim(-1, p)
    plt.ylim(-1, p)
    plt.legend()
    plt.grid(True)

    # Zapisanie obrazu w formacie base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    return base64.b64encode(image_png).decode('utf-8')

def get_point_order(point, curve_p, curve_a):
    """
    @brief Funkcja oblicza rząd punktu na krzywej eliptycznej.
    @param point Punkt na krzywej eliptycznej, którego rząd ma zostać obliczony.
    @param curve_p Liczba odnosząca się do Z_p, nad którym zdefifiowana jest krzywa.
    @param curve_a Współczynnik 'a' w równaniu krzywej eliptycznej.
    @return Rząd punktu na krzywej eliptycznej.
    """
    order = 1
    current_point = point

    while not current_point.is_infinity:
        order += 1
        current_point = elliptic_curve_add(current_point, point, curve_a, curve_p)

    return order

def count_points_on_curve(a, b, p):
    """
    @brief Funkcja oblicza liczbę punktów na krzywej eliptycznej.
    @param a Współczynnik a w równaniu krzywej eliptycznej.
    @param b Współczynnik b w równaniu krzywej eliptycznej.
    @param p Liczba odnosząca się do Z_p, nad którym zdefifiowana jest krzywa.
    @return Liczba punktów leżących na krzywej eliptycznej, w tym punkt w nieskończoności.
    """
    points = 1  # Zaczynamy od punktu w nieskończoności
    for x in range(p):
        # Obliczamy prawą stronę równania y^2 ≡ x^3 + ax + b (mod p)
        rhs = (x**3 + a*x + b) % p
        # Sprawdzamy, ile wartości y spełnia równanie y^2 ≡ rhs (mod p)
        num_solutions = 0
        for y in range(p):
            if (y**2) % p == rhs:
                num_solutions += 1
        points += num_solutions
    return points
