import datetime
import random
import re
from string import ascii_letters, digits

from django.contrib.auth import login
from django.contrib.humanize.templatetags import humanize
from sms_ir import SmsIr

from config.settings import redis, SMS_API_KEY, SMS_PHONE, SMS_TEMPLATE_ID
from wallet.models import Wallet
from .models import Login
from .models import User

irancell_prefix = [930, 933, 935, 936, 937, 938, 939, 900, 901, 902, 903, 904, 905, 941]
hamrah_aval_prefix = [910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 990, 991, 992, 993, 994, 903]
ritel_prefix = [920, 921, 922]
shatel_prefix = [999]
all_prefix = irancell_prefix + hamrah_aval_prefix + ritel_prefix + shatel_prefix
sms_ir = SmsIr(SMS_API_KEY, SMS_PHONE)


def check_amount(amount):
    if re.match("^[0-9]{5,}$", amount) and int(amount) >= 20000:
        return True
    return False


def check_phone_ip(request, phone):
    # user_ip = get_client_ip(request)
    # counter_ip = redis.get(f"VerificationIP-{user_ip}") or 0
    # counter_ip = int(counter_ip)
    # if counter_ip >= 5:
    #     return False
    counter_phone = redis.get(f"VerificationPhone-{phone}") or 0
    counter_phone = int(counter_phone)
    if counter_phone >= 5:
        return False
    # redis.set(f"VerificationIP-{user_ip}", counter_ip + 1, ex=86400)
    redis.set(f"VerificationPhone-{phone}", counter_phone + 1, ex=86400)
    return True


def save_login_info(request, user, user_agent):
    info_login = Login.objects.create(user=user, ip=get_client_ip(request), data=user_agent)
    info_login.save()


def get_user_agent(request):
    try:
        user_agent = request.META['HTTP_USER_AGENT'].lower()
    except Exception:
        return None
    return user_agent


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def make_hash():
    letters_digits = ascii_letters + digits
    time_now = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    result = time_now
    for i in random.choices(letters_digits, k=30):
        result += i
    return result


def is_phone_correct(phone):
    if not phone.isdigit():
        return False
    if phone.startswith("0"):
        phone = phone[1:]
    elif phone.startswith("98"):
        phone = phone[2:]
    elif phone.startswith("+98"):
        phone = phone[3:]
    elif not phone.startswith("9"):
        return False

    if len(phone) != 10:
        return False
    if int(phone[:3]) not in all_prefix:
        return False

    phone = "0" + phone
    return phone


def expire_code(hash_id):
    redis.delete(f"VerificationHashId-{hash_id}")


def login_register_user(request, phone, user_agent, hash_id):
    try:
        user = User.objects.get(phone=phone, is_active=True)
    except User.DoesNotExist:
        user = User.objects.create(phone=phone, username=phone, is_active=True)

    login(request, user)
    expire_code(hash_id)
    save_login_info(request, user, user_agent)
    Wallet.objects.get_or_create(user=user)


def send_code(request, phone, hash_id):
    if not check_phone_ip(request, phone):
        return False, False

    if hash_id:
        real_code = redis.get(f"VerificationHashId-{hash_id}")
        if real_code:
            print(phone, real_code)
            return real_code, hash_id
    real_code = "".join([str(i) for i in random.choices(range(10), k=5)])
    res = sms_ir.send_verify_code(number=phone, template_id=SMS_TEMPLATE_ID, parameters=[{"name": "code", "value": real_code}])
    if res.status_code != 200:
        return False, False
    hash_id = make_hash()
    redis.set(f"VerificationHashId-{hash_id}", real_code, ex=300)
    print(phone, real_code)
    return real_code, hash_id


def human_readable_size(size, price=False, cpu=False):
    if price:
        return humanize.intcomma(size) + " " + "تومان"
    if cpu:
        return size + " " + "core"
    giga = 1000
    tera = 1000000
    size = int(size)
    if size >= tera:
        return str(size / tera) + " " + "TB"
    elif size >= giga:
        return str(size / giga) + " " + "GB"
    else:
        return str(size) + " " + "MB"
