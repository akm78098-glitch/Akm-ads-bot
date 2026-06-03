from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import router
import uvicorn
import os
import logging
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Update

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize app
app = FastAPI(
    title="AKM Ads Market API",
    description="Telegram Ad Marketplace Backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your existing API routes
app.include_router(router, prefix="/api")

# ============ TELEGRAM BOT WEBHOOK ============
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN not set! Bot webhook will not work.")
else:
    logger.info(f"BOT_TOKEN found: {BOT_TOKEN[:10]}...")

bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None
dp = Dispatcher() if bot else None

# Import your bot handlers (only if bot exists)
if bot and dp:
    try:
        from handlers import (
            cmd_start, help_command, cancel_handler, role_selected,
            process_channel_category, process_campaign_category,
            process_add_funds, process_channel_id, process_channel_title,
            process_channel_subs, process_channel_price, process_campaign_title,
            process_campaign_desc, process_campaign_budget, process_campaign_price,
            process_campaign_min_subs, show_dashboard, show_wallet,
            add_funds_start, add_channel_start, create_campaign_start,
            browse_marketplace, my_channels, my_campaigns
        )
        from keyboards import main_menu
        from states import RegisterState, AddChannelState, CreateCampaignState, AddFundsState
        logger.info("All handlers imported successfully")
    except Exception as e:
        logger.error(f"Failed to import handlers: {e}")

    # Register handlers
    @dp.message(Command("start"))
    async def webhook_cmd_start(message: types.Message, state: FSMContext):
        logger.info(f"Received /start from user {message.from_user.id}")
        try:
            await cmd_start(message, state)
            logger.info("cmd_start executed successfully")
        except Exception as e:
            logger.error(f"Error in cmd_start: {e}")

    @dp.message(Command("help"))
    async def webhook_help(message: types.Message):
        await help_command(message)

    @dp.message(Command("cancel"))
    async def webhook_cancel(message: types.Message, state: FSMContext):
        await cancel_handler(message, state)

    @dp.callback_query(lambda c: c.data.startswith("role_"))
    async def webhook_role_selected(callback: types.CallbackQuery, state: FSMContext):
        await role_selected(callback, state)

    @dp.callback_query(lambda c: c.data.startswith("cat_"))
    async def webhook_category(callback: types.CallbackQuery, state: FSMContext):
        current_state = await state.get_state()
        if current_state == AddChannelState.waiting_for_category:
            await process_channel_category(callback, state)
        elif current_state == CreateCampaignState.waiting_for_category:
            await process_campaign_category(callback, state)

    @dp.message()
    async def webhook_messages(message: types.Message, state: FSMContext):
        logger.info(f"Received message: {message.text}")
        current_state = await state.get_state()
        
        if current_state == AddFundsState.waiting_for_amount:
            await process_add_funds(message, state)
        elif current_state == AddChannelState.waiting_for_channel_id:
            await process_channel_id(message, state)
        elif current_state == AddChannelState.waiting_for_title:
            await process_channel_title(message, state)
        elif current_state == AddChannelState.waiting_for_subscribers:
            await process_channel_subs(message, state)
        elif current_state == AddChannelState.waiting_for_price:
            await process_channel_price(message, state)
        elif current_state == CreateCampaignState.waiting_for_title:
            await process_campaign_title(message, state)
        elif current_state == CreateCampaignState.waiting_for_description:
            await process_campaign_desc(message, state)
        elif current_state == CreateCampaignState.waiting_for_budget:
            await process_campaign_budget(message, state)
        elif current_state == CreateCampaignState.waiting_for_price_per_post:
            await process_campaign_price(message, state)
        elif current_state == CreateCampaignState.waiting_for_min_subs:
            await process_campaign_min_subs(message, state)
        else:
            if message.text == "📊 Dashboard":
                await show_dashboard(message)
            elif message.text == "💰 Wallet":
                await show_wallet(message)
            elif message.text == "💳 Add Funds":
                await add_funds_start(message, state)
            elif message.text == "➕ Add Channel":
                await add_channel_start(message, state)
            elif message.text == "✨ Create Campaign":
                await create_campaign_start(message, state)
            elif message.text == "🔍 Browse Marketplace":
                await browse_marketplace(message)
            elif message.text == "📢 My Channels":
                await my_channels(message)
            elif message.text == "📈 My Campaigns":
                await my_campaigns(message)
            elif message.text == "❓ Help":
                await help_command(message)

    @app.post(f"/webhook/{BOT_TOKEN}")
    async def telegram_webhook(request: Request):
        logger.info("=== WEBHOOK CALLED ===")
        try:
            update_data = await request.json()
            logger.info(f"Update data received")
            
            if bot is None or dp is None:
                logger.error("Bot or Dispatcher is None!")
                return {"ok": False}
            
            update = Update.model_validate(update_data)
            await dp.feed_update(bot, update)
            logger.info("Update fed to dispatcher successfully")
            return {"ok": True}
        except Exception as e:
            logger.error(f"Webhook error: {e}", exc_info=True)
            return {"ok": False}

    @app.on_event("startup")
    async def on_startup():
        if bot and BOT_TOKEN:
            webhook_url = f"https://akm-ads-bot.onrender.com/webhook/{BOT_TOKEN}"
            await bot.set_webhook(webhook_url)
            logger.info(f"Webhook set to: {webhook_url}")
        else:
            logger.error("Cannot set webhook: BOT_TOKEN missing")

    @app.on_event("shutdown")
    async def on_shutdown():
        if bot:
            await bot.delete_webhook()
            await bot.session.close()
            logger.info("Webhook deleted and session closed")

# ============ TEST ENDPOINTS ============
@app.get("/test-bot")
async def test_bot():
    """Test if bot token is valid"""
    if not BOT_TOKEN:
        return {"error": "BOT_TOKEN not set"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe")
            return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/webhook/info")
async def webhook_info():
    """Get webhook info from Telegram"""
    if not BOT_TOKEN:
        return {"error": "BOT_TOKEN not set"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo")
            return response.json()
    except Exception as e:
        return {"error": str(e)}

# ============ HEALTH CHECK ============
@app.get("/")
def root():
    return {
        "message": "AKM Ads Market API is running",
        "status": "active",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )