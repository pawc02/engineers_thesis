from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import EcdsaSignForm, EcdsaVerifyForm, ElGamalEncryptForm, ElGamalDecryptForm, KeysGenerationForm, PasswordVerificationForm, LenstraForm
from .models import SignedMessage, EncryptedMessage, UserKeys
from .appModule import generate_key_pair, hash_message, ecdsa_sign, ecdsa_verify, Point, elgamal_encrypt, elgamal_decrypt, ecm_factorization
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages

def home_page(request):
    return render(request, 'eccApp/home_page.html')


# ECDSA

def ecdsa_page(request):
    return render(request, 'eccApp/ecdsa_page.html')

def ecdsa_sign_view(request, key_id=None):
    initial_data = {}

    # Wstępnie wypełniamy formularz danymi użytkownika, jeśli podano `key_id`
    if key_id:
        key = get_object_or_404(UserKeys, pk=key_id)
        initial_data = {
            'username': key.username,
            'curve_p': key.curve_p,
            'curve_a': key.curve_a,
            'curve_b': key.curve_b,
            'curve_n': key.curve_n,
            'g_x': key.g_x,
            'g_y': key.g_y
        }

    if request.method == 'POST':
        form = EcdsaSignForm(request.POST)
        if form.is_valid():
            # Pobierz dane z formularza
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            message = form.cleaned_data['message']
            curve_p = form.cleaned_data['curve_p']
            curve_a = form.cleaned_data['curve_a']
            curve_b = form.cleaned_data['curve_b']
            curve_n = form.cleaned_data['curve_n']
            g_x = form.cleaned_data['g_x']
            g_y = form.cleaned_data['g_y']

            try:
                # Wyszukaj użytkownika w bazie danych
                user = UserKeys.objects.get(username=username)

                # Sprawdź hasło
                if check_password(password, user.hashed_password):
                    # Użytkownik i hasło są poprawne
                    # Pobierz klucz prywatny z bazy danych
                    privkey = user.privkey

                    # Zhashuj wiadomość
                    hash_msg = hash_message(message)

                    # Podpisz wiadomość
                    r, s = ecdsa_sign(privkey, hash_msg, curve_p, curve_a, curve_n, g_x, g_y)

                    # Zapisz podpisaną wiadomość do bazy
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

                    # Przekieruj do listy podpisanych wiadomości
                    return redirect(reverse('ecdsa_messages'))
                else:
                    # Błędne hasło
                    messages.error(request, 'Błędne hasło.')
            except UserKeys.DoesNotExist:
                # Użytkownik nie istnieje
                messages.error(request, 'Użytkownik nie istnieje.')
    else:
        form = EcdsaSignForm(initial=initial_data)

    return render(request, 'eccApp/ecdsa_sign.html', {'form': form})

@never_cache  # Ten dekorator wyłącza cache dla tego widoku
def ecdsa_messages(request):
    messages = SignedMessage.objects.all()
    return render(request, 'eccApp/ecdsa_messages.html', {'messages': messages})

