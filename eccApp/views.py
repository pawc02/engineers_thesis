from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import EcdsaSignForm, EcdsaVerifyForm, ElGamalEncryptForm, ElGamalDecryptForm, KeysGenerationForm, PasswordVerificationForm, LenstraForm, AddPointsForm, MultiplyPointForm, ShowMultiplesForm, ShowCurveGraphForm, UpdateUserParametersForm
from .models import SignedMessage, EncryptedMessage, UserKeys
from .appModule import generate_key_pair, hash_message, ecdsa_sign, ecdsa_verify, Point, elgamal_encrypt, elgamal_decrypt, ecm_factorization, elliptic_curve_add, elliptic_curve_multiply, plot_elliptic_curve_modulo, get_point_order, count_points_on_curve, draw_valid_curve_and_point, plot_points_on_curve, is_point_on_curve, validate_curve_parameters, is_prime
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from django.http import JsonResponse


def home_page(request):
    """
    @brief Wyświetla stronę główną aplikacji.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @return Renderuje stronę `home_page.html`.
    """
    return render(request, 'eccApp/home_page.html')


# Algorytm ECDSA

def ecdsa_page(request):
    """
    @brief Widok wyświetlający stronę główną algorytmu ECDSA w aplikacji.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @return Renderuje stronę `ecdsa_page.html`.
    """
    return render(request, 'eccApp/ecdsa_page.html')

def ecdsa_sign_view(request, key_id=None):
    """
    @brief Widok obsługujący proces podpisywania wiadomości za pomocą algorytmu ECDSA.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @param key_id (opcjonalny) Identyfikator użytkownika w bazie danych, używany do wstępnego wypełnienia formularza.
    @return Renderuje stronę `ecdsa_sign.html` z formularzem do podpisywania wiadomości. W przypadku pomyślnego podpisania wiadomości przekierowuje na stronę z podpisanymi wiadomościami.
    """
    initial_data = {}

    # Wypełnienie formularza danymi użytkownika, jeśli podano `key_id`
    if key_id:
        key = get_object_or_404(UserKeys, pk=key_id)
        initial_data = {
            'username': key.username,
            'curve_p': key.curve_p,
            'curve_a': key.curve_a,
            'curve_b': key.curve_b,
            'g_x': key.g_x,
            'g_y': key.g_y
        }

    if request.method == 'POST':
        form = EcdsaSignForm(request.POST)
        if form.is_valid():
            # Pobranie danych z formularza
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            message = form.cleaned_data['message']
            curve_p = form.cleaned_data['curve_p']
            curve_a = form.cleaned_data['curve_a']
            curve_b = form.cleaned_data['curve_b']
            g_x = form.cleaned_data['g_x']
            g_y = form.cleaned_data['g_y']

            # Walidacja parametrów krzywej
            is_valid_curve, validation_error = validate_curve_parameters(curve_p, curve_a, curve_b)
            if not is_valid_curve:
                messages.error(request, validation_error)
                return render(request, 'eccApp/ecdsa_sign.html', {'form': form})

            # Obliczenie rzędu punktu bazowego
            G = Point(g_x, g_y, False)
            curve_n = get_point_order(G, curve_p, curve_a)

            # Walidacja punktu bazowego
            if not is_point_on_curve(g_x, g_y, curve_a, curve_b, curve_p):
                messages.error(request, f"Punkt bazowy ({g_x}, {g_y}) nie leży na krzywej.")
                return render(request, 'eccApp/ecdsa_sign.html', {'form': form})
            # Sprawdzenie, czy rząd punktu bazowego jest liczbą pierwszą
            if not is_prime(curve_n):
                messages.error(request, f"Rząd punktu bazowego ({curve_n}) nie jest liczbą pierwszą.")
                return render(request, 'eccApp/ecdsa_sign.html', {'form': form})

            try:
                # Wyszukanie użytkownika w bazie danych
                user = UserKeys.objects.get(username=username)

                # Sprawdzenie poprawności hasła
                if check_password(password, user.hashed_password):
                    # Pobranie klucza prywatnego z bazy danych
                    privkey = user.privkey

                    # Hashowanie wiadomości
                    hash_msg = hash_message(message)

                    # Podpisanie wiadomości
                    r, s = ecdsa_sign(privkey, hash_msg, curve_p, curve_a, curve_n, g_x, g_y)

                    # Zapisanie podpisanej wiadomości do bazy danych
                    signed_message = SignedMessage(
                        username=username,
                        curve_p=curve_p,
                        curve_a=curve_a,
                        curve_b=curve_b,
                        curve_n=curve_n,
                        g_x=g_x,
                        g_y=g_y,
                        message=message,
                        pubkey_x=user.pubkey_x,
                        pubkey_y=user.pubkey_y,
                        r=r,
                        s=s,
                        hash=hash_msg
                    )
                    signed_message.save()

                    return redirect(reverse('ecdsa_messages'))
                else:
                    messages.error(request, 'Błędne hasło.')
            except UserKeys.DoesNotExist:
                messages.error(request, 'Użytkownik nie istnieje.')
    else:
        form = EcdsaSignForm(initial=initial_data)

    return render(request, 'eccApp/ecdsa_sign.html', {'form': form})

