from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu(user_type=None):
    """Main menu keyboard based on user type"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Dashboard"), KeyboardButton(text="💰 Wallet")],
            [KeyboardButton(text="📢 My Channels"), KeyboardButton(text="📈 My Campaigns")],
            [KeyboardButton(text="➕ Add Channel"), KeyboardButton(text="✨ Create Campaign")],
            [KeyboardButton(text="🔍 Browse Marketplace"), KeyboardButton(text="❓ Help")]
        ],
        resize_keyboard=True
    )
    return keyboard

def role_selection():
    """Role selection inline keyboard"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📈 Advertiser", callback_data="role_advertiser"))
    builder.add(InlineKeyboardButton(text="📢 Channel Owner", callback_data="role_owner"))
    builder.row(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"))
    return builder.as_markup()

def categories_keyboard():
    """Channel categories selection"""
    builder = InlineKeyboardBuilder()
    categories = ["Tech", "News", "Gaming", "Lifestyle", "Business", "Crypto", "Sports", "Other"]
    for cat in categories:
        builder.add(InlineKeyboardButton(text=cat, callback_data=f"cat_{cat}"))
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"))
    return builder.as_markup()

def back_button():
    """Simple back button"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 Back", callback_data="back"))
    return builder.as_markup()

def confirm_keyboard():
    """Confirmation keyboard"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Yes", callback_data="confirm_yes"))
    builder.add(InlineKeyboardButton(text="❌ No", callback_data="confirm_no"))
    return builder.as_markup()