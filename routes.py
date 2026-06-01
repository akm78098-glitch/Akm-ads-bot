from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import secrets

from database import get_db
from models import User, Channel, Campaign, Order, Payment
from schemas import (
    UserCreate, UserResponse, ChannelCreate, ChannelResponse,
    CampaignCreate, CampaignResponse, OrderResponse
)

router = APIRouter()

# ============ USERS ============
@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.telegram_id == user.telegram_id).first()
    if existing:
        return existing
    
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/{telegram_id}", response_model=UserResponse)
def get_user(telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users/{telegram_id}/add-funds")
def add_funds(telegram_id: int, amount: float, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.balance += amount
    db.commit()
    return {"message": f"Added ${amount}", "new_balance": user.balance}

# ============ CHANNELS ============
@router.post("/channels", response_model=ChannelResponse)
def create_channel(channel: ChannelCreate, db: Session = Depends(get_db)):
    owner = db.query(User).filter(User.id == channel.owner_id).first()
    if not owner or owner.user_type != "channel_owner":
        raise HTTPException(status_code=400, detail="Only channel owners can add channels")
    
    db_channel = Channel(**channel.dict())
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel

@router.get("/channels", response_model=List[ChannelResponse])
def get_channels(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Channel).filter(Channel.is_active == True)
    
    if category:
        query = query.filter(Channel.category == category)
    if min_price:
        query = query.filter(Channel.price_per_post >= min_price)
    if max_price:
        query = query.filter(Channel.price_per_post <= max_price)
    
    return query.all()

@router.get("/channels/owner/{owner_id}", response_model=List[ChannelResponse])
def get_owner_channels(owner_id: int, db: Session = Depends(get_db)):
    return db.query(Channel).filter(Channel.owner_id == owner_id).all()

# ============ CAMPAIGNS ============
@router.post("/campaigns", response_model=CampaignResponse)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    advertiser = db.query(User).filter(User.id == campaign.advertiser_id).first()
    if not advertiser or advertiser.user_type != "advertiser":
        raise HTTPException(status_code=400, detail="Only advertisers can create campaigns")
    
    db_campaign = Campaign(**campaign.dict())
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    
    # Auto-match channels
    matched_channels = db.query(Channel).filter(
        Channel.category == campaign.category,
        Channel.price_per_post <= campaign.price_per_post,
        Channel.subscribers >= campaign.target_subscribers_min,
        Channel.is_active == True
    ).order_by(Channel.subscribers.desc()).limit(10).all()
    
    for channel in matched_channels:
        order = Order(
            campaign_id=db_campaign.id,
            channel_id=channel.id,
            amount=channel.price_per_post,
            status="pending"
        )
        db.add(order)
    
    db.commit()
    return db_campaign

@router.get("/campaigns/advertiser/{advertiser_id}", response_model=List[CampaignResponse])
def get_advertiser_campaigns(advertiser_id: int, db: Session = Depends(get_db)):
    return db.query(Campaign).filter(Campaign.advertiser_id == advertiser_id).all()

# ============ ORDERS ============
@router.get("/orders/campaign/{campaign_id}", response_model=List[OrderResponse])
def get_campaign_orders(campaign_id: int, db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.campaign_id == campaign_id).all()

@router.get("/orders/channel/{channel_id}", response_model=List[OrderResponse])
def get_channel_orders(channel_id: int, db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.channel_id == channel_id).all()

@router.post("/orders/{order_id}/lock")
def lock_payment(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    campaign = order.campaign
    advertiser = db.query(User).filter(User.id == campaign.advertiser_id).first()
    
    if advertiser.balance < order.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Lock funds in escrow
    advertiser.balance -= order.amount
    escrow_code = secrets.token_hex(16)
    
    payment = Payment(
        order_id=order_id,
        amount=order.amount,
        status="locked",
        escrow_code=escrow_code
    )
    
    order.status = "locked"
    db.add(payment)
    db.commit()
    
    return {"message": "Payment locked in escrow", "escrow_code": escrow_code}

@router.post("/orders/{order_id}/confirm-post")
def confirm_post(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = "posted"
    order.posted_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Ad post confirmed"}

@router.post("/orders/{order_id}/release")
def release_payment(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != "posted":
        raise HTTPException(status_code=400, detail="Ad must be posted before releasing payment")
    
    payment = db.query(Payment).filter(Payment.order_id == order_id).first()
    channel_owner = order.channel.owner
    
    # Release funds to channel owner
    channel_owner.balance += order.amount
    payment.status = "released"
    payment.released_at = datetime.utcnow()
    order.status = "released"
    
    db.commit()
    
    return {"message": "Payment released to channel owner"}

# ============ MATCHING ENGINE ============
@router.get("/match/{campaign_id}")
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
    
    return {
        "campaign_id": campaign_id,
        "matches": [
            {
                "channel_id": c.id,
                "title": c.title,
                "subscribers": c.subscribers,
                "price": c.price_per_post
            } for c in matched[:10]
        ],
        "total_matches": len(matched)
    }