import hashlib
import random
import math

class Point:
    def __init__(self, x=0, y=0, is_infinity=True):
        self.x = x
        self.y = y
        self.is_infinity = is_infinity

    def set_infinity(self):
        self.is_infinity = True

    def unset_infinity(self):
        self.is_infinity = False

def mod(a, m):
    res = a % m
    return res if res >= 0 else res + m

def mod_inverse(a, n):
    t, newt = 0, 1
    r, newr = n, a
    while newr != 0:
        quotient = r // newr
        t, newt = newt, t - quotient * newt
        r, newr = newr, r - quotient * newr
    if r > 1:
        # Jeśli nie ma odwrotności, gcd(a, n) jest dzielnikiem
        factor = gcd(a, n)
        raise ValueError(f"a is not invertible, factor = {factor}")
    return t + n if t < 0 else t

def elliptic_curve_add(p, q, a, n):
    if p.is_infinity:
        return q
    if q.is_infinity:
        return p

    if p.x == q.x and (p.y + q.y) % n == 0:
        return Point()

    try:
        if p.x == q.x and p.y == q.y:
            # Point doubling
            pom = (2 * p.y) % n
            lambda_ = ((3 * p.x * p.x + a) * mod_inverse(pom, n)) % n
        else:
            # Point addition
            pom = ((q.x - p.x) % n + n) % n
            pom2 = ((q.y - p.y) % n + n) % n
            lambda_ = pom2 * mod_inverse(pom, n) % n
    except ValueError as e:
        # Złap wyjątek i przerzuć go dalej, aby zgłosić znaleziony dzielnik
        raise e

    xr = (lambda_ * lambda_ - p.x - q.x) % n
    xr = (xr + n) % n
    yr = (lambda_ * (p.x - xr) - p.y) % n
    yr = (yr + n) % n
    r = Point(xr, yr, False)
    if xr == 0 and yr == 0:
        r.set_infinity()

    return r

def elliptic_curve_multiply(p, k, a, n):
    result = Point()
    temp = p
    while k > 0:
        if k % 2 == 1:
            result = elliptic_curve_add(result, temp, a, n)
        temp = elliptic_curve_add(temp, temp, a, n)
        k //= 2
    return result

def generate_key_pair(curve_p, curve_a, curve_n, g_x, g_y):
    privkey = random.randint(1, curve_n - 1)
    G = Point(g_x, g_y, False)
    pubkey = elliptic_curve_multiply(G, privkey, curve_a, curve_p)
    return privkey, pubkey

def hash_message(message):
    return hashlib.sha256(message.encode('utf-8')).hexdigest()

def ecdsa_sign(privkey, hash, p, a, curve_n, g_x, g_y):
    G = Point(g_x, g_y, False)
    while True:
        k = random.randint(1, curve_n - 1)
        R = elliptic_curve_multiply(G, k, a, p)
        r = mod(R.x, curve_n)
        if r != 0:
            break
    h = mod(int(hash, 16), curve_n)
    s = mod(mod_inverse(k, curve_n) * (h + privkey * r), curve_n)
    if s == 0:
        raise ValueError("Signature s is zero")

    return r, s

def ecdsa_verify(pubkey, hash, r, s, p, a, curve_n, g_x, g_y):
    G = Point(g_x, g_y, False)
    h = mod(int(hash, 16), curve_n)
    w = mod_inverse(s, curve_n)
    u1 = mod(h * w, curve_n)
    u2 = mod(r * w, curve_n)

    u1G = elliptic_curve_multiply(G, u1, a, p)
    u2Q = elliptic_curve_multiply(pubkey, u2, a, p)
    R = elliptic_curve_add(u1G, u2Q, a, p)

    return mod(R.x, curve_n) == r

def elgamal_encrypt(pubkey, P, G, curve_a, curve_b, curve_p, curve_n):
    r = random.randint(1, curve_n - 1)
    C1 = elliptic_curve_multiply(G, r, curve_a, curve_p)
    rkB = elliptic_curve_multiply(pubkey, r, curve_a, curve_p)
    C2 = elliptic_curve_add(P, rkB, curve_a, curve_p)
    return C1, C2

def elgamal_decrypt(privkey, C1, C2, G, curve_a, curve_b, curve_p, curve_n):
    kC1 = elliptic_curve_multiply(C1, privkey, curve_a, curve_p)
    kC1.y = -kC1.y % curve_p  # Negacja współrzędnej y
    return elliptic_curve_add(C2, kC1, curve_a, curve_p)

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def lcm(a, b):
    return (a // gcd(a, b)) * b

def lcm_ext(numbers):
    wynik = numbers[0]
    for num in numbers[1:]:
        wynik = lcm(wynik, num)
    return wynik

def ecm_factorization(n):
    attempts = 0
    while True:
        a = random.randint(1, n - 1)
        x = random.randint(1, n - 1)
        y = random.randint(1, n - 1)
        b = (y * y - x * x * x - a * x) % n
        if b < 0:
            b += n

        # Jeśli największy wspólny dzielnik jest różny od 1, przejdź do następnej iteracji
        if gcd(4 * a * a * a + 27 * b * b, n) != 1:
            continue

        attempts += 1
        P = Point(x, y, False)

        numbers = [i for i in range(2, 11)]
        k = lcm_ext(numbers)

        # Próbuj wykonywać operacje na krzywej eliptycznej
        try:
            P = elliptic_curve_multiply(P, k, a, n)
        except ValueError as e:
            # Jeśli pojawi się błąd z `mod_inverse`, oznacza to, że znaleźliśmy dzielnik
            dzielnik = int(str(e).split('=')[-1].strip())  # Pobieramy wartość dzielnika z komunikatu błędu
            return dzielnik, attempts
