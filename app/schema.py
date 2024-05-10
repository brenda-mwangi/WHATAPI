import re
from typing import Optional
from pydantic import BaseModel, constr, validator,EmailStr, Field
from enum import Enum
import utils


class PasswordRequirements(BaseModel):
    password: constr(min_length=8)

    @validator('password')
    def check_password(cls, v):
        special_characters = "!@#$%^&*()_-+=<>?/"

        if not any(char.isupper() for char in v):
            raise ValueError(
                'Password must contain at least one uppercase letter')
        elif not any(char.islower() for char in v):
            raise ValueError(
                'Password must contain at least one lowercase letter')
        elif not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        elif not any(char in special_characters for char in v):
            raise ValueError(
                'Password must contain at least one special character')
        return v

class ModeOfPayment(str, Enum):
    mpesa = "Mpesa"
    airtel = "Airtel"
    card = "Card"

class UserBase(BaseModel):
    id: int = None
    username: constr(min_length=2, max_length=50) = Field(..., example="John")
    email: EmailStr = Field(..., example="john@example.com")
    password: constr(min_length=8) = Field(..., example="Pass@123*")

    @validator('password')
    def check_password_requirements(cls, v):
        PasswordRequirements(password=v)
        return v

class UserLogin(BaseModel):
    """Handles user login data"""

    # email: EmailStr
    phone: constr(strip_whitespace=True) = None
    password: constr(min_length=8)

    @validator('phone')
    def check_phone(cls, v):
        PhoneRequirements(phone=v)
        return v

    @validator('password')
    def check_password_requirements(cls, v):
        PasswordRequirements(password=v)
        return v

class LinkBase(BaseModel):
    id: str = utils.generate_random_link()
    title: constr(max_length=70, min_length=1)
    description: constr(min_length=1)
    mode_of_beneficiary_payment: ModeOfPayment
    beneficiary_phone: constr(min_length=13, max_length=13)
    target_amount: int = None

    @validator('beneficiary_phone')
    def check_phone(cls, v):
        PhoneRequirements(phone=v)
        return v

    def __init__(self, **data):
        super().__init__(**data)
        self.id = utils.generate_random_link()

    # @validator('our_percentage', always=True)
    # def set_our_percentage(cls, v, values):
    #     total_amount_collected = values.get('total_amount_collected')
    #     if total_amount_collected <= 1000:
    #         return 5.5
    #     elif total_amount_collected <= 5000:
    #         return 5
    #     elif total_amount_collected <= 20000:
    #         return 4.75
    #     else:
    #         return 4.5

    # total_amount_collected: conint(ge=0)
    # our_percentage: confloat(ge=0, le=100)
    # date_started: datetime
    # date_end: datetime

class UpdateUser(BaseModel):
    firstname: Optional[constr(min_length=2, max_length=50)]
    lastname: Optional[constr(min_length=2, max_length=50)]
    password: Optional[str]

    @validator('password')
    def check_password_requirements(cls, v):
        if v is None or v == '':
            return v
        else:
            PasswordRequirements(password=v)
            return v

    class Config:
        orm_mode = True

class UpdateLink(BaseModel):
    title: Optional[constr(max_length=70, min_length=1)]
    description: Optional[constr(min_length=1)]
    mode_of_beneficiary_payment: Optional[ModeOfPayment]
    beneficiary_phone: Optional[str]
    target_amount: Optional[int] = None

    # total_amount_collected: conint(ge=0)
    # date_end: datetime
    @validator('beneficiary_phone')
    def check_phone(cls, v):
        if v is None or v == '':
            return v
        else:
            PhoneRequirements(phone=v)
            return v

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    username: str
    email: str

    class Config:
        orm_mode = True

class LinkResponse(BaseModel):
    owner_id: int
    title: str = Field(..., title="The title associated with the link", max_length=70)
    description: str = Field(..., title="A description for the link")
    mode_of_beneficiary_payment: str = Field(None, title="The mode of payment to the beneficiary", max_length=100)
    beneficiary_phone: str = Field(..., title="The phone number of the beneficiary", max_length=13)
    target_amount: int = Field(default=None, title="The desired amount to be collected")

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData:
    def __init__(self, id: Optional[int], username: Optional[str], role: Optional[str]):
        self.id = id
        self.username = username
        self.role = role


# class Contribution(BaseModel):
#     full_name: str
#     hide_name: bool
#     phone: constr(regex=r'^(\+254\s?[17])\d{8}$')
#     contribution_amount: float
#     mode_of_payment: ModeOfPayment

#     @validator('contribution_amount')
#     def validate_min_amount(cls, v):
#         if v < 50:
#             raise ValueError('Contribution amount must be at least 50')
#         else:
#             v = ceil(v)
#         return v