def ecdsa_verify_view(request, message_id=None):
    if message_id:
        # Pobierz wiadomość z bazy danych, aby wypełnić formularz
        signed_message = get_object_or_404(SignedMessage, pk=message_id)
        initial_data = {
            'curve_p': signed_message.curve_p,
            'curve_a': signed_message.curve_a,
            'curve_b': signed_message.curve_b,
            'curve_n': signed_message.curve_n,
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
            # Pobierz dane z formularza
            curve_p = form.cleaned_data['curve_p']
            curve_a = form.cleaned_data['curve_a']
            curve_b = form.cleaned_data['curve_b']
            curve_n = form.cleaned_data['curve_n']
            g_x = form.cleaned_data['g_x']
            g_y = form.cleaned_data['g_y']
            message = form.cleaned_data['message']
            pubkey_x = form.cleaned_data['pubkey_x']
            pubkey_y = form.cleaned_data['pubkey_y']
            r = form.cleaned_data['r']
            s = form.cleaned_data['s']

            # Zhashuj wiadomość
            hash_msg = hash_message(message)

            # Sprawdź podpis
            pubkey = Point(pubkey_x, pubkey_y, False)
            valid = ecdsa_verify(pubkey, hash_msg, r, s, curve_p, curve_a, curve_n, g_x, g_y)

            return render(request, 'eccApp/ecdsa_verify_result.html', {'valid': valid})
    return render(request, 'eccApp/ecdsa_verify.html', {'form': form})

def ecdsa_message_detail(request, message_id):
    message = get_object_or_404(SignedMessage, pk=message_id)
    return render(request, 'eccApp/ecdsa_message_detail.html', {'message': message})

def ecdsa_delete_message(request, message_id):
    # Pobierz wiadomość z bazy danych
    message = get_object_or_404(SignedMessage, pk=message_id)

    # Usuń wiadomość
    message.delete()

    # Przekieruj do strony z listą wiadomości
    return redirect('ecdsa_messages')




# El Gamal

def elgamal_page(request):
    return render(request, 'eccApp/elgamal_page.html')

def elgamal_encrypt_view(request, key_id=None):
    # Wstępnie wypełniamy formularz danymi użytkownika, jeśli podano `key_id`
    if key_id:
        key = get_object_or_404(UserKeys, pk=key_id)
        initial_data = {
            'receiver': key.username,
            'curve_p': key.curve_p,
            'curve_a': key.curve_a,
            'curve_b': key.curve_b,
            'curve_n': key.curve_n,
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
            # Pobierz dane z formularza
            receiver = form.cleaned_data['receiver']
            curve_p = form.cleaned_data['curve_p']
            curve_a = form.cleaned_data['curve_a']
            curve_b = form.cleaned_data['curve_b']
            curve_n = form.cleaned_data['curve_n']
            g_x = form.cleaned_data['g_x']
            g_y = form.cleaned_data['g_y']
            G = Point(g_x, g_y, False)

            pubkey_x = form.cleaned_data['pubkey_x']
            pubkey_y = form.cleaned_data['pubkey_y']
            pubkey = Point(pubkey_x, pubkey_y, False)

            message_x = form.cleaned_data['message_x']
            message_y = form.cleaned_data['message_y']
            P = Point(message_x, message_y, False)

            # Szyfruj wiadomość
            C1, C2 = elgamal_encrypt(pubkey, P, G, curve_a, curve_b, curve_p, curve_n)

            # Zapisz zaszyfrowaną wiadomość w bazie danych
            encrypted_message = EncryptedMessage(
                receiver=receiver,
                curve_a=curve_a,
                curve_b=curve_b,
                curve_p=curve_p,
                curve_n=curve_n,
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

    return render(request, 'eccApp/elgamal_encrypt.html', {'form': form})


def elgamal_decrypt_view(request, message_id=None):
    if message_id:
        # Pobieramy wiadomość z bazy danych
        encrypted_message = get_object_or_404(EncryptedMessage, pk=message_id)
        initial_data = {
            'receiver': encrypted_message.receiver,
            'curve_p': encrypted_message.curve_p,
            'curve_a': encrypted_message.curve_a,
            'curve_b': encrypted_message.curve_b,
            'curve_n': encrypted_message.curve_n,
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
            # Pobieramy dane z formularza
            receiver = form.cleaned_data['receiver']
            curve_p = form.cleaned_data['curve_p']
            curve_a = form.cleaned_data['curve_a']
            curve_b = form.cleaned_data['curve_b']
            curve_n = form.cleaned_data['curve_n']
            g_x = form.cleaned_data['g_x']
            g_y = form.cleaned_data['g_y']
            privkey = form.cleaned_data['privkey']
            c1_x = form.cleaned_data['c1_x']
            c1_y = form.cleaned_data['c1_y']
            c2_x = form.cleaned_data['c2_x']
            c2_y = form.cleaned_data['c2_y']

            # Odszyfruj wiadomość
            G = Point(g_x, g_y, False)
            C1 = Point(c1_x, c1_y, False)
            C2 = Point(c2_x, c2_y, False)
            decrypted_message = elgamal_decrypt(privkey, C1, C2, G, curve_a, curve_b, curve_p, curve_n)

            return render(request, 'eccApp/elgamal_decrypt_result.html', {'decrypted_message': decrypted_message})

    return render(request, 'eccApp/elgamal_decrypt.html', {'form': form})


def elgamal_messages(request):
    messages = EncryptedMessage.objects.all()
    return render(request, 'eccApp/elgamal_messages.html', {'messages': messages})

def elgamal_message_detail(request, message_id):
    message = get_object_or_404(EncryptedMessage, id=message_id)
    return render(request, 'eccApp/elgamal_message_detail.html', {'message': message})

def elgamal_delete_message(request, message_id):
    # Pobierz wiadomość z bazy danych
    message = get_object_or_404(EncryptedMessage, pk=message_id)

    # Usuń wiadomość
    message.delete()

    # Przekieruj do listy wiadomości
    return redirect('elgamal_messages')




# user's section

def generate_keys_view(request):
    if request.method == 'POST':
        form = KeysGenerationForm(request.POST)
        if form.is_valid():
            # Pobierz dane z formularza
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            curve_p = form.cleaned_data['curve_p']
            curve_a = form.cleaned_data['curve_a']
            curve_b = form.cleaned_data['curve_b']
            curve_n = form.cleaned_data['curve_n']
            g_x = form.cleaned_data['g_x']
            g_y = form.cleaned_data['g_y']

            # Generowanie kluczy
            privkey, pubkey = generate_key_pair(curve_p, curve_a, curve_n, g_x, g_y)

            # Haszowanie hasła
            hashed_password = make_password(password)

            # Zapisz klucze w bazie danych
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

            return redirect('users')
    else:
        form = KeysGenerationForm()
    return render(request, 'eccApp/generate_keys.html', {'form': form})

def users_view(request):
    keys = UserKeys.objects.all()
    return render(request, 'eccApp/users.html', {'keys': keys})

def user_detail_view(request, key_id):
    key = get_object_or_404(UserKeys, pk=key_id)
    form = PasswordVerificationForm()
    privkey_revealed = False

    if request.method == 'POST':
        form = PasswordVerificationForm(request.POST)
        if form.is_valid():
            entered_password = form.cleaned_data['password']
            # Sprawdź, czy podane hasło jest poprawne
            if check_password(entered_password, key.hashed_password):
                privkey_revealed = True

    return render(request, 'eccApp/user_detail.html', {
        'key': key,
        'privkey_revealed': privkey_revealed,
        'form': form,
    })

def delete_user_view(request, key_id):
    # Pobierz klucz użytkownika lub zwróć 404, jeśli nie istnieje
    user_key = get_object_or_404(UserKeys, pk=key_id)

    # Usuń klucz użytkownika
    user_key.delete()

    # Przekieruj do strony z listą użytkowników
    return redirect('users')




# Lenstra algorithm

def lenstra_page(request):
    return render(request, 'eccApp/lenstra_page.html')

def lenstra_factorize(request):
    if request.method == 'POST':
        form = LenstraForm(request.POST)
        if form.is_valid():
            number_to_factorize = form.cleaned_data['number_to_factorize']
            try:
                factor, attempts = ecm_factorization(number_to_factorize)
                result = f"Znaleziono dzielnik: {factor} po {attempts} próbach"
            except Exception as e:
                result = f"Błąd podczas faktoryzacji: {str(e)}"
            return render(request, 'eccApp/lenstra_result.html', {'result': result})
    else:
        form = LenstraForm()
    return render(request, 'eccApp/lenstra_factorize.html', {'form': form})