def ecdsa_messages(request):
    """
    @brief Widok wyświetlający listę podpisanych wiadomości.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @return Renderuje stronę `ecdsa_messages.html`, zawierającą wszystkie wiadomości podpisane za pomocą algorytmu ECDSA.
    """
    messages = SignedMessage.objects.all()
    return render(request, 'eccApp/ecdsa_messages.html', {'messages': messages})

def ecdsa_verify_view(request, message_id=None):
    """
    @brief Widok obsługujący weryfikację podpisów ECDSA.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @param message_id (opcjonalny) Identyfikator podpisanej wiadomości w bazie danych, używany do wstępnego wypełnienia formularza danymi podpisanej wiadomości.
    @return Renderuje stronę `ecdsa_verify.html` z formularzem do weryfikacji podpisu. Zwraca wynik weryfikacji w `ecdsa_verify_result.html`.
    """
    if message_id:
        # Pobranie wiadomości z bazy danych, jeśli podano `message_id`
        signed_message = get_object_or_404(SignedMessage, pk=message_id)
        initial_data = {
            'curve_p': signed_message.curve_p,
            'curve_a': signed_message.curve_a,
            'curve_b': signed_message.curve_b,
            'g_x': signed_message.g_x,
            'g_y': signed_message.g_y,
            'message': signed_message.message,
            'pubkey_x': signed_message.pubkey_x,
            'pubkey_y': signed_message.pubkey_y,
            'r': signed_message.r,
            's': signed_message.s,
        }
        form = EcdsaVerifyForm(initial=initial_data)
    else:
        form = EcdsaVerifyForm()

    if request.method == 'POST':
        form = EcdsaVerifyForm(request.POST)
        if form.is_valid():
            # Pobranie danych z formularza
            curve_p = form.cleaned_data['curve_p']
            curve_a = form.cleaned_data['curve_a']
            curve_b = form.cleaned_data['curve_b']
            g_x = form.cleaned_data['g_x']
            g_y = form.cleaned_data['g_y']
            message = form.cleaned_data['message']
            pubkey_x = form.cleaned_data['pubkey_x']
            pubkey_y = form.cleaned_data['pubkey_y']
            r = form.cleaned_data['r']
            s = form.cleaned_data['s']


            # Walidacja parametrów krzywej
            is_valid_curve, validation_error = validate_curve_parameters(curve_p, curve_a, curve_b)
            if not is_valid_curve:
                messages.error(request, validation_error)

            # Obliczenie rzędu punktu bazowego
            G = Point(g_x, g_y, False)
            curve_n = get_point_order(G, curve_p, curve_a)

            # Sprawdzenie, czy rząd punktu bazowego jest liczbą pierwszą
            if not is_prime(curve_n):
                messages.error(request, f"Rząd punktu bazowego ({curve_n}) nie jest liczbą pierwszą.")
            # Walidacja punktu bazowego
            if not is_point_on_curve(g_x, g_y, curve_a, curve_b, curve_p):
                messages.error(request, f"Punkt bazowy ({g_x}, {g_y}) nie leży na krzywej.")
            # Walidacja klucza publicznego
            if not is_point_on_curve(pubkey_x, pubkey_y, curve_a, curve_b, curve_p):
                messages.error(request, f"Klucz publiczny ({pubkey_x}, {pubkey_y}) nie leży na krzywej.")
            else:
                # Hashowanie wiadomości
                hash_msg = hash_message(message)

                # Weryfikacja podpisu
                pubkey = Point(pubkey_x, pubkey_y, False)
                valid = ecdsa_verify(pubkey, hash_msg, r, s, curve_p, curve_a, curve_n, g_x, g_y)

                return render(request, 'eccApp/ecdsa_verify_result.html', {'valid': valid})

    return render(request, 'eccApp/ecdsa_verify.html', {'form': form})

def ecdsa_message_detail(request, message_id):
    """
    @brief Widok wyświetlający szczegóły podpisanej wiadomości.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @param message_id Identyfikator wiadomości w bazie danych, używany do pobrania szczegółów wiadomości.
    @return Renderuje stronę `ecdsa_message_detail.html` z szczegółowymi informacjami o wybranej wiadomości.
    """
    message = get_object_or_404(SignedMessage, pk=message_id)
    return render(request, 'eccApp/ecdsa_message_detail.html', {'message': message})

def ecdsa_delete_message(request, message_id):
    """
    @brief Widok usuwający podpisaną wiadomość z bazy danych.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @param message_id Identyfikator podpisanej wiadomości, która ma zostać usunięta.
    @return Przekierowuje użytkownika na stronę z listą podpisanych wiadomości.
    """
    # Pobranie wiadomości z bazy danych
    message = get_object_or_404(SignedMessage, pk=message_id)

    # Usunięcie wiadomości
    message.delete()

    # Przekierowanie do strony z listą wiadomości
    return redirect('ecdsa_messages')




