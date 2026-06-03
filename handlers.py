from aiogram import types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
import os

from keyboards import *
from states import *
from utils import *

ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

async def cmd_start(message: types.Message, state: FSMContext):
    """Handle /start command"""
    await state.clear()
    
    # Check if user exists
    user = await get_user(message.from_user.id)
    
    if user and "error" not in user:
        # Existing user
        welcome_text = (
            f"🎯 Welcome back, {message.from_user.first_name}!\n\n"
            f"📊 Your account type: {user['user_type'].upper()}\n"
            f"💰 Balance: {format_balance(user['balance'])}\n\n"
            f"Use the buttons below to manage your ads:"
        )
        await message.answer(welcome_text, reply_markup=main_menu(user['user_type']))
    else:
        # New user
        await message.answer(
            f"🚀 Welcome to AKM Ads Market, {message.from_user.first_name}!\n\n"
            f"Buy and sell Telegram ads with escrow protection.\n\n"
            f"Please select your role:",
            reply_markup=role_selection()
        )
        await state.set_state(RegisterState.waiting_for_role)

async def role_selected(callback: types.CallbackQuery, state: FSMContext):
    """Handle role selection"""
    role = callback.data.split("_")[1]
    
    # Register user
    result = await register_user(
        callback.from_user.id,
        callback.from_user.username,
        role
    )
    
    if "error" in result:
        await callback.message.edit_text(
            "❌ Registration failed. Please try again."
        )
    else:
        await callback.message.edit_text(
            f"✅ Registered successfully as {role.upper()}!\n\n"
            f"💰 You've received $100 welcome bonus!\n"
            f"Start by adding funds or creating campaigns."
        )
        await callback.message.answer(
            "Main Menu:",
            reply_markup=main_menu(role)
        )
    
    await state.clear()
    await callback.answer()

async def show_dashboard(message: types.Message):
    """Show user dashboard"""
    user = await get_user(message.from_user.id)
    
    if "error" in user:
        await message.answer("Please /start again")
        return
    
    if user['user_type'] == 'advertiser':
        campaigns = await get_advertiser_campaigns(user['id'])
        total_spent = sum(c.get('budget', 0) for c in campaigns if campaigns)
        
        dashboard = (
            f"📊 Advertiser Dashboard\n\n"
            f"💰 Balance: {format_balance(user['balance'])}\n"
            f"📢 Active Campaigns: {len([c for c in campaigns if c.get('is_active')])}\n"
            f"💸 Total Budget: {format_balance(total_spent)}\n\n"
            f"✨ Create a campaign to start advertising!"
        )
    else:
        channels = await get_owner_channels(user['id'])
        total_earning = sum(c.get('price_per_post', 0) for c in channels)
        
        dashboard = (
            f"📊 Channel Owner Dashboard\n\n"
            f"💰 Balance: {format_balance(user['balance'])}\n"
            f"📢 Channels: {len(channels)}\n"
            f"💹 Potential Earnings: {format_balance(total_earning)}\n\n"
            f"➕ Add channels to start earning!"
        )
    
    await message.answer(dashboard, reply_markup=main_menu(user['user_type']))

