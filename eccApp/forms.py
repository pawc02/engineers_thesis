from django import forms

class EcdsaSignForm(forms.Form):
    username = forms.CharField(label='Nazwa użytkownika',max_length=100)
    password = forms.CharField(label='Hasło', widget=forms.PasswordInput)
    curve_p = forms.IntegerField(label='Liczba pierwsza p')
    curve_a = forms.IntegerField(label='Współczynnik a')
    curve_b = forms.IntegerField(label='Współczynnik b')
    g_x = forms.IntegerField(label='Współrzędna x')
    g_y = forms.IntegerField(label='Współrzędna y')
    message = forms.CharField(label='Wiadomość', widget=forms.Textarea)

class EcdsaVerifyForm(forms.Form):
    curve_p = forms.IntegerField(label='Liczba pierwsza p')
    curve_a = forms.IntegerField(label='Współczynnik a')
    curve_b = forms.IntegerField(label='Współczynnik b')
    g_x = forms.IntegerField(label='Współrzędna x')
    g_y = forms.IntegerField(label='Współrzędna y')
    pubkey_x = forms.IntegerField(label='Współrzędna x')
    pubkey_y = forms.IntegerField(label='Współrzędna y')
    r = forms.IntegerField(label='Składowa r')
    s = forms.IntegerField(label='Składowa s')
    message = forms.CharField(label='Wiadomość', widget=forms.Textarea)

class ElGamalEncryptForm(forms.Form):
    receiver = forms.CharField(label='Odbiorca', max_length=100)
    curve_p = forms.IntegerField(label='Liczba pierwsza p')
    curve_a = forms.IntegerField(label='Współczynnik a')
    curve_b = forms.IntegerField(label='Współczynnik b')
    g_x = forms.IntegerField(label='Współrzędna x')
    g_y = forms.IntegerField(label='Współrzędna y')
    pubkey_x = forms.IntegerField(label='Współrzędna x')
    pubkey_y = forms.IntegerField(label='Współrzędna y')
    message_x = forms.IntegerField(label='Współrzędna x')
    message_y = forms.IntegerField(label='Współrzędna y')

class ElGamalDecryptForm(forms.Form):
    receiver = forms.CharField(label='Odbiorca', max_length=100)
    privkey = forms.IntegerField(label='Klucz prywatny odbiorcy')
    curve_p = forms.IntegerField(label='Liczba pierwsza p')
    curve_a = forms.IntegerField(label='Współczynnik a')
    curve_b = forms.IntegerField(label='Współczynnik b')
    g_x = forms.IntegerField(label='Współrzędna x')
    g_y = forms.IntegerField(label='Współrzędna y')
    c1_x = forms.IntegerField(label='Współrzędna x')
    c1_y = forms.IntegerField(label='Współrzędna y')
    c2_x = forms.IntegerField(label='Współrzędna x')
    c2_y = forms.IntegerField(label='Współrzędna y')

class KeysGenerationForm(forms.Form):
    username = forms.CharField(label='Nazwa użytkownika', max_length=100)
    password = forms.CharField(label='Hasło', widget=forms.PasswordInput)
    curve_p = forms.IntegerField(label='Liczba pierwsza p')
    curve_a = forms.IntegerField(label='Współczynnik a')
    curve_b = forms.IntegerField(label='Współczynnik b')
    g_x = forms.IntegerField(label='Współrzędna x')
    g_y = forms.IntegerField(label='Współrzędna y')

class UpdateUserParametersForm(forms.Form):
    username = forms.CharField(label='Nazwa użytkownika', max_length=100)
    old_password = forms.CharField(label='Stare hasło', widget=forms.PasswordInput)
    new_password = forms.CharField(label='Nowe hasło', widget=forms.PasswordInput, required=False)
    curve_p = forms.IntegerField(label='Liczba pierwsza p')
    curve_a = forms.IntegerField(label='Współczynnik a')
    curve_b = forms.IntegerField(label='Współczynnik b')
    g_x = forms.IntegerField(label='Współrzędna x')
    g_y = forms.IntegerField(label='Współrzędna y')

class PasswordVerificationForm(forms.Form):
    password = forms.CharField(label='Hasło', widget=forms.PasswordInput)

class LenstraForm(forms.Form):
    number_to_factorize = forms.IntegerField(label='Liczba do faktoryzacji')

class AddPointsForm(forms.Form):
    curve_a = forms.IntegerField(label='Współczynnik a')
    curve_b = forms.IntegerField(label='Współczynnik b')
    curve_p = forms.IntegerField(label='Liczba pierwsza p')
    p_x = forms.IntegerField(label='Współrzędna x')
    p_y = forms.IntegerField(label='Współrzędna y')
    q_x = forms.IntegerField(label='Współrzędna x')
    q_y = forms.IntegerField(label='Współrzędna y')

class MultiplyPointForm(forms.Form):
    curve_a = forms.IntegerField(label='Współczynnik a')
    curve_b = forms.IntegerField(label='Współczynnik b')
    curve_p = forms.IntegerField(label='Liczba pierwsza p')
    p_x = forms.IntegerField(label='Współrzędna x')
    p_y = forms.IntegerField(label='Współrzędna y')
    multiplier = forms.IntegerField(label='k')

class ShowMultiplesForm(forms.Form):
    curve_a = forms.IntegerField(label='Współczynnik a')
    curve_b = forms.IntegerField(label='Współczynnik b')
    curve_p = forms.IntegerField(label='Liczba pierwsza p')
    p_x = forms.IntegerField(label='Współrzędna x')
    p_y = forms.IntegerField(label='Współrzędna y')

class ShowCurveGraphForm(forms.Form):
    curve_a = forms.IntegerField(label='Współczynnik a')
    curve_b = forms.IntegerField(label='Współczynnik b')
    curve_p = forms.IntegerField(label='Liczba pierwsza p')