# Algorytm ElGamala

def elgamal_page(request):
    """
    @brief Widok wyświetlający stronę główną algorytmu ElGamala w aplikacji.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @return Renderuje stronę `elgamal_page.html`.
    """
    return render(request, 'eccApp/elgamal_page.html')

def elgamal_encrypt_view(request, key_id=None):
    """
    @brief Widok obsługujący proces szyfrowania wiadomości za pomocą algorytmu ElGamala na krzywej eliptycznej.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @param key_id (opcjonalny) Identyfikator użytkownika w bazie danych używany do wstępnego wypełnienia formularza.
    @return Renderuje stronę `elgamal_encrypt.html` z formularzem do wypełnienia.
    """
    # Wypełnienie formularza danymi użytkownika, jeśli podano `key_id`
    if key_id:
        key = get_object_or_404(UserKeys, pk=key_id)
        initial_data = {
            'receiver': key.username,
            'curve_p': key.curve_p,
            'curve_a': key.curve_a,
            'curve_b': key.curve_b,
            'g_x': key.g_x,
            'g_y': key.g_y,
            'pubkey_x': key.pubkey_x,
            'pubkey_y': key.pubkey_y,
        }
        form = ElGamalEncryptForm(initial=initial_data)
    else:
        form = ElGamalEncryptForm()

    if request.method == 'POST':
        form = ElGamalEncryptForm(request.POST)
        if form.is_valid():
            # Pobranie danych z formularza
            receiver = form.cleaned_data['receiver']
            curve_p = form.cleaned_data['curve_p']
            curve_a = form.cleaned_data['curve_a']
            curve_b = form.cleaned_data['curve_b']
            g_x = form.cleaned_data['g_x']
            g_y = form.cleaned_data['g_y']

            # Tworzenie punktów
            G = Point(g_x, g_y, False)

            pubkey_x = form.cleaned_data['pubkey_x']
            pubkey_y = form.cleaned_data['pubkey_y']
            pubkey = Point(pubkey_x, pubkey_y, False)

            message_x = form.cleaned_data['message_x']
            message_y = form.cleaned_data['message_y']
            P = Point(message_x, message_y, False)

            # Walidacja parametrów krzywej
            is_valid_curve, validation_error = validate_curve_parameters(curve_p, curve_a, curve_b)
            if not is_valid_curve:
                messages.error(request, validation_error)
            # Walidacja punktu bazowego
            elif not is_point_on_curve(g_x, g_y, curve_a, curve_b, curve_p):
                messages.error(request, f"Punkt bazowy ({g_x}, {g_y}) nie leży na krzywej.")
            # Walidacja klucza publicznego
            elif not is_point_on_curve(pubkey_x, pubkey_y, curve_a, curve_b, curve_p):
                messages.error(request, f"Klucz publiczny ({pubkey_x}, {pubkey_y}) nie leży na krzywej.")
            # Walidacja wiadomości jako punktu
            elif not is_point_on_curve(message_x, message_y, curve_a, curve_b, curve_p):
                messages.error(request, f"Wiadomość w postaci punktu ({message_x}, {message_y}) nie leży na krzywej.")
            else:
                # Szyfrowanie wiadomości
                try:
                    C1, C2 = elgamal_encrypt(pubkey, P, G, curve_a, curve_p)

                    # Zapisanie zaszyfrowanej wiadomości w bazie danych
                    encrypted_message = EncryptedMessage(
                        receiver=receiver,
                        curve_a=curve_a,
                        curve_b=curve_b,
                        curve_p=curve_p,
                        g_x=g_x,
                        g_y=g_y,
                        pubkey_x=pubkey_x,
                        pubkey_y=pubkey_y,
                        message_x=message_x,
                        message_y=message_y,
                        c1_x=C1.x,
                        c1_y=C1.y,
                        c2_x=C2.x,
                        c2_y=C2.y
                    )
                    encrypted_message.save()
                    return redirect('elgamal_messages')
                except Exception as e:
                    messages.error(request, f"Wystąpił błąd podczas szyfrowania: {e}")

    return render(request, 'eccApp/elgamal_encrypt.html', {'form': form})