async def show_wallet(message: types.Message):
    """Show wallet and recent orders"""
    user = await get_user(message.from_user.id)
    
    if "error" in user:
        await message.answer("Please /start again")
        return
    
    wallet_text = (
        f"💰 Your Wallet\n\n"
        f"Balance: {format_balance(user['balance'])}\n"
        f"Account Type: {user['user_type'].upper()}\n\n"
        f"💡 Tips:\n"
        f"• Advertisers: Add funds to create campaigns\n"
        f"• Channel Owners: Complete orders to earn\n\n"
        f"Use buttons below to manage funds:"
    )
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💳 Add Funds")],
            [KeyboardButton(text="📜 Transaction History")],
            [KeyboardButton(text="🔙 Back to Menu")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(wallet_text, reply_markup=keyboard)

async def add_funds_start(message: types.Message, state: FSMContext):
    """Start add funds process"""
    await message.answer(
        "💰 Enter amount to add (USD):\n\n"
        "Minimum: $10\n"
        "Maximum: $1000\n\n"
        "Example: 100",
        reply_markup=back_button()
    )
    await state.set_state(AddFundsState.waiting_for_amount)

async def process_add_funds(message: types.Message, state: FSMContext):
    """Process add funds"""
    try:
        amount = float(message.text)
        if amount < 10 or amount > 1000:
            await message.answer("❌ Amount must be between $10 and $1000")
            return
        
        result = await add_funds(message.from_user.id, amount)
        
        if "error" in result:
            await message.answer("❌ Failed to add funds. Try again.")
        else:
            await message.answer(
                f"✅ Added {format_balance(amount)} to your wallet!\n"
                f"💰 New balance: {format_balance(result['new_balance'])}"
            )
        
        await state.clear()
    except ValueError:
        await message.answer("❌ Please enter a valid number")

async def add_channel_start(message: types.Message, state: FSMContext):
    """Start add channel process"""
    user = await get_user(message.from_user.id)
    
    if user.get('user_type') != 'channel_owner':
        await message.answer("❌ Only channel owners can add channels!\nUse /start to change role.")
        return
    
    await message.answer(
        "📢 Let's add your Telegram channel!\n\n"
        "Step 1/5: Send your channel username\n"
        "Example: @myawesomechannel\n\n"
        "⚠️ Make sure your channel is public!"
    )
    await state.set_state(AddChannelState.waiting_for_channel_id)

async def process_channel_id(message: types.Message, state: FSMContext):
    """Process channel ID"""
    channel_id = message.text.strip()
    if not channel_id.startswith('@'):
        channel_id = '@' + channel_id
    
    await state.update_data(channel_id=channel_id)
    await message.answer(
        "Step 2/5: What's the channel title?\n"
        "Example: Tech News Daily"
    )
    await state.set_state(AddChannelState.waiting_for_title)

async def process_channel_title(message: types.Message, state: FSMContext):
    """Process channel title"""
    await state.update_data(title=message.text)
    await message.answer(
        "Step 3/5: Select channel category:",
        reply_markup=categories_keyboard()
    )
    await state.set_state(AddChannelState.waiting_for_category)

async def process_channel_category(callback: types.CallbackQuery, state: FSMContext):
    """Process channel category"""
    category = callback.data.split("_")[1]
    await state.update_data(category=category)
    
    await callback.message.edit_text(
        f"Step 4/5: How many subscribers does {category} channel have?\n"
        "Example: 5000"
    )
    await state.set_state(AddChannelState.waiting_for_subscribers)
    await callback.answer()

async def process_channel_subs(message: types.Message, state: FSMContext):
    """Process subscriber count"""
    try:
        subs = int(message.text)
        await state.update_data(subscribers=subs)
        await message.answer(
            "Step 5/5: What's your price per post? (USD)\n"
            "Example: 50\n\n"
            "💡 Tip: Price based on subscribers:\n"
            "• 1K subs: $10-20\n"
            "• 10K subs: $50-100\n"
            "• 100K+ subs: $200+"
        )
        await state.set_state(AddChannelState.waiting_for_price)
    except ValueError:
        await message.answer("❌ Please enter a valid number")

async def process_channel_price(message: types.Message, state: FSMContext):
    """Process channel price"""
    try:
        price = float(message.text)
        data = await state.get_data()
        
        user = await get_user(message.from_user.id)
        
        channel_data = {
            "channel_id": data['channel_id'],
            "title": data['title'],
            "category": data['category'],
            "subscribers": data['subscribers'],
            "price_per_post": price,
            "owner_id": user['id']
        }
        
        result = await add_channel(channel_data)
        
        if "error" in result:
            await message.answer("❌ Failed to add channel. Try again.")
        else:
            await message.answer(
                f"✅ Channel added successfully!\n\n"
                f"📢 {data['title']}\n"
                f"📁 Category: {data['category']}\n"
                f"👥 {format_number(data['subscribers'])} subscribers\n"
                f"💰 {format_balance(price)} per post\n\n"
                f"Your channel is now live in the marketplace!"
            )
        
        await state.clear()
    except ValueError:
        await message.answer("❌ Please enter a valid price")

async def create_campaign_start(message: types.Message, state: FSMContext):
    """Start campaign creation"""
    user = await get_user(message.from_user.id)
    
    if user.get('user_type') != 'advertiser':
        await message.answer("❌ Only advertisers can create campaigns!\nUse /start to change role.")
        return
    
    await message.answer(
        "✨ Let's create your ad campaign!\n\n"
        "Step 1/6: Campaign title\n"
        "Example: Summer Sale 2024"
    )
    await state.set_state(CreateCampaignState.waiting_for_title)

async def process_campaign_title(message: types.Message, state: FSMContext):
    """Process campaign title"""
    await state.update_data(title=message.text)
    await message.answer(
        "Step 2/6: Campaign description\n"
        "Describe your product/service (max 200 chars):"
    )
    await state.set_state(CreateCampaignState.waiting_for_description)

async def process_campaign_desc(message: types.Message, state: FSMContext):
    """Process campaign description"""
    if len(message.text) > 200:
        await message.answer("❌ Description too long! Max 200 characters.")
        return
    
    await state.update_data(description=message.text)
    await message.answer(
        "Step 3/6: Select campaign category:",
        reply_markup=categories_keyboard()
    )
    await state.set_state(CreateCampaignState.waiting_for_category)

async def process_campaign_category(callback: types.CallbackQuery, state: FSMContext):
    """Process campaign category"""
    category = callback.data.split("_")[1]
    await state.update_data(category=category)
    
    await callback.message.edit_text(
        f"Step 4/6: Total budget for {category} campaign (USD)\n"
        "Example: 500"
    )
    await state.set_state(CreateCampaignState.waiting_for_budget)
    await callback.answer()

async def process_campaign_budget(message: types.Message, state: FSMContext):
    """Process campaign budget"""
    try:
        budget = float(message.text)
        if budget < 50:
            await message.answer("❌ Minimum budget is $50")
            return
        
        await state.update_data(budget=budget)
        await message.answer(
            "Step 5/6: Price per post (USD)\n"
            "How much will you pay per channel?\n"
            "Example: 25"
        )
        await state.set_state(CreateCampaignState.waiting_for_price_per_post)
    except ValueError:
        await message.answer("❌ Please enter a valid number")

async def process_campaign_price(message: types.Message, state: FSMContext):
    """Process campaign price per post"""
    try:
        price = float(message.text)
        data = await state.get_data()
        
        if price > data['budget']:
            await message.answer("❌ Price per post cannot exceed total budget!")
            return
        
        await state.update_data(price_per_post=price)
        await message.answer(
            "Step 6/6: Minimum subscribers per channel\n"
            "Example: 1000 (or 0 for no minimum)"
        )
        await state.set_state(CreateCampaignState.waiting_for_min_subs)
    except ValueError:
        await message.answer("❌ Please enter a valid number")

async def process_campaign_min_subs(message: types.Message, state: FSMContext):
    """Process campaign minimum subscribers"""
    try:
        min_subs = int(message.text)
        data = await state.get_data()
        
        user = await get_user(message.from_user.id)
        
        campaign_data = {
            "advertiser_id": user['id'],
            "title": data['title'],
            "description": data['description'],
            "category": data['category'],
            "budget": data['budget'],
            "price_per_post": data['price_per_post'],
            "target_subscribers_min": min_subs
        }
        
        result = await create_campaign(campaign_data)
        
        if "error" in result:
            await message.answer("❌ Failed to create campaign. Try again.")
        else:
            await message.answer(
                f"✅ Campaign created successfully!\n\n"
                f"📢 {data['title']}\n"
                f"📁 Category: {data['category']}\n"
                f"💰 Budget: {format_balance(data['budget'])}\n"
                f"💸 Price/Post: {format_balance(data['price_per_post'])}\n"
                f"🎯 Min subscribers: {format_number(min_subs)}\n\n"
                f"🤖 Auto-matching channels..."
            )
            
            # Show matched channels
            match_result = await api_request("GET", f"/match/{result['id']}")
            if match_result and 'matches' in match_result:
                matches = match_result['matches'][:5]
                if matches:
                    text = "🔍 Top matched channels:\n\n"
                    for m in matches:
                        text += f"📢 {m['title']} - {format_number(m['subscribers'])} subs - {format_balance(m['price'])}\n"
                    await message.answer(text)
        
        await state.clear()
    except ValueError:
        await message.answer("❌ Please enter a valid number")

async def browse_marketplace(message: types.Message):
    """Browse available channels"""
    channels = await get_channels()
    
    if not channels or "error" in channels:
        await message.answer("❌ No channels available yet.")
        return
    
    text = "🔍 Available Channels:\n\n"
    for ch in channels[:10]:
        text += (
            f"📢 {ch['title']}\n"
            f"📁 {ch['category']} | 👥 {format_number(ch['subscribers'])} subs\n"
            f"💰 {format_balance(ch['price_per_post'])}/post\n\n"
        )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Filter by Category", callback_data="filter_channels")]
    ])
    
    await message.answer(text, reply_markup=keyboard)

