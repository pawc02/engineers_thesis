from django import forms

class EcdsaSignForm(forms.Form):
    username = forms.CharField(label='Username',max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    curve_p = forms.IntegerField(label='Curve P')
    curve_a = forms.IntegerField(label='Curve A')
    curve_b = forms.IntegerField(label='Curve B')
    curve_n = forms.IntegerField(label='Curve N')
    g_x = forms.IntegerField(label='Base Point Gx')
    g_y = forms.IntegerField(label='Base Point Gy')
    message = forms.CharField(label='Message', widget=forms.Textarea)

class EcdsaVerifyForm(forms.Form):
    curve_p = forms.IntegerField(label='Curve P')
    curve_a = forms.IntegerField(label='Curve A')
    curve_b = forms.IntegerField(label='Curve B')
    curve_n = forms.IntegerField(label='Curve N')
    g_x = forms.IntegerField(label='Base Point Gx')
    g_y = forms.IntegerField(label='Base Point Gy')
    message = forms.CharField(label='Message', widget=forms.Textarea)
    pubkey_x = forms.IntegerField(label='Public Key X')
    pubkey_y = forms.IntegerField(label='Public Key Y')
    r = forms.IntegerField(label='Signature r')
    s = forms.IntegerField(label='Signature s')

class ElGamalEncryptForm(forms.Form):
    receiver = forms.CharField(label='Receiver', max_length=100)
    curve_p = forms.IntegerField(label='Prime Field P')
    curve_a = forms.IntegerField(label='Elliptic Curve A')
    curve_b = forms.IntegerField(label='Elliptic Curve B')
    curve_n = forms.IntegerField(label='Order of Curve N')

    g_x = forms.IntegerField(label='Base Point G X coordinate')
    g_y = forms.IntegerField(label='Base Point G Y coordinate')

    pubkey_x = forms.IntegerField(label='Public Key X coordinate')
    pubkey_y = forms.IntegerField(label='Public Key Y coordinate')

    message_x = forms.IntegerField(label='Message X coordinate')
    message_y = forms.IntegerField(label='Message Y coordinate')

class ElGamalDecryptForm(forms.Form):
    receiver = forms.CharField(label='Receiver', max_length=100)
    curve_p = forms.IntegerField(label='Prime Field P')
    curve_a = forms.IntegerField(label='Elliptic Curve A')
    curve_b = forms.IntegerField(label='Elliptic Curve B')
    curve_n = forms.IntegerField(label='Order of Curve N')

    g_x = forms.IntegerField(label='Base Point G X coordinate')
    g_y = forms.IntegerField(label='Base Point G Y coordinate')

    privkey = forms.IntegerField(label='Private Key')

    c1_x = forms.IntegerField(label='Ciphertext C1 X coordinate')
    c1_y = forms.IntegerField(label='Ciphertext C1 Y coordinate')
    c2_x = forms.IntegerField(label='Ciphertext C2 X coordinate')
    c2_y = forms.IntegerField(label='Ciphertext C2 Y coordinate')

class KeysGenerationForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    curve_p = forms.IntegerField(label='Prime Field P')
    curve_a = forms.IntegerField(label='Elliptic Curve A')
    curve_b = forms.IntegerField(label='Elliptic Curve B')
    curve_n = forms.IntegerField(label='Order of Curve N')
    g_x = forms.IntegerField(label='Base Point G X coordinate')
    g_y = forms.IntegerField(label='Base Point G Y coordinate')

class PasswordVerificationForm(forms.Form):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
