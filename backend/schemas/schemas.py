from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
import re


# ─── Auth ───
class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str
    phone: Optional[str] = None
    country: str = "India"

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is None or v.strip() == '':
            return None
        # Strip spaces and dashes for normalization
        cleaned = re.sub(r'[\s\-\(\)]+', '', v)
        # Accept Indian (10 digit) or international (+country_code + digits, 7-15 digits)
        if re.fullmatch(r'\d{10}', cleaned):  # Indian local
            return cleaned
        if re.fullmatch(r'\+\d{7,15}', cleaned):  # International e.g. +919876543210
            return cleaned
        raise ValueError('Phone must be a valid 10-digit number or international format (e.g. +919876543210)')

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

class UserLogin(BaseModel):
    identifier: str  # email OR phone number
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    phone: Optional[str]
    country: str
    role: str
    created_at: datetime
    class Config:
        from_attributes = True


from pydantic import BaseModel, EmailStr, Field

# ─── Store ───
class StoreCreate(BaseModel):
    name: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    region: str = Field(..., max_length=100)
    address: str = Field(..., max_length=1000)
    story: Optional[str] = Field(None, max_length=2000)
    phone: Optional[str] = Field(None, max_length=20)
    established_year: Optional[int] = None

class StoreOut(BaseModel):
    id: int
    owner_id: int
    name: str
    city: str
    region: str
    address: str
    story: Optional[str]
    phone: Optional[str]
    rating: float
    image_url: Optional[str]
    is_verified: bool
    established_year: Optional[int]
    class Config:
        from_attributes = True


# ─── Product ───
class ProductOut(BaseModel):
    id: int
    name: str
    regional_name: Optional[str]
    description: Optional[str]
    category: Optional[str]
    region: Optional[str]
    image_url: Optional[str]
    gst_rate: float = 12.0
    class Config:
        from_attributes = True

class StoreProductOut(BaseModel):
    id: int
    store_id: int
    product: ProductOut
    price: float
    weight_grams: int
    in_stock: bool
    class Config:
        from_attributes = True

class AddToCartItem(BaseModel):
    store_product_id: int
    quantity: int = 1


# ─── Delivery Address (Amazon-style structured fields) ───
class AddressCreate(BaseModel):
    full_name: str = Field(..., max_length=255)
    mobile: str = Field(..., max_length=20)
    pincode: str = Field(..., max_length=10)
    flat_building: str = Field(..., max_length=255)
    area_street: str = Field(..., max_length=255)
    landmark: Optional[str] = Field("", max_length=255)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    is_default: bool = False

class AddressOut(AddressCreate):
    id: int
    user_id: int
    class Config:
        from_attributes = True

class DeliveryAddress(AddressCreate):
    pass

# ─── Order ───
class OrderCreate(BaseModel):
    store_id: int
    address_id: Optional[int] = None
    delivery_address: Optional[DeliveryAddress] = None
    payment_method: str  # cod, upi, card, razorpay, paypal
    is_gift: bool = False
    gift_message: Optional[str] = None
    items: List[AddToCartItem]

class OrderItemOut(BaseModel):
    id: int
    store_product_id: int
    quantity: int
    unit_price: float
    product_name: Optional[str] = None
    product_image: Optional[str] = None
    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str  # pending, confirmed, preparing, shipped, delivered, cancelled

class OrderOut(BaseModel):
    id: int
    user_id: int
    store_id: int
    status: str
    subtotal: float
    discount_amount: float = 0.0
    gst_amount: float
    cgst_amount: float = 0.0
    sgst_amount: float = 0.0
    igst_amount: float = 0.0
    total_amount: float
    delivery_address: str
    is_gift: bool = False
    gift_message: Optional[str] = None
    payment_method: str
    payment_status: str
    payment_reference: Optional[str]
    created_at: datetime
    items: List[OrderItemOut] = []
    class Config:
        from_attributes = True
