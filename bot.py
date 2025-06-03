import os
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# TOKEN va ADMIN_ID
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Cheklar saqlanadigan papka
PAYMENT_CHECKS_FOLDER = "payment_checks"
os.makedirs(PAYMENT_CHECKS_FOLDER, exist_ok=True)

# Bot va dispatcher
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# FSM state
class RegistrationState(StatesGroup):
    waiting_for_payment_check = State()
    waiting_for_pubg_nick = State()

# Asosiy menyu
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
    await message.answer(
        "👋 <b>ASSALOMU ALYKUM</b>\n"
        "TDM TOURNAMENT BOTGA🎮 Xush kelibsiz!\n\n"
        "Bu botdan🤖 foydalanib turnirda qatnashish imkoniyatingiz bor.\n\n"
        "⚠️ <b>Oldindan ogohlantirish:</b> turnirda qatnashish <b>pullik</b>💵.\n"
        "Ya'ni slotlik! Biz sizni majburlamaymiz, bu <b>sizning qaroringiz</b>!!!🔞\n\n"
        "Agar turnirda qatnashmoqchi bo‘lsangiz, mana shu pastdagi 💳 karta raqamlariga <b>10.000 so‘m</b> tashlab ro'yxatdan o'tishingiz mumkin!!!\n\n"
        "❗️ Chekni yuborish uchun '📝 Ro'yxatdan o'tish' tugmasini bosing.\n"
        "❗️ Faqat rasm (chek rasmi) yuboring, ikki marta to‘lov qilmaslik uchun ehtiyot bo‘ling!\n\n"
        "<b>TURNIRDA QATNASHUVCHILARGA OMAD!</b>",
        reply_markup=main_menu
    )

@dp.callback_query(F.data == "register")
async def ask_for_check(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("💳 Iltimos, to‘lov chekini rasm yoki fayl shaklida yuboring.")
    await state.set_state(RegistrationState.waiting_for_payment_check)
    await callback.answer()

@dp.message(RegistrationState.waiting_for_payment_check, F.document | F.photo)
async def handle_check(message: Message, state: FSMContext):
    if message.document:
        file_id = message.document.file_id
        ext = message.document.file_name.split('.')[-1]
    else:
        file_id = message.photo[-1].file_id
        ext = "jpg"

    filename = f"{message.from_user.id}_{file_id}.{ext}"
    path = os.path.join(PAYMENT_CHECKS_FOLDER, filename)
    await bot.download_file_by_id(file_id, destination=path)

    # Tugmalar
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ To‘g‘ri", callback_data=f"approve:{message.from_user.id}")
    builder.button(text="❌ Noto‘g‘ri", callback_data=f"reject:{message.from_user.id}")

    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=file_id,
        caption=f"📥 Yangi chek:\n👤 @{message.from_user.username or message.from_user.full_name}\n🆔 ID: <code>{message.from_user.id}</code>",
        reply_markup=builder.as_markup()
    )

    await message.answer("✅ Chekingiz yuborildi. Endi PUBG nick va ID'ingizni yozing.")
    await state.set_state(RegistrationState.waiting_for_pubg_nick)

@dp.message(RegistrationState.waiting_for_pubg_nick)
async def handle_nick(message: Message, state: FSMContext):
    info = message.text
    await bot.send_message(ADMIN_ID, f"📄 PUBG ma'lumot:\n👤 @{message.from_user.username or message.from_user.full_name}\n🆔 {message.from_user.id}\n{info}")
    await message.answer("📋 Ma'lumot qabul qilindi. Tez orada bog‘lanamiz.")
    await state.clear()

@dp.callback_query(F.data.startswith("approve:"))
async def approve_callback(call: CallbackQuery):
    user_id = int(call.data.split(":")[1])
    await bot.send_message(
        user_id,
        "⚡️⚡️⚡️Chekingiz admin tomonidan tasdiqlandi✅✅✅.\n"
        "Endi PUBG nick🪪 ingizni va ID🆔 ingizni yuboring va siz ro'yxatdan o'tgan hisoblanasiz🔥🔥🔥!!!"
    )
    await call.answer("✅ Tasdiqlandi!")

@dp.callback_query(F.data.startswith("reject:"))
async def reject_callback(call: CallbackQuery):
    user_id = int(call.data.split(":")[1])
    await bot.send_message(
        user_id,
        "❌ Chekingiz rad etildi!\n"
        "🛑 Eskirgan yoki noto‘g‘ri chek yuborgan bo‘lsangiz, turnirdan chetlatilishingiz mumkin."
    )
    await call.answer("❌ Rad etildi.")

@dp.callback_query(F.data == "results")
async def results(callback: CallbackQuery):
    await callback.message.answer("📊 Natijalar hali mavjud emas.")
    await callback.answer()

@dp.callback_query(F.data == "my_games")
async def my_games(callback: CallbackQuery):
    await callback.message.answer("🎮 Sizda hozircha hech qanday o‘yinlar yo‘q.")
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
