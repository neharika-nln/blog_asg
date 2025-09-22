import random
from datetime import datetime, timedelta


def generate_otp(otp_store, email):
    otp = str(random.randint(100000, 999999))
    otp_store[email] = {
        "otp": otp,
        "expires_at": datetime.now() + timedelta(minutes=10)
    }
    return otp
