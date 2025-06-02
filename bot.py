import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import DefaultBotProperties, Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# TOKEN va ADMIN_ID
TOKEN = "7858191430:AAF2G3nxunGzFDVCCLwApA_31ymjTLIQtZA"
ADMIN_ID = 429955887

# To‘lov cheklarini saqlash papkasi
PAYMENT_CHECKS_FOLDER = "payment_checks"
os.makedirs(PAYMENT_CHECKS_FOLDER, exist_ok=True)

# Bot va Dispatcher
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# FSM holatlari
class RegistrationState(StatesGroup):
    waiting_for_payment_check = State()
    waiting_for_pubg_nick = State()

# Inline menyu
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="📝 Ro'yxatdan o'tish", callback_data="register"),
        InlineKeyboardButton(text="📊 Natijalar", callback_data="results")
    ],
    [
        InlineKeyboardButton(text="🎮 Mening o‘yinlarim", callback_data="my_games"),
        InlineKeyboardButton(text="📞 Admin (@xonda30)", url="https://t.me/xonda30")
    ]
])

@dp.message(Command("start"))
async def start_handler(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Check yuborish", callback_data="send_check")]
    ])
    await message.answer("Assalomu alaykum!\nTo‘lov chekini yuborish uchun tugmani bosing:", reply_markup=keyboard)

@dp.callback_query(F.data == "send_check")
async def ask_for_check(callback: CallbackQuery):
    await callback.message.answer("Iltimos, to‘lov chekini rasm yoki fayl shaklida yuboring.")
    await callback.answer()

@dp.message(F.document | F.photo)
async def handle_check_upload(message: Message):
    if message.document:
        file_id = message.document.file_id
        ext = message.document.file_name.split('.')[-1]
    else:
        file_id = message.photo[-1].file_id
        ext = "jpg"
    file = await bot.get_file(file_id)
    filename = f"{message.from_user.id}_{file_id}.{ext}"
    saved_path = os.path.join(PAYMENT_CHECKS_FOLDER, filename)

    # Faylni yuklab olish
    await bot.download_file_by_id(file_id, destination=saved_path)

    await message.answer("✅ Chekingiz qabul qilindi. Admin tekshiradi.")

    # Adminga yuborish
    await bot.send_photo(
        ADMIN_ID, 
        photo=file_id,
        caption=(
            f"🧾 Yangi to‘lov cheki keldi!\n"
            f"👤 @{message.from_user.username or message.from_user.full_name}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"📎 Fayl nomi: {filename}"
        )
    )
    await message.answer(
        "Iltimos, endi PUBG nick va ID'ingizni yozib yuboring."
    )
    # FSMni keyingi bosqichga o'tkazish
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(RegistrationState.waiting_for_pubg_nick)

@dp.message(RegistrationState.waiting_for_payment_check)
async def wrong_payment_format(message: Message):
    await message.answer("❌ Iltimos, faqat rasm yoki hujjat shaklidagi to‘lov chekini yuboring!")

@dp.message(RegistrationState.waiting_for_pubg_nick)
async def handle_pubg_nick(message: Message, state: FSMContext):
    user_pubg_info = message.text
    await message.answer(
        f"📋 Sizning PUBG ma'lumotingiz qabul qilindi:\n{user_pubg_info}\n\n"
        "Tez orada turnir vaqti haqida xabar beramiz."
    )
    # Adminga yuborish
    await bot.send_message(
        ADMIN_ID,
        f"📢 PUBG ma'lumot keldi:\n👤 @{message.from_user.username or message.from_user.full_name}\n🆔 {message.from_user.id}\n\n{user_pubg_info}"
    )
    await state.clear()

@dp.callback_query(F.data == "my_games")
async def handle_my_games(callback_query: CallbackQuery):
    await callback_query.message.answer("📋 Sizda hozircha hech qanday o‘yinlar yo‘q.")
    await callback_query.answer()

@dp.callback_query(F.data == "results")
async def handle_results(callback_query: CallbackQuery):
    await callback_query.message.answer("📊 Turnir natijalari hali mavjud emas.")
    await callback_query.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