def elgamal_decrypt_view(request, message_id=None):
    """
    @brief Widok obsługujący proces odszyfrowania wiadomości za pomocą algorytmu ElGamala.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @param message_id (opcjonalny) Identyfikator wiadomości w bazie danych, używany do wstępnego wypełnienia formularza danymi zaszyfrowanej wiadomości.
    @return Renderuje stronę `elgamal_decrypt.html` z formularzem do odszyfrowania wiadomości. W przypadku powodzenia zwraca wynik odszyfrowania w `elgamal_decrypt_result.html`.
    """
    if message_id:
        # Pobranie wiadomości z bazy danych, jeśli podano `message_id`
        encrypted_message = get_object_or_404(EncryptedMessage, pk=message_id)
        initial_data = {
            'receiver': encrypted_message.receiver,
            'curve_p': encrypted_message.curve_p,
            'curve_a': encrypted_message.curve_a,
            'curve_b': encrypted_message.curve_b,
            'g_x': encrypted_message.g_x,
            'g_y': encrypted_message.g_y,
            'c1_x': encrypted_message.c1_x,
            'c1_y': encrypted_message.c1_y,
            'c2_x': encrypted_message.c2_x,
            'c2_y': encrypted_message.c2_y,
        }
        form = ElGamalDecryptForm(initial=initial_data)
    else:
        form = ElGamalDecryptForm()

    if request.method == 'POST':
        form = ElGamalDecryptForm(request.POST)
        if form.is_valid():
            # Pobranie danych z formularza
            receiver = form.cleaned_data['receiver']
            curve_p = form.cleaned_data['curve_p']
            curve_a = form.cleaned_data['curve_a']
            curve_b = form.cleaned_data['curve_b']
            g_x = form.cleaned_data['g_x']
            g_y = form.cleaned_data['g_y']
            privkey = form.cleaned_data['privkey']
            c1_x = form.cleaned_data['c1_x']
            c1_y = form.cleaned_data['c1_y']
            c2_x = form.cleaned_data['c2_x']
            c2_y = form.cleaned_data['c2_y']

            # Tworzenie punktów
            G = Point(g_x, g_y, False)
            C1 = Point(c1_x, c1_y, False)
            C2 = Point(c2_x, c2_y, False)

            # Walidacja parametrów krzywej
            is_valid_curve, validation_error = validate_curve_parameters(curve_p, curve_a, curve_b)
            if not is_valid_curve:
                messages.error(request, validation_error)
            # Walidacja klucza prywatnego
            elif privkey < 1:
                messages.error(request, f"Klucz prywatny nie może być mniejszy od 1.")
            # Walidacja punktu bazowego
            elif not is_point_on_curve(g_x, g_y, curve_a, curve_b, curve_p):
                messages.error(request, f"Punkt bazowy ({g_x}, {g_y}) nie leży na krzywej.")
            # Walidacja pierwszego punktu szyfrogramu
            elif not is_point_on_curve(c1_x, c1_y, curve_a, curve_b, curve_p):
                messages.error(request, f"Punkt szyfrogramu C1 ({c1_x}, {c1_y}) nie leży na krzywej.")
            # Walidacja drugiego punktu szyfrogramu
            elif not is_point_on_curve(c2_x, c2_y, curve_a, curve_b, curve_p):
                messages.error(request, f"Punkt szyfrogramu C2 ({c2_x}, {c2_y}) nie leży na krzywej.")
            else:
                # Odszyfrowanie wiadomości
                try:
                    decrypted_message = elgamal_decrypt(privkey, C1, C2, curve_a, curve_p)

                    # Wyświetlenie wyniku odszyfrowania
                    return render(request, 'eccApp/elgamal_decrypt_result.html', {'decrypted_message': decrypted_message})
                except Exception as e:
                    messages.error(request, f"Wystąpił błąd podczas odszyfrowania: {e}")

    return render(request, 'eccApp/elgamal_decrypt.html', {'form': form})

def elgamal_messages(request):
    """
    @brief Widok wyświetlający listę wszystkich wiadomości zaszyfrowanych za pomocą algorytmu ElGamala.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @return Renderuje stronę `elgamal_messages.html` z listą wszystkich zaszyfrowanych wiadomości przechowywanych w bazie danych.
    """
    messages = EncryptedMessage.objects.all()
    return render(request, 'eccApp/elgamal_messages.html', {'messages': messages})

def elgamal_message_detail(request, message_id):
    """
    @brief Widok wyświetlający szczegóły pojedynczej zaszyfrowanej wiadomości.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @param message_id Identyfikator wiadomości w bazie danych, używany do pobrania szczegółów wiadomości.
    @return Renderuje stronę `elgamal_message_detail.html` z informacjami o wybranej wiadomości.
    """
    message = get_object_or_404(EncryptedMessage, id=message_id)
    return render(request, 'eccApp/elgamal_message_detail.html', {'message': message})

def elgamal_delete_message(request, message_id):
    """
    @brief Widok usuwający wybraną zaszyfrowaną wiadomość z bazy danych.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @param message_id Identyfikator wiadomości w bazie danych, używany do usunięcia wiadomości.
    @return Przekierowuje użytkownika na stronę z listą wszystkich wiadomości.
    """
    # Pobranie wiadomości z bazy danych
    message = get_object_or_404(EncryptedMessage, pk=message_id)

    # Usunięcie wiadomości
    message.delete()

    # Przekierowanie do listy wiadomości
    return redirect('elgamal_messages')




# Część związana z danymi użytkownika

