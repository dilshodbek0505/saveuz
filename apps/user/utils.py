import requests

from django.conf import settings


ESKIZ_EMAIL = settings.ESKIZ_SMS_EMAIL
ESKIZ_PASSWORD = settings.ESKIZ_SMS_PASSWORD


class SMSBusiness:
    def __init__(self, text: str, phone: str, ):
        self.email = ESKIZ_EMAIL
        self.password = ESKIZ_PASSWORD
        self.text = text
        self.phone = phone
    
    def auth(self):
        url = "https://notify.eskiz.uz/api/auth/login"

        payload = {
            "email": self.email,
            "password": self.password
        }
        headers = {}
        files = []

        res = requests.request("POST", url, headers=headers, data=payload, files=files)
        if res.status_code == 200:
            res = res.json()
            return res.get("data").get("token")
        return None
    
    def send_sms(self):
        url = "https://notify.eskiz.uz/api/message/sms/send"
        payload = {
            "mobile_phone": self.phone,
            "message": self.text,
            "from": "4546",
        }

        files = []
        token = self.auth()
        
        headers = {
            "Authorization": f"Bearer {token}"
        }

        res = requests.request("POST", url, headers=headers, data=payload, files=files)

        return res.status_code
