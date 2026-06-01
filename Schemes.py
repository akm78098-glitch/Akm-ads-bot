from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    user_type: str

class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    user_type: str
    balance: float

class ChannelCreate(BaseModel):
    channel_id: str
    title: str
    category: str
    subscribers: int
    price_per_post: float
    owner_id: int

class ChannelResponse(BaseModel):
    id: int
    channel_id: str
    title: str
    category: str
    subscribers: int
    price_per_post: float
    is_active: bool

class CampaignCreate(BaseModel):
    advertiser_id: int
    title: str
    description: str
    category: str
    budget: float
    price_per_post: float
    target_subscribers_min: int = 0

class CampaignResponse(BaseModel):
    id: int
    title: str
    category: str
    budget: float
    price_per_post: float
    is_active: bool

class OrderResponse(BaseModel):
    id: int
    campaign_id: int
    channel_id: int
    amount: float
    status: str
    created_at: datetime