def generate_keys_view(request):
    """
    @brief Widok odpowiedzialny za generowanie pary kluczy (prywatnego i publicznego) dla użytkownika aplikacji.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @return Renderuje stronę `generate_keys.html` z formularzem umożliwiającym wygenerowanie kluczy.
    """
    if request.method == 'POST':
        form = KeysGenerationForm(request.POST)

        # Losowanie parametrów krzywej
        if "draw_parameters" in request.POST:
            curve_p, curve_a, curve_b, g_x, g_y = draw_valid_curve_and_point()
            curve_n = count_points_on_curve(curve_a, curve_b, curve_p)

            # Wypełnienie formularza wylosowanymi parametrami
            form = KeysGenerationForm(initial={
                'curve_p': curve_p,
                'curve_a': curve_a,
                'curve_b': curve_b,
                'curve_n': curve_n,
                'g_x': g_x,
                'g_y': g_y,
            })

        # Generowanie kluczy
        elif "generate_keys" in request.POST:
            if form.is_valid():
                # Pobranie danych z formularza
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                curve_p = form.cleaned_data['curve_p']
                curve_a = form.cleaned_data['curve_a']
                curve_b = form.cleaned_data['curve_b']
                g_x = form.cleaned_data['g_x']
                g_y = form.cleaned_data['g_y']

                # Walidacja parametrów krzywej
                is_valid_curve, validation_error = validate_curve_parameters(curve_p, curve_a, curve_b)
                if not is_valid_curve:
                    messages.error(request, validation_error)
                # Walidacja punktu bazowego
                elif not is_point_on_curve(g_x, g_y, curve_a, curve_b, curve_p):
                    messages.error(request, f"Punkt bazowy ({g_x}, {g_y}) nie leży na krzywej.")
                else:
                    curve_n = count_points_on_curve(curve_a, curve_b, curve_p)

                    try:
                        # Sprawdzenie, czy użytkownik istnieje
                        UserKeys.objects.get(username=username)
                        messages.error(request, f"Użytkownik '{username}' już istnieje.")
                    except UserKeys.DoesNotExist:
                        # Generowanie kluczy
                        privkey, pubkey = generate_key_pair(curve_p, curve_a, curve_n, g_x, g_y)

                        # Haszowanie hasła
                        hashed_password = make_password(password)

                        # Zapisanie kluczy i parametrów w bazie danych
                        user_key = UserKeys(
                            username=username,
                            hashed_password=hashed_password,
                            curve_p=curve_p,
                            curve_a=curve_a,
                            curve_b=curve_b,
                            curve_n=curve_n,
                            g_x=g_x,
                            g_y=g_y,
                            privkey=privkey,
                            pubkey_x=pubkey.x,
                            pubkey_y=pubkey.y,
                        )
                        user_key.save()

                        # Przekierowanie po sukcesie
                        return redirect('users')
    else:
        # Domyślnie puste pola formularza
        form = KeysGenerationForm()

    return render(request, 'eccApp/generate_keys.html', {'form': form})

def change_user_parameters(request, key_id):
    """
    @brief Widok odpowiedzialny za zmianę danych użytkownika aplikacji.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @param key_id Identyfikator użytkownika, którego dane mają zostać zmienione.
    @return Renderuje stronę `generate_keys.html` z formularzem umożliwiającym zmianę danych i wygenerowanie nowych kluczy.
    """
    user = get_object_or_404(UserKeys, pk=key_id)

    if request.method == 'POST':
        form = UpdateUserParametersForm(request.POST)

        # Losowanie parametrów krzywej
        if "draw_parameters" in request.POST:
            curve_p, curve_a, curve_b, g_x, g_y = draw_valid_curve_and_point()
            curve_n = count_points_on_curve(curve_a, curve_b, curve_p)

            # Wypełnienie formularza wylosowanymi parametrami
            initial_data = {
                'username': user.username,
                'curve_p': curve_p,
                'curve_a': curve_a,
                'curve_b': curve_b,
                'curve_n': curve_n,
                'g_x': g_x,
                'g_y': g_y,
            }
            form = UpdateUserParametersForm(initial=initial_data)

        # Generowanie kluczy
        elif "generate_keys" in request.POST:
            if form.is_valid():
                # Pobranie danych z formularza
                username = form.cleaned_data['username']
                old_password = form.cleaned_data['old_password']
                new_password = form.cleaned_data['new_password']
                curve_p = form.cleaned_data['curve_p']
                curve_a = form.cleaned_data['curve_a']
                curve_b = form.cleaned_data['curve_b']
                g_x = form.cleaned_data['g_x']
                g_y = form.cleaned_data['g_y']

                # Sprawdzenie poprawności starego hasła
                if not check_password(old_password, user.hashed_password):
                    messages.error(request, "Stare hasło jest nieprawidłowe.")
                else:
                    # Walidacja parametrów krzywej
                    is_valid_curve, validation_error = validate_curve_parameters(curve_p, curve_a, curve_b)
                    if not is_valid_curve:
                        messages.error(request, validation_error)
                    # Walidacja punktu bazowego
                    elif not is_point_on_curve(g_x, g_y, curve_a, curve_b, curve_p):
                        messages.error(request, f"Punkt bazowy ({g_x}, {g_y}) nie leży na krzywej.")
                    else:
                        # Sprawdzenie unikalności nazwy użytkownika
                        if username != user.username:
                            try:
                                UserKeys.objects.get(username=username)
                                messages.error(request, f"Użytkownik '{username}' już istnieje.")
                                return render(request, 'eccApp/generate_keys.html', {
                                    'form': form,
                                    'update_mode': True,
                                    'key_id': key_id
                                })
                            except UserKeys.DoesNotExist:
                                pass  # Nazwa użytkownika jest unikalna

                        # Obliczanie rzędu krzywej i generowanie kluczy
                        curve_n = count_points_on_curve(curve_a, curve_b, curve_p)
                        privkey, pubkey = generate_key_pair(curve_p, curve_a, curve_n, g_x, g_y)

                        # Aktualizacja danych użytkownika
                        user.username = username
                        user.hashed_password = make_password(new_password)
                        user.curve_p = curve_p
                        user.curve_a = curve_a
                        user.curve_b = curve_b
                        user.curve_n = curve_n
                        user.g_x = g_x
                        user.g_y = g_y
                        user.privkey = privkey
                        user.pubkey_x = pubkey.x
                        user.pubkey_y = pubkey.y

                        user.save()
                        return redirect('user_detail', key_id=key_id)

    else:
        initial_data = {
            'username': user.username,
            'curve_p': user.curve_p,
            'curve_a': user.curve_a,
            'curve_b': user.curve_b,
            'g_x': user.g_x,
            'g_y': user.g_y,
        }
        form = UpdateUserParametersForm(initial=initial_data)

    return render(request, 'eccApp/generate_keys.html', {
        'form': form,
        'update_mode': True,
        'key_id': key_id
    })

