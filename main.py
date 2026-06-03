from fastapi import FastAPI, Request, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
import secrets
import uvicorn
import logging
import httpx

# ============ LOGGING ============
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ DATABASE SETUP ============
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./akm_market.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============ MODELS ============
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    user_type = Column(String, nullable=False)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Channel(Base):
    __tablename__ = "channels"
    id = Column(Integer, primary_key=True)
    channel_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    subscribers = Column(Integer, default=0)
    price_per_post = Column(Float, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True)
    advertiser_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    budget = Column(Float, nullable=False)
    price_per_post = Column(Float, nullable=False)
    target_subscribers_min = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    channel_id = Column(Integer, ForeignKey("channels.id"))
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    posted_at = Column(DateTime, nullable=True)

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")
    escrow_code = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    released_at = Column(DateTime, nullable=True)

Base.metadata.create_all(bind=engine)

# ============ SCHEMAS ============
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

# ============ FASTAPI APP ============
app = FastAPI(title="AKM Ads Market API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ API ROUTES ============
@app.post("/api/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.telegram_id == user.telegram_id).first()
    if existing:
        return existing
    db_user = User(**user.dict())
    if db_user.balance == 0:
        db_user.balance = 100.0
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/users/{telegram_id}", response_model=UserResponse)
def get_user(telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/users/{telegram_id}/add-funds")
def add_funds(telegram_id: int, amount: float = Query(..., ge=10, le=1000), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.balance += amount
    db.commit()
    return {"message": f"Added ${amount}", "new_balance": user.balance}

@app.post("/api/channels", response_model=ChannelResponse)
def create_channel(channel: ChannelCreate, db: Session = Depends(get_db)):
    owner = db.query(User).filter(User.id == channel.owner_id).first()
    if not owner or owner.user_type != "channel_owner":
        raise HTTPException(status_code=400, detail="Only channel owners can add channels")
    db_channel = Channel(**channel.dict())
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel

@app.get("/api/channels", response_model=List[ChannelResponse])
def get_channels(category: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, db: Session = Depends(get_db)):
    query = db.query(Channel).filter(Channel.is_active == True)
    if category:
        query = query.filter(Channel.category == category)
    if min_price:
        query = query.filter(Channel.price_per_post >= min_price)
    if max_price:
        query = query.filter(Channel.price_per_post <= max_price)
    return query.all()

@app.get("/api/channels/owner/{owner_id}", response_model=List[ChannelResponse])
def get_owner_channels(owner_id: int, db: Session = Depends(get_db)):
    return db.query(Channel).filter(Channel.owner_id == owner_id).all()

@app.post("/api/campaigns", response_model=CampaignResponse)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    advertiser = db.query(User).filter(User.id == campaign.advertiser_id).first()
    if not advertiser or advertiser.user_type != "advertiser":
        raise HTTPException(status_code=400, detail="Only advertisers can create campaigns")
    db_campaign = Campaign(**campaign.dict())
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    matched_channels = db.query(Channel).filter(
        Channel.category == campaign.category,
        Channel.price_per_post <= campaign.price_per_post,
        Channel.subscribers >= campaign.target_subscribers_min,
        Channel.is_active == True
    ).order_by(Channel.subscribers.desc()).limit(10).all()
    for channel in matched_channels:
        order = Order(campaign_id=db_campaign.id, channel_id=channel.id, amount=channel.price_per_post, status="pending")
        db.add(order)
    db.commit()
    return db_campaign

@app.get("/api/campaigns/advertiser/{advertiser_id}", response_model=List[CampaignResponse])
def get_advertiser_campaigns(advertiser_id: int, db: Session = Depends(get_db)):
    return db.query(Campaign).filter(Campaign.advertiser_id == advertiser_id).all()

@app.get("/api/orders/campaign/{campaign_id}", response_model=List[OrderResponse])
def get_campaign_orders(campaign_id: int, db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.campaign_id == campaign_id).all()

@app.get("/api/orders/channel/{channel_id}", response_model=List[OrderResponse])
def get_channel_orders(channel_id: int, db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.channel_id == channel_id).all()

@app.get("/api/orders/user/{user_id}", response_model=List[OrderResponse])
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    advertiser_orders = db.query(Order).join(Campaign).filter(Campaign.advertiser_id == user_id).all()
    owner_orders = db.query(Order).join(Channel).filter(Channel.owner_id == user_id).all()
    all_orders = {order.id: order for order in advertiser_orders + owner_orders}
    return list(all_orders.values())

@app.post("/api/orders/{order_id}/lock")
def lock_payment(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Order can only be locked once")
    campaign = order.campaign
    advertiser = db.query(User).filter(User.id == campaign.advertiser_id).first()
    if advertiser.balance < order.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    advertiser.balance -= order.amount
    escrow_code = secrets.token_hex(16)
    payment = Payment(order_id=order_id, amount=order.amount, status="locked", escrow_code=escrow_code)
    order.status = "locked"
    db.add(payment)
    db.commit()
    return {"message": "Payment locked in escrow", "escrow_code": escrow_code}

@app.post("/api/orders/{order_id}/confirm-post")
def confirm_post(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "locked":
        raise HTTPException(status_code=400, detail="Payment must be locked first")
    order.status = "posted"
    order.posted_at = datetime.utcnow()
    db.commit()
    return {"message": "Ad post confirmed"}

@app.post("/api/orders/{order_id}/release")
def release_payment(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "posted":
        raise HTTPException(status_code=400, detail="Ad must be posted before releasing payment")
    payment = db.query(Payment).filter(Payment.order_id == order_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")
    channel_owner = order.channel.owner
    channel_owner.balance += order.amount
    payment.status = "released"
    payment.released_at = datetime.utcnow()
    order.status = "released"
    db.commit()
    return {"message": "Payment released to channel owner"}

@app.get("/api/match/{campaign_id}")
def match_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    matched = db.query(Channel).filter(
        Channel.category == campaign.category,
        Channel.price_per_post <= campaign.price_per_post,
        Channel.subscribers >= campaign.target_subscribers_min,
        Channel.is_active == True
    ).order_by(Channel.subscribers.desc()).all()
    return {"campaign_id": campaign_id, "matches": [{"channel_id": c.id, "title": c.title, "subscribers": c.subscribers, "price": c.price_per_post} for c in matched[:10]], "total_matches": len(matched)}

# ============ TELEGRAM BOT WEBHOOK ============
BOT_TOKEN = os.getenv("BOT_TOKEN")

@app.post(f"/webhook/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
        if "message" in update:
            message = update["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            if text == "/start":
                reply = "🚀 Welcome to AKM Ads Market!\n\nUse web app: https://akm-ads-app.vercel.app"
            else:
                reply = "Please use web app: https://akm-ads-app.vercel.app"
            async with httpx.AsyncClient() as client:
                await client.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": reply})
        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"ok": False}

@app.on_event("startup")
async def on_startup():
    if BOT_TOKEN:
        webhook_url = f"https://akm-ads-bot.onrender.com/webhook/{BOT_TOKEN}"
        async with httpx.AsyncClient() as client:
            await client.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}")
        logger.info(f"Webhook set to: {webhook_url}")

# ============ HEALTH CHECKS ============
@app.get("/")
def root():
    return {"message": "AKM Ads Market API is running", "status": "active"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)