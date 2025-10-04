import random
import time
from passlib.context import CryptContext
import uuid
from starlette.templating import Jinja2Templates

pwd_ctxt = CryptContext(schemes=["argon2"], deprecated= "auto")
base_url = "http://localhost:8000"

# Template configuration
templates = Jinja2Templates(directory="templates")

# def chat_create_link(title, description, mode_of_beneficiary_payment, beneficiary_phone, target_amount):
#     url = base_url+"/link/create_link"
#     json_data = {
#         "title":title,
#         "description": description,
#         "mode_of_beneficiary_payment": mode_of_beneficiary_payment,
#         "beneficiary_phone": beneficiary_phone,
#         "target_amount": target_amount
#     }

    # print(json.loads(requests.post(url, json=json_data, headers={"Content-Type":"application/json"})))

def clear_chat(file):
    file.seek(0)
    file.truncate()

def hash(password: str):
    return pwd_ctxt.hash(password)


def verify_password(login_password: str, hashed_password: str):
    return pwd_ctxt.verify(login_password, hashed_password)

def generate_random_link():
    timestamp_hex = format(int(time.time() * 1000), '013x')
    random_value_hex = format(random.randint(0, 999999999), '09x')
    complex_uuid = str(f'{timestamp_hex}-{random_value_hex}-{"-".join(str(uuid.getnode()).split(":"))}')

    l = [""] + list(complex_uuid)
    l.append("")
    random.shuffle(l)

    unique_code_generated = ''.join(l)

    while '--' in unique_code_generated or unique_code_generated.startswith('-') or unique_code_generated.endswith('-'):
        random.shuffle(l)
        unique_code_generated = ''.join(l)

    return unique_code_generated