async def my_channels(message: types.Message):
    """Show user's channels"""
    user = await get_user(message.from_user.id)
    
    if user.get('user_type') != 'channel_owner':
        await message.answer("❌ You are not a channel owner.")
        return
    
    channels = await get_owner_channels(user['id'])
    
    if not channels:
        await message.answer("📢 You haven't added any channels yet.\nUse '➕ Add Channel' button to start!")
        return
    
    text = "📢 Your Channels:\n\n"
    total_earning = 0
    for ch in channels:
        text += (
            f"• {ch['title']}\n"
            f"  📁 {ch['category']} | 👥 {format_number(ch['subscribers'])} subs\n"
            f"  💰 {format_balance(ch['price_per_post'])}/post\n\n"
        )
        total_earning += ch['price_per_post']
    
    text += f"💹 Potential earnings: {format_balance(total_earning)}"
    await message.answer(text)

async def my_campaigns(message: types.Message):
    """Show user's campaigns"""
    user = await get_user(message.from_user.id)
    
    if user.get('user_type') != 'advertiser':
        await message.answer("❌ You are not an advertiser.")
        return
    
    campaigns = await get_advertiser_campaigns(user['id'])
    
    if not campaigns:
        await message.answer("✨ You haven't created any campaigns yet.\nUse '✨ Create Campaign' button to start!")
        return
    
    text = "📈 Your Campaigns:\n\n"
    for camp in campaigns:
        orders = await get_campaign_orders(camp['id'])
        completed = len([o for o in orders if o.get('status') == 'released'])
        
        text += (
            f"• {camp['title']}\n"
            f"  📁 {camp['category']} | 💰 {format_balance(camp['budget'])}\n"
            f"  📊 Orders: {completed}/{len(orders)} completed\n\n"
        )
    
    await message.answer(text)

async def help_command(message: types.Message):
    """Show help message"""
    help_text = (
        "📚 AKM Ads Market - Help Guide\n\n"
        "📌 For Advertisers:\n"
        "1. Add funds to wallet\n"
        "2. Create campaign with budget\n"
        "3. System auto-matches channels\n"
        "4. Lock payment in escrow\n"
        "5. Confirm ad → payment released\n\n"
        "📌 For Channel Owners:\n"
        "1. Add your channels\n"
        "2. Get matched with campaigns\n"
        "3. Post the ad\n"
        "4. Get payment from escrow\n\n"
        "🔒 Escrow Protection:\n"
        "Funds are locked until ad is confirmed\n\n"
        "💡 Commands:\n"
        "/start - Main menu\n"
        "/help - This guide\n\n"
        "💬 Support: @akm_support"
    )
    await message.answer(help_text)

async def cancel_handler(message: types.Message, state: FSMContext):
    """Cancel current operation"""
    await state.clear()
    await message.answer(
        "❌ Operation cancelled.",
        reply_markup=main_menu()
    )
