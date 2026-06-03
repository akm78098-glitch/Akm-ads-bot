import aiohttp
import os
from datetime import datetime

API_URL = os.getenv("API_URL", "https://akm-ads-bot.onrender.com")

async def api_request(method, endpoint, data=None):
    """Make API requests to backend"""
    async with aiohttp.ClientSession() as session:
        url = f"{API_URL}/api{endpoint}"
        try:
            if method == "GET":
                async with session.get(url) as resp:
                    return await resp.json()
            elif method == "POST":
                async with session.post(url, json=data) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        return {"error": f"HTTP {resp.status}"}
        except Exception as e:
            return {"error": str(e)}

async def get_user(telegram_id):
    """Get user from backend"""
    return await api_request("GET", f"/users/{telegram_id}")

async def register_user(telegram_id, username, user_type):
    """Register new user"""
    return await api_request("POST", "/users", {
        "telegram_id": telegram_id,
        "username": username,
        "user_type": user_type
    })

async def add_channel(data):
    """Add channel to backend"""
    return await api_request("POST", "/channels", data)

async def create_campaign(data):
    """Create campaign"""
    return await api_request("POST", "/campaigns", data)

async def add_funds(telegram_id, amount):
    """Add funds to wallet"""
    return await api_request("POST", f"/users/{telegram_id}/add-funds?amount={amount}", {})

async def get_channels(category=None):
    """Get all channels"""
    url = "/channels"
    if category:
        url += f"?category={category}"
    return await api_request("GET", url)

async def get_owner_channels(owner_id):
    """Get channel owner's channels"""
    return await api_request("GET", f"/channels/owner/{owner_id}")

async def get_advertiser_campaigns(advertiser_id):
    """Get advertiser's campaigns"""
    return await api_request("GET", f"/campaigns/advertiser/{advertiser_id}")

async def get_campaign_orders(campaign_id):
    """Get orders for a campaign"""
    return await api_request("GET", f"/orders/campaign/{campaign_id}")

async def lock_payment(order_id):
    """Lock payment in escrow"""
    return await api_request("POST", f"/orders/{order_id}/lock", {})

async def confirm_post(order_id):
    """Confirm ad posted"""
    return await api_request("POST", f"/orders/{order_id}/confirm-post", {})

async def release_payment(order_id):
    """Release payment to channel owner"""
    return await api_request("POST", f"/orders/{order_id}/release", {})

def format_number(num):
    """Format numbers with K/M suffix"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)

def format_balance(amount):
    """Format balance with currency"""
    return f"${amount:,.2f}"
