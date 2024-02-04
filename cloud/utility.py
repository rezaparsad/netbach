import random
from string import ascii_letters, digits


def generate_password(number=16):
    letters_digits = ascii_letters + digits
    result = ""
    for i in random.choices(letters_digits, k=number):
        result += i
    return result
