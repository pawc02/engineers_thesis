from django.db import models

class SignedMessage(models.Model):
    username = models.CharField(max_length=100)
    curve_p = models.IntegerField()
    curve_a = models.IntegerField()
    curve_b = models.IntegerField()
    curve_n = models.IntegerField()
    g_x = models.IntegerField()
    g_y = models.IntegerField()
    message = models.TextField()
    pubkey_x = models.IntegerField()
    pubkey_y = models.IntegerField()
    r = models.IntegerField()
    s = models.IntegerField()
    hash = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wiadomość podpisana {self.timestamp} z otrzymanymi składowymi podpisu r = {self.r} oraz s = {self.s}"


class EncryptedMessage(models.Model):
    receiver = models.CharField(max_length=100)
    curve_p = models.BigIntegerField()
    curve_a = models.BigIntegerField()
    curve_b = models.BigIntegerField()
    g_x = models.BigIntegerField()
    g_y = models.BigIntegerField()
    pubkey_x = models.BigIntegerField()
    pubkey_y = models.BigIntegerField()
    message_x = models.BigIntegerField()
    message_y = models.BigIntegerField()
    c1_x = models.BigIntegerField()
    c1_y = models.BigIntegerField()
    c2_x = models.BigIntegerField()
    c2_y = models.BigIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Zaszyfrowana wiadomość z otrzymanymi punktami szyfrogramu C1=({self.c1_x}, {self.c1_y}) and C2=({self.c2_x}, {self.c2_y})'


class UserKeys(models.Model):
    username = models.CharField(max_length=100, unique=True)
    hashed_password = models.CharField(max_length=128)
    curve_p = models.IntegerField()
    curve_a = models.IntegerField()
    curve_b = models.IntegerField()
    curve_n = models.IntegerField()
    g_x = models.IntegerField()
    g_y = models.IntegerField()
    privkey = models.IntegerField()
    pubkey_x = models.IntegerField()
    pubkey_y = models.IntegerField()

    def __str__(self):
        return f"{self.username}"