def users_view(request):
    """
    @brief Widok wyświetlający listy użytkowników w aplikacji.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @return Renderuje stronę `users.html`, wyświetlającą wszystkich użytkowników aplikacji.
    """
    keys = UserKeys.objects.all()
    return render(request, 'eccApp/users.html', {'keys': keys})

def user_detail_view(request, key_id):
    """
    @brief Widok wyświatlający szczegóły danego użytkownika.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @param key_id Identyfikator użytkownika, którego szczegóły mają zostać wyświetlone.
    @return Renderuje stronę `user_detail.html` z danymi użytkownika.
    """
    key = get_object_or_404(UserKeys, pk=key_id)
    form = PasswordVerificationForm()
    privkey_revealed = False

    if request.method == 'POST':
        form = PasswordVerificationForm(request.POST)
        if form.is_valid():
            entered_password = form.cleaned_data['password']
            # Sprawdzenie, czy podane hasło jest poprawne
            if check_password(entered_password, key.hashed_password):
                privkey_revealed = True

    return render(request, 'eccApp/user_detail.html', {
        'key': key,
        'privkey_revealed': privkey_revealed,
        'form': form,
    })

def delete_user_view(request, key_id):
    """
    @brief Widok umożliwiający usunięcie użytkownika.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @param key_id Ientyfikator użytkownika, który ma zostać usunięty.
    @return Renderuje stronę `delete_user.html`.
    """
    user_key = get_object_or_404(UserKeys, pk=key_id)
    form = PasswordVerificationForm()

    if request.method == 'POST':
        form = PasswordVerificationForm(request.POST)
        if form.is_valid():
            entered_password = form.cleaned_data['password']
            # Sprawdzenie, czy podane hasło jest poprawne
            if check_password(entered_password, user_key.hashed_password):
                # Usunięcie użytkownika
                user_key.delete()
                return redirect('users')
            else:
                # Wyświetlenie błędu, jeśli hasło jest nieprawidłowe
                messages.error(request, "Nieprawidłowe hasło.")

    return render(request, 'eccApp/delete_user.html', {
        'key': user_key,
        'form': form,
    })




# Algorytm faktoryzacji Lenstry

def lenstra_page(request):
    """
    @brief Widok wyświetlający stronę główną algorytmu faktoryzacji Lenstry.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @return Renderuje stronę `lenstra_page.html`.
    """
    return render(request, 'eccApp/lenstra_page.html')

def lenstra_factorize(request):
    """
    @brief Widok umożliwiający faktoryzację liczby za pomocą algorytmu Lenstry.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @return Renderuje stronę `lenstra_factorize.html` z formularzem, który umożliwia wprowadzenie liczby do faktoryzacji. Wynik jest wyświetlany na stronie `lenstra_result.html`.
    """
    if request.method == 'POST':
        form = LenstraForm(request.POST)
        if form.is_valid():
            number_to_factorize = form.cleaned_data['number_to_factorize']

            # Sprawdzenie, czy liczba jest dodatnia
            if number_to_factorize <= 0:
                messages.error(request, "Podana liczba musi być dodatnia.")
                return render(request, 'eccApp/lenstra_factorize.html', {'form': form})

            try:
                # Przeprowadzenie faktoryzacji
                factor, attempts = ecm_factorization(number_to_factorize)
                result = f"Znaleziono dzielnik {factor} po {attempts} próbach (liczba losowanych krzywych)"
            except Exception as e:
                result = f"Błąd podczas faktoryzacji: {str(e)}"

            return render(request, 'eccApp/lenstra_result.html', {'result': result})
    else:
        form = LenstraForm()
    return render(request, 'eccApp/lenstra_factorize.html', {'form': form})





