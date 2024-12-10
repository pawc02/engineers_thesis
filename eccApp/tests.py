from django.test import TestCase
from .appModule import elliptic_curve_add, elliptic_curve_multiply, Point, ecdsa_sign, ecdsa_verify, elgamal_encrypt, elgamal_decrypt, ecm_factorization

class EllipticCurveOperationsTest(TestCase):
    def setUp(self):
        # Parametry krzywej eliptycznej: y^2 = x^3 + ax + b mod n
        self.a = 1  # Współczynnik a w równaniu krzywej
        self.n = 11  # Liczba odnosząca się do Z_n, nad którym zdefifiowana jest krzywa.
        self.infinity_point = Point()  # Punkt w nieskończoności
        self.G = Point(2, 7, False) # Punkt bazowy na krzywej

    def test_add_with_infinity_point(self):
        result = elliptic_curve_add(self.G, self.infinity_point, self.a, self.n)
        self.assertEqual(result, self.G, "Dodanie punktu do nieskończoności powinno zwrócić ten sam punkt.")
        result = elliptic_curve_add(self.infinity_point, self.G, self.a, self.n)
        self.assertEqual(result, self.G, "Dodanie nieskończoności do punktu powinno zwrócić ten sam punkt.")

    def test_add_opposite_points(self):
        opposite_point = Point(self.G.x, (-self.G.y) % self.n, False)
        result = elliptic_curve_add(self.G, opposite_point, self.a, self.n)
        self.assertTrue(result.is_infinity, "Dodanie punktów przeciwnych powinno zwrócić punkt w nieskończoności.")

    def test_add_points(self):
        point_p = Point(2, 7, False)
        point_q = Point(5, 2, False)
        result = elliptic_curve_add(point_p, point_q, self.a, self.n)
        self.assertEqual(result, Point(8,3,False), "Sprawdzenie poprawności dodawania punktów.")

    def test_multiply_point(self):
        multiplier = 4
        result = elliptic_curve_multiply(self.G, multiplier, self.a, self.n)
        self.assertEqual(result, Point(10,2,False), "Sprawdzenie poprawności obliczania wielokrotności punktu.")


class EcdsaTests(TestCase):
    def setUp(self):
        self.p = 37  # Liczba odnosząca się do Z_p, nad którym zdefifiowana jest krzywa.
        self.a = 1  # Współczynnik 'a' krzywej eliptycznej
        self.b = 11  # Współczynnik 'b' krzywej eliptycznej
        self.curve_n = 23  # Rząd punktu bazowego
        self.g_x = 2  # Współrzędna x punktu bazowego
        self.g_y = 13  # Współrzędna y punktu bazowego
        self.privkey = 6  # Przykładowy klucz prywatny
        self.pubkey = elliptic_curve_multiply(Point(self.g_x, self.g_y, False), self.privkey, self.a, self.p)
        self.message_hash = "8c14f0d"  # Przykładowy hash wiadomości w postaci heksadecymalnej

    def test_ecdsa_sign(self):
        r, s = ecdsa_sign(self.privkey, self.message_hash, self.p, self.a, self.curve_n, self.g_x, self.g_y)
        self.assertGreater(r, 0, "Komponent 'r' podpisu powinien być większy od 0.")
        self.assertGreater(s, 0, "Komponent 's' podpisu powinien być większy od 0.")
        self.assertLess(r, self.curve_n, "Komponent 'r' podpisu powinien być mniejszy od rzędu krzywej.")
        self.assertLess(s, self.curve_n, "Komponent 's' podpisu powinien być mniejszy od rzędu krzywej.")

    def test_ecdsa_verify_valid_signature(self):
        # Test weryfikacji poprawnego podpisu.
        r, s = ecdsa_sign(self.privkey, self.message_hash, self.p, self.a, self.curve_n, self.g_x, self.g_y)
        is_valid = ecdsa_verify(self.pubkey, self.message_hash, r, s, self.p, self.a, self.curve_n, self.g_x, self.g_y)
        self.assertTrue(is_valid, "Poprawny podpis powinien zostać zweryfikowany pomyślnie.")

    def test_ecdsa_verify_invalid_signature(self):
        # Test weryfikacji nieprawidłowego podpisu.
        r, s = ecdsa_sign(self.privkey, self.message_hash, self.p, self.a, self.curve_n, self.g_x, self.g_y)
        # Fałszywy podpis
        invalid_r, invalid_s = (r-1)%self.curve_n, (s+1)%self.curve_n
        is_valid = ecdsa_verify(self.pubkey, self.message_hash, invalid_r, invalid_s, self.p, self.a, self.curve_n, self.g_x, self.g_y)
        self.assertFalse(is_valid, "Nieprawidłowy podpis nie powinien zostać zweryfikowany.")


class ElGamalTests(TestCase):
    def setUp(self):
        self.curve_p = 11  # Z_p (pole liczb modulo)
        self.curve_a = 1  # Współczynnik 'a' w równaniu krzywej eliptycznej
        self.curve_b = 6  # Współczynnik 'b' w równaniu krzywej eliptycznej
        self.G = Point(2, 7, False)  # Punkt bazowy na krzywej eliptycznej
        self.privkey = 6  # Klucz prywatny
        self.pubkey = elliptic_curve_multiply(self.G, self.privkey, self.curve_a, self.curve_p) # Klucz publiczny
        self.P = Point(8, 3, False) # Punkt reprezentujący wiadomość

    def test_elgamal_decrypt(self):
        # Szyfrujemy wiadomość
        C1, C2 = elgamal_encrypt(self.pubkey, self.P, self.G, self.curve_a, self.curve_p)
        # Deszyfrujemy wiadomość
        decrypted_point = elgamal_decrypt(self.privkey, C1, C2, self.curve_a, self.curve_p)
        # Sprawdzamy, czy odszyfrowany punkt jest równy oryginalnej wiadomości P
        self.assertEqual(decrypted_point, self.P, "Deszyfrowana wiadomość nie jest zgodna z oryginałem.")

    def test_elgamal_with_invalid_key(self):
        # Szyfrujemy wiadomość
        C1, C2 = elgamal_encrypt(self.pubkey, self.P, self.G, self.curve_a, self.curve_p)
        # Próbujemy deszyfrować wiadomość z nieprawidłowym kluczem prywatnym
        invalid_privkey = 10
        decrypted_point = elgamal_decrypt(invalid_privkey, C1, C2, self.curve_a, self.curve_p)
        # Oczekujemy, że odszyfrowana wiadomość nie będzie równa oryginalnej wiadomości P
        self.assertNotEqual(decrypted_point, self.P, "Deszyfrowana wiadomość nie powinna być zgodna z oryginałem.")


class ECMFactorizationTests(TestCase):

    def test_ecm_factorization(self):
        n = 221  # 221 = 13 * 17
        factor, attempts = ecm_factorization(n)

        self.assertTrue(n % factor == 0, "Znaleziony dzielnik nie dzieli liczby n!")
        self.assertIn(factor, [13, 17], "Znaleziony dzielnik nie jest poprawny dla liczby n=221!")
