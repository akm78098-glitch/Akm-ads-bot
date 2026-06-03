from aiogram.fsm.state import State, StatesGroup

class RegisterState(StatesGroup):
    waiting_for_role = State()

class AddChannelState(StatesGroup):
    waiting_for_channel_id = State()
    waiting_for_title = State()
    waiting_for_category = State()
    waiting_for_subscribers = State()
    waiting_for_price = State()

class CreateCampaignState(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_category = State()
    waiting_for_budget = State()
    waiting_for_price_per_post = State()
    waiting_for_min_subs = State()

class AddFundsState(StatesGroup):
    waiting_for_amount = State()

class OrderActionState(StatesGroup):
    waiting_for_confirmation = State()