# Operacje na krzywych

def curve_operations(request):
    """
    @brief Widok główny dla operacji na krzywych eliptycznych.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @return Renderuje stronę `curve_operations.html` z listą dostępnych operacji.
    """
    return render(request, 'eccApp/curve_operations.html')

def add_points(request):
    """
    @brief Widok obsługujący dodawanie dwóch punktów na krzywej eliptycznej.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @return Renderuje stronę `add_points.html` z formularzem do wprowadzenia danych oraz wynikiem dodawania.
    """
    result_point = None
    point_p = None
    point_q = None
    plot_url = None
    error_message = None

    if request.method == 'POST':
        form = AddPointsForm(request.POST)
        if form.is_valid():
            # Pobranie danych z formularza
            curve_p = form.cleaned_data['curve_p']
            curve_a = form.cleaned_data['curve_a']
            curve_b = form.cleaned_data['curve_b']
            p_x = form.cleaned_data['p_x']
            p_y = form.cleaned_data['p_y']
            q_x = form.cleaned_data['q_x']
            q_y = form.cleaned_data['q_y']

            # Sprawdzenie poprawności parametrów krzywej
            is_valid, validation_error = validate_curve_parameters(curve_p, curve_a, curve_b)
            if not is_valid:
                error_message = validation_error
            else:
                # Tworzenie punktów P i Q
                point_p = Point(p_x, p_y, False)
                point_q = Point(q_x, q_y, False)

                # Sprawdzenie, czy punkty leżą na krzywej
                if not is_point_on_curve(p_x, p_y, curve_a, curve_b, curve_p):
                    error_message = f"Punkt P ({p_x}, {p_y}) nie leży na krzywej."
                elif not is_point_on_curve(q_x, q_y, curve_a, curve_b, curve_p):
                    error_message = f"Punkt Q ({q_x}, {q_y}) nie leży na krzywej."
                else:
                    # Obliczenie sumy punktów
                    result_point = elliptic_curve_add(point_p, point_q, curve_a, curve_p)
                    plot_url = plot_elliptic_curve_modulo(
                        curve_p, curve_a, curve_b, [point_p, point_q], result_point, operation_type="addition"
                    )
    else:
        form = AddPointsForm()

    return render(request, 'eccApp/add_points.html', {
        'form': form,
        'result': result_point,
        'point_p': point_p,
        'point_q': point_q,
        'plot_url': plot_url,
        'error_message': error_message,
    })

def multiply_point(request):
    """
    @brief Widok obsługujący obliczanie wielokrotności punktu na krzywej eliptycznej przez dany współczynnik.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @return Renderuje stronę `multiply_point.html` z formularzem do wprowadzenia danych oraz wynikiem mnożenia punktu.
    """
    result_point = None
    point_p = None
    multiplier = 1
    plot_url = None
    error_message = None

    if request.method == 'POST':
        form = MultiplyPointForm(request.POST)
        if form.is_valid():
            # Pobranie danych z formularza
            curve_p = form.cleaned_data['curve_p']
            curve_a = form.cleaned_data['curve_a']
            curve_b = form.cleaned_data['curve_b']
            p_x = form.cleaned_data['p_x']
            p_y = form.cleaned_data['p_y']
            multiplier = form.cleaned_data['multiplier']

            # Sprawdzenie poprawności parametrów krzywej
            is_valid_curve, validation_error = validate_curve_parameters(curve_p, curve_a, curve_b)
            if not is_valid_curve:
                error_message = validation_error
            else:
                # Tworzenie punktu P
                point_p = Point(p_x, p_y, False)

                # Sprawdzenie, czy punkt P leży na krzywej
                if not is_point_on_curve(p_x, p_y, curve_a, curve_b, curve_p):
                    error_message = f"Punkt P ({p_x}, {p_y}) nie leży na krzywej."
                elif multiplier <= 0:
                    error_message = f"Współczynnik k musi być dodatni."
                else:
                    # Obliczenie wielokrotności punktu
                    result_point = elliptic_curve_multiply(point_p, multiplier, curve_a, curve_p)
                    plot_url = plot_elliptic_curve_modulo(
                        curve_p, curve_a, curve_b, [point_p], result_point, operation_type="multiplication", multiplier=multiplier
                    )
    else:
        form = MultiplyPointForm()

    return render(request, 'eccApp/multiply_point.html', {
        'form': form,
        'result': result_point,
        'point_p': point_p,
        'multiplier': multiplier,
        'plot_url': plot_url,
        'error_message': error_message,
    })

