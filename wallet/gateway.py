import json

import requests

from config.settings import SANDBOX, MERCHANT

ZP_API_REQUEST = f"https://{SANDBOX}.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = f"https://{SANDBOX}.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/"


class ZarinPalRequest:

    class Response:
        status = False
        code = 0
        url = None
        authority = None
        ref_id = None

        def __init__(self, status, code, url=None, authority=None, ref_id=None) -> None:
            self.status = status
            self.code = code
            self.url = url
            self.authority = authority if authority else 'start'
            self.ref_id = ref_id
    
    def create_gateway(self, amount, description, callback_url):
        data = {
            "merchant_id": MERCHANT,
            "amount": amount * 10,
            "description": description,
            "callback_url": callback_url,
        }
        data = json.dumps(data)
        headers = {'content-type': 'application/json', 'content-length': str(len(data))}
        try:
            response = requests.post(ZP_API_REQUEST, data=data, headers=headers, timeout=10)
            if response.status_code == 200:
                response = response.json()
                if response['data']['code'] == 100:
                    return self.Response(True, 100, ZP_API_STARTPAY + str(response['data']['authority']), response['data']['authority'])
                else:
                    return self.Response(False, response['data']['code'])
            return self.Response(False, 400)
        
        except requests.exceptions.Timeout:
            return self.Response(False, 600)
        except requests.exceptions.ConnectionError:
            return self.Response(False, 601)
    
    def verify(self, authority, amount) -> Response:
        data = {
            "merchant_id": MERCHANT,
            "amount": amount * 10,
            "authority": authority
        }
        data = json.dumps(data)
        headers = {'content-type': 'application/json', 'content-length': str(len(data))}
        try:
            response = requests.post(ZP_API_VERIFY, data=data, headers=headers)
            if response.status_code == 200:
                response = response.json()
                if response['data']['code'] == 100:
                    return self.Response(True, 100, ref_id=response['data']['ref_id'])
            return self.Response(False, response.status_code)
        except requests.exceptions.Timeout:
            return self.Response(False, 600)
        except requests.exceptions.ConnectionError:
            return self.Response(False, 601)
