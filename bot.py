import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

TOKEN = "7858191430:AAF2G3nxunGzFDVCCLwApA_31ymjTLIQtZA"
ADMIN_ID = 429955887  # Sizning admin ID'ingiz

# Papka yaratish (agar yo'q bo'lsa)
PAYMENT_CHECKS_FOLDER = "payment_checks"
os.makedirs(PAYMENT_CHECKS_FOLDER, exist_ok=True)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

router = Router()
dp.include_router(router)

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

@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "👋 <b>ASSALOMU ALYKUM</b>\n"
        "TDM TOURNAMENT BOTGA🎮 Xush kelibsiz!\n\n"
        "Bu botdan🤖 foydalanib turnirda qatnashish imkoniyatingiz bor.\n\n"
        "⚠️ <b>Oldindan ogohlantirish:</b> turnirda qatnashish <b>pullik</b>💵.\n"
        "Ya'ni slotlik! Biz sizni majburlamaymiz, bu <b>sizning qaroringiz</b>!!!🔞\n\n"
        "Agar turnirda qatnashmoqchi bo‘lsangiz, mana shu pastdagi 💳 karta raqamlariga 💳\n"
        "<b>10.000 so‘m</b> tashlab ro'yxatdan o'tishingiz mumkin!!!\n\n"
        "❗ Chekni yuborish uchun pastdagi '📝 Ro'yxatdan o'tish' tugmasini bosing.\n"
        "❗ Faqat rasm (chek rasmi) yuboring, ikki marta to‘lov qilmaslik uchun ehtiyot bo‘ling!\n\n"
        "<b>TURNIRDA QATNASHUVCHILARGA OMAD!</b>",
        reply_markup=main_menu
    )

@router.callback_query(lambda c: c.data == "register")
async def handle_register(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "💳 Ro‘yxatdan o‘tish uchun to‘lovni amalga oshirib, rasmni yuboring.\n\n"
        "📸 Iltimos, pastdagi 📎 tugmani bosib, 'Gallery' yoki 'Rasm' ni tanlang va to‘lov chekini rasm ko‘rinishida yuboring.\n\n"
        "⚠️ Faqatgina rasm formatidagi chek qabul qilinadi!"
    )
    await callback_query.answer()
    await state.set_state(RegistrationState.waiting_for_payment_check)

@router.message(RegistrationState.waiting_for_payment_check, lambda message: message.content_type == "photo")
async def handle_payment_check(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path_telegram = file.file_path
    filename = f"{message.from_user.id}_{photo.file_id}.jpg"
    local_path = os.path.join(PAYMENT_CHECKS_FOLDER, filename)

    # Yuklab olish
    await bot.download_file(file_path_telegram, destination=local_path)

    await message.answer("✅ Chek qabul qilindi! To‘lovingiz tekshirilmoqda, biroz kuting.")

    # Adminga habar beramiz
    await bot.send_message(
        ADMIN_ID,
        f"💳 Yangi to‘lov cheki yuborildi!\n"
        f"👤 @{message.from_user.username or message.from_user.full_name}\n"
        f"🆔 ID: {message.from_user.id}\n"
        f"🖼 Fayl: {filename}"
    )
    await bot.send_photo(ADMIN_ID, photo.file_id)

    await message.answer("Iltimos, endi PUBG nick va ID'ingizni yozib yuboring.")
    await state.set_state(RegistrationState.waiting_for_pubg_nick)

@router.message(RegistrationState.waiting_for_payment_check)
async def handle_wrong_payment_format(message: Message):
    await message.answer("❌ Noto‘g‘ri format! Iltimos, faqat rasm formatidagi to‘lov chekini yuboring.")

@router.message(RegistrationState.waiting_for_pubg_nick)
async def handle_pubg_nick(message: Message, state: FSMContext):
    user_pubg_info = message.text
    await message.answer(
        f"📋 Sizning PUBG ma'lumotingiz qabul qilindi:\n{user_pubg_info}\n\n"
        "Tez orada turnir vaqti haqida xabar beramiz."
    )
    await state.clear()

@router.callback_query(lambda c: c.data == "my_games")
async def handle_my_games(callback_query: CallbackQuery):
    await callback_query.message.answer("📋 Sizda hozircha hech qanday o‘yinlar yo‘q.")
    await callback_query.answer()

@router.callback_query(lambda c: c.data == "results")
async def handle_results(callback_query: CallbackQuery):
    await callback_query.message.answer("📊 Turnir natijalari hali mavjud emas.")
    await callback_query.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


