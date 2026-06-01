from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    user_type = Column(String, nullable=False)  # advertiser or channel_owner
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    channels = relationship("Channel", back_populates="owner")
    campaigns = relationship("Campaign", back_populates="advertiser")

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
    
    owner = relationship("User", back_populates="channels")
    orders = relationship("Order", back_populates="channel")

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
    
    advertiser = relationship("User", back_populates="campaigns")
    orders = relationship("Order", back_populates="campaign")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    channel_id = Column(Integer, ForeignKey("channels.id"))
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, locked, posted, released
    created_at = Column(DateTime, default=datetime.utcnow)
    posted_at = Column(DateTime, nullable=True)
    
    campaign = relationship("Campaign", back_populates="orders")
    channel = relationship("Channel", back_populates="orders")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, locked, released
    escrow_code = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    released_at = Column(DateTime, nullable=True)