def get_plot_for_multiple(request):
    """
    @brief Generuje wykres dla wyświetlania wielokrotności punktu na krzywej eliptycznej.
    @param request Żądanie HTTP z parametrami krzywej, punktu i współczynnika mnożenia.
    @return JsonResponse z adresem URL do wygenerowanego wykresu.
    """
    curve_p = int(request.GET.get('curve_p'))
    curve_a = int(request.GET.get('curve_a'))
    curve_b = int(request.GET.get('curve_b'))
    p_x = int(request.GET.get('p_x'))
    p_y = int(request.GET.get('p_y'))
    multiplier = int(request.GET.get('multiple'))

    point_p = Point(p_x, p_y, False)

    result_point = elliptic_curve_multiply(point_p, multiplier, curve_a, curve_p)

    plot_url = plot_elliptic_curve_modulo(
        curve_p, curve_a, curve_b, [point_p], result_point,
        operation_type="multiplication",
        multiplier=multiplier,
        show_all_curve_points=True
    )

    return JsonResponse({'plot_url': plot_url})

def show_multiples_of_point(request):
    """
    @brief widok wyświetlający wielokrotności punktu na krzywej eliptycznej.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @return Renderuje stronę `show_multiples_of_point.html` z formularzem oraz animacją wielokrotności punktu.
    """
    form = ShowMultiplesForm(request.POST or None)
    plot_url = None
    max_multiplier = 1
    error_message = None

    if request.method == 'POST' and form.is_valid():
        # Pobranie danych z formularza
        curve_p = form.cleaned_data['curve_p']
        curve_a = form.cleaned_data['curve_a']
        curve_b = form.cleaned_data['curve_b']
        p_x = form.cleaned_data['p_x']
        p_y = form.cleaned_data['p_y']

        # Tworzenie punktu P
        point_p = Point(p_x, p_y, False)

        # Sprawdzenie poprawności parametrów krzywej
        is_valid_curve, validation_error = validate_curve_parameters(curve_p, curve_a, curve_b)
        if not is_valid_curve:
            error_message = validation_error
        # Sprawdzenie, czy punkt P leży na krzywej
        elif not is_point_on_curve(p_x, p_y, curve_a, curve_b, curve_p):
            error_message = f"Punkt P ({p_x}, {p_y}) nie leży na krzywej."
        else:
            # Obliczenie liczby wyświetlanych wielokrotności (2 razy liczba punktów na krzywej)
            max_multiplier = 2 * get_point_order(point_p, curve_p, curve_a)

            # Generowanie wielokrotności punktu P
            multiples = [point_p]
            current_point = point_p
            for _ in range(1, max_multiplier):
                current_point = elliptic_curve_add(current_point, point_p, curve_a, curve_p)
                multiples.append(current_point)

            # Generowanie wykresu dla wielokrotności punktu P
            plot_url = plot_elliptic_curve_modulo(
                curve_p, curve_a, curve_b, multiples, None, operation_type="multiplication", show_all_curve_points=True
            )

    return render(request, 'eccApp/show_multiples_of_point.html', {
        'form': form,
        'plot_url': plot_url,
        'max_multiplier': max_multiplier,
        'curve_p': form.cleaned_data['curve_p'] if form.is_valid() else None,
        'curve_a': form.cleaned_data['curve_a'] if form.is_valid() else None,
        'curve_b': form.cleaned_data['curve_b'] if form.is_valid() else None,
        'point_p': Point(
            form.cleaned_data['p_x'], form.cleaned_data['p_y'], False
        ) if form.is_valid() else None,
        'error_message': error_message,
    })

def show_curve_graph(request):
    """
    @brief Widok wyświetlający wykres punktów leżących na krzywej eliptycznej.
    @param request Żądanie HTTP wysyłane przez użytkownika.
    @return Renderuje stronę `show_curve_graph.html` z formularzem oraz wykresem punktów na krzywej.
    """
    points_on_curve = []
    plot_url = None
    error_message = None
    form = ShowCurveGraphForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        # Pobranie danych z formularza
        curve_a = form.cleaned_data['curve_a']
        curve_b = form.cleaned_data['curve_b']
        curve_p = form.cleaned_data['curve_p']

        # Sprawdzenie poprawności parametrów krzywej
        is_valid_curve, validation_error = validate_curve_parameters(curve_p, curve_a, curve_b)
        if not is_valid_curve:
            error_message = validation_error
        else:
            # Wyszukiwanie punktów na krzywej
            for x in range(curve_p):
                for y in range(curve_p):
                    if (y**2) % curve_p == (x**3 + curve_a * x + curve_b) % curve_p:
                        points_on_curve.append((x, y))

            plot_url = plot_points_on_curve(curve_p, curve_a, curve_b, points_on_curve)

    return render(request, 'eccApp/show_curve_graph.html', {
        'form': form,
        'points_on_curve': points_on_curve,
        'plot_url': plot_url,
        'error_message': error_message,
    })
