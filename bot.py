import asyncio
import logging
import time
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    LabeledPrice, 
    PreCheckoutQuery,
    FSInputFile
)

# =====================================================================
# ⚙️ НАСТРОЙКИ
# =====================================================================

BOT_TOKEN = "8786703803:AAFbBkEjFMiSorJw92-QpDs6nDtFHXw2bAo"

PUBLIC_CHANNEL_ID = "@dinosha_ace"          
PUBLIC_CHANNEL_LINK = "https://t.me/dinosha_ace" 

PRIVATE_CHANNEL_ID = -100336518816
USDT_WALLET = "TKVMZrfBCquFMyUHWWpm9gHzgtoN7m3g1r"

ADMIN_USERNAME = "@dinosha_its"
ADMIN_ID = 6886475878  # Твой Telegram ID для получения чеков на проверку

# =====================================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

user_languages = {}

class PaymentState(StatesGroup):
    waiting_for_proof = State()

# --- ТЕКСТЫ НА РАЗНЫХ ЯЗЫКАХ ---
TEXTS = {
    "ru": {
        "select_lang": "🌐 <b>Выберите язык / Choose language / Wybierz język:</b>",
        "need_sub": "Привет! 🥰\n\nДля использования бота, пожалуйста, подпишись на наш канал.",
        "sub_btn": "🔗 Подписаться",
        "check_sub_btn": "✅ Я подписался",
        "not_sub_alert": "❌ Вы всё ещё не подписаны на канал!",
        "tariff_caption": (
            "<b>Канал: VIP Доступ</b>\n"
            "<b>Тариф: 1 месяц</b>\n"
            "<b>Стоимость: 300 ⭐️ / $5 (USDT)</b>\n\n"
            "<b>Выберите способ оплаты:</b>"
        ),
        "pay_stars": "⭐️ Telegram Stars (300 Stars)",
        "pay_crypto": "💎 USDT TRC-20 (5$)",
        "back": "« Назад",
        "crypto_info": (
            "💎 <b>Оплата USDT (TRC-20)</b>\n\n"
            "Срок доступа: <b>1 месяц</b>\n"
            "Сумма к оплате: <b>5 USDT</b>\n\n"
            "Переведите <b>5 USDT</b> на адрес:\n"
            f"<code>{USDT_WALLET}</code>\n\n"
            "После перевода нажмите кнопку ниже и отправьте скриншот/хэш перевода прямо в этот чат!"
        ),
        "send_proof_btn": "📤 Отправить чек / хэш",
        "ask_proof": "📸 Пожалуйста, отправьте скриншот или хэш перевода прямо сюда следующим сообщением:",
        "proof_sent": "⏳ <b>Ваш чек отправлен администратору на проверку!</b>\nОжидайте, после проверки ссылка на 1 месяц будет отправлена сюда автоматически.",
        "success_pay": "🎉 <b>Оплата подтверждена! Доступ на 1 месяц активирован.</b>\n\nТвоя персональная ссылка в VIP-канал:\n",
        "rejected_pay": "❌ Ваш чек не был подтверждён. Обратитесь к администратору {admin}.",
        "link_error": f"Не удалось создать ссылку. Напишите администратору {ADMIN_USERNAME}."
    },
    "en": {
        "select_lang": "🌐 <b>Choose your language:</b>",
        "need_sub": "Hello! 🥰\n\nTo use this bot, please subscribe to our official channel.",
        "sub_btn": "🔗 Subscribe",
        "check_sub_btn": "✅ I subscribed",
        "not_sub_alert": "❌ You are still not subscribed to the channel!",
        "tariff_caption": (
            "<b>Channel: VIP Access</b>\n"
            "<b>Tariff: 1 Month</b>\n"
            "<b>Price: 300 ⭐️ / $5 (USDT)</b>\n\n"
            "<b>Select a payment method:</b>"
        ),
        "pay_stars": "⭐️ Telegram Stars (300 Stars)",
        "pay_crypto": "💎 USDT TRC-20 ($5)",
        "back": "« Back",
        "crypto_info": (
            "💎 <b>Pay with USDT (TRC-20)</b>\n\n"
            "Access duration: <b>1 Month</b>\n"
            "Amount: <b>5 USDT</b>\n\n"
            "Transfer <b>5 USDT</b> to wallet address:\n"
            f"<code>{USDT_WALLET}</code>\n\n"
            "After payment, click the button below and send the payment screenshot/hash directly to this chat!"
        ),
        "send_proof_btn": "📤 Send receipt / hash",
        "ask_proof": "📸 Please send the payment screenshot or hash directly here as the next message:",
        "proof_sent": "⏳ <b>Your receipt was sent to the admin for verification!</b>\nPlease wait, your 1-month VIP invite link will arrive here automatically.",
        "success_pay": "🎉 <b>Payment confirmed! 1-Month access granted.</b>\n\nHere is your link to the VIP channel:\n",
        "rejected_pay": "❌ Your receipt was rejected. Please contact admin {admin}.",
        "link_error": f"Could not create link. Please contact admin {ADMIN_USERNAME}."
    },
    "pl": {
        "select_lang": "🌐 <b>Wybierz język:</b>",
        "need_sub": "Cześć! 🥰\n\nAby korzystać z bota, zasubskrybuj nasz oficjalny kanał.",
        "sub_btn": "🔗 Dołącz do kanału",
        "check_sub_btn": "✅ Subskrybuję",
        "not_sub_alert": "❌ Nadal nie subskrybujesz kanału!",
        "tariff_caption": (
            "<b>Kanał: Dostęp VIP</b>\n"
            "<b>Taryfa: 1 Miesiąc</b>\n"
            "<b>Cena: 300 ⭐️ / $5 (USDT)</b>\n\n"
            "<b>Wybierz metodę płatności:</b>"
        ),
        "pay_stars": "⭐️ Telegram Stars (300 Stars)",
        "pay_crypto": "💎 USDT TRC-20 ($5)",
        "back": "« Powrót",
        "crypto_info": (
            "💎 <b>Płatność USDT (TRC-20)</b>\n\n"
            "Czas dostępu: <b>1 Miesiąc</b>\n"
            "Kwota: <b>5 USDT</b>\n\n"
            "Przelej <b>5 USDT</b> na adres:\n"
            f"<code>{USDT_WALLET}</code>\n\n"
            "Po wpłacie kliknij przycisk poniżej i wyślij potwierdzenie/zrzut ekranu w tej rozmowie!"
        ),
        "send_proof_btn": "📤 Wyślij potwierdzenie / hash",
        "ask_proof": "📸 Wyślij zrzut ekranu lub hash płatności bezpośrednio w następnej wiadomości:",
        "proof_sent": "⏳ <b>Twoje potwierdzenie zostało wysłane do weryfikacji!</b>\nOczekuj, Twój 1-miesięczny link VIP zostanie wysłany tutaj automatycznie.",
        "success_pay": "🎉 <b>Płatność potwierdzona! Dostęp na 1 miesiąc aktywowany.</b>\n\nOto Twój prywatny link do kanału VIP:\n",
        "rejected_pay": "❌ Twoje potwierdzenie zostało odrzucone. Skontaktuj się z {admin}.",
        "link_error": f"Nie udało się utworzyć linku. Skontaktuj się z administratorem {ADMIN_USERNAME}."
    }
}

# --- ПОМОЩНИКИ ---

def get_lang(user_id: int) -> str:
    return user_languages.get(user_id, "ru")

async def create_vip_invite_link(lang: str) -> str:
    try:
        # Создаем одноразовую ссылку, которая действительна для входа 24 часа
        expire_date = int(time.time()) + (24 * 3600)
        invite = await bot.create_chat_invite_link(
            chat_id=PRIVATE_CHANNEL_ID,
            member_limit=1,
            expire_date=expire_date
        )
        return invite.invite_link
    except Exception as e:
        logging.error(f"Error creating invite link: {e}")
        return TEXTS[lang]["link_error"]

async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=PUBLIC_CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# --- КЛАВИАТУРЫ ---

def get_language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton(text="🇵🇱 Polski", callback_data="lang_pl")
        ]
    ])

def get_sub_keyboard(lang: str):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["sub_btn"], url=PUBLIC_CHANNEL_LINK)],
        [InlineKeyboardButton(text=t["check_sub_btn"], callback_data="check_sub")]
    ])

def get_payment_methods_keyboard(lang: str):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["pay_stars"], callback_data="pay_stars")],
        [InlineKeyboardButton(text=t["pay_crypto"], callback_data="pay_crypto")],
        [InlineKeyboardButton(text=t["back"], callback_data="back_to_start")]
    ])

async def send_tariff_card(chat_id: int, lang: str):
    t = TEXTS[lang]
    try:
        photo = FSInputFile("preview.jpg")
        await bot.send_photo(
            chat_id=chat_id, 
            photo=photo, 
            caption=t["tariff_caption"], 
            reply_markup=get_payment_methods_keyboard(lang), 
            parse_mode="HTML"
        )
    except Exception:
        await bot.send_message(
            chat_id=chat_id, 
            text=t["tariff_caption"], 
            reply_markup=get_payment_methods_keyboard(lang), 
            parse_mode="HTML"
        )

# --- ОБРАБОТЧИКИ ---

# --- ОБРАБОТЧИКИ ---

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    try:
        # Отправляем приветственное фото с подписью и выбором языка
        photo = FSInputFile("preview.jpg")
        await message.answer_photo(
            photo=photo,
            caption=TEXTS["ru"]["select_lang"],
            reply_markup=get_language_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        # Если фото по какой-то причине не загрузилось, отправляем обычным текстом
        await message.answer(
            text=TEXTS["ru"]["select_lang"],
            reply_markup=get_language_keyboard(),
            parse_mode="HTML"
        )
@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    user_languages[callback.from_user.id] = lang
    await callback.message.delete()
    
    if not await check_subscription(callback.from_user.id):
        await callback.message.answer(TEXTS[lang]["need_sub"], reply_markup=get_sub_keyboard(lang))
    else:
        await send_tariff_card(callback.message.chat.id, lang)

@dp.callback_query(F.data == "check_sub")
async def on_check_sub(callback: types.CallbackQuery):
    lang = get_lang(callback.from_user.id)
    if await check_subscription(callback.from_user.id):
        await callback.message.delete()
        await send_tariff_card(callback.message.chat.id, lang)
    else:
        await callback.answer(TEXTS[lang]["not_sub_alert"], show_alert=True)

@dp.callback_query(F.data == "back_to_start")
async def back_to_start(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    lang = get_lang(callback.from_user.id)
    await callback.message.delete()
    await send_tariff_card(callback.message.chat.id, lang)

# 1. Telegram Stars
@dp.callback_query(F.data == "pay_stars")
async def pay_stars(callback: types.CallbackQuery):
    await callback.answer()
    prices = [LabeledPrice(label="VIP Access (1 Month)", amount=300)]
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="VIP Subscription (1 Month)",
        description="1 month access to private VIP channel",
        payload="vip_access_stars_1m",
        currency="XTR",
        prices=prices,
        provider_token=""
    )

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    lang = get_lang(message.from_user.id)
    invite_link = await create_vip_invite_link(lang)
    await message.answer(
        f"{TEXTS[lang]['success_pay']}\n{invite_link}",
        parse_mode="HTML"
    )

# 2. Crypto (USDT TRC-20)
@dp.callback_query(F.data == "pay_crypto")
async def pay_crypto(callback: types.CallbackQuery):
    await callback.answer()
    lang = get_lang(callback.from_user.id)
    t = TEXTS[lang]
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["send_proof_btn"], callback_data="start_send_proof")],
        [InlineKeyboardButton(text=t["back"], callback_data="back_to_start")]
    ])
    
    try:
        await callback.message.edit_caption(caption=t["crypto_info"], reply_markup=kb, parse_mode="HTML")
    except Exception:
        await callback.message.edit_text(text=t["crypto_info"], reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "start_send_proof")
async def start_send_proof(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    lang = get_lang(callback.from_user.id)
    await state.set_state(PaymentState.waiting_for_proof)
    await callback.message.answer(TEXTS[lang]["ask_proof"])

# Прием чека
@dp.message(StateFilter(PaymentState.waiting_for_proof))
async def process_proof(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    lang = get_lang(user_id)
    user_name = f"@{message.from_user.username}" if message.from_user.username else f"ID: {user_id}"

    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить (1 мес)", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{user_id}")
        ]
    ])

    admin_caption = f"🧾 <b>Новый чек на проверку (1 месяц)!</b>\nОт пользователя: {user_name} (ID: <code>{user_id}</code>)"

    try:
        if message.photo:
            await bot.send_photo(ADMIN_ID, photo=message.photo[-1].file_id, caption=admin_caption, reply_markup=admin_kb, parse_mode="HTML")
        elif message.document:
            await bot.send_document(ADMIN_ID, document=message.document.file_id, caption=admin_caption, reply_markup=admin_kb, parse_mode="HTML")
        else:
            await bot.send_message(ADMIN_ID, text=f"{admin_caption}\n\nТекст чека:\n{message.text}", reply_markup=admin_kb, parse_mode="HTML")
        
        await message.answer(TEXTS[lang]["proof_sent"], parse_mode="HTML")
    except Exception as e:
        logging.error(f"Error sending proof to admin: {e}")
        await message.answer(TEXTS[lang]["link_error"])

# Решение админа
@dp.callback_query(F.data.startswith("approve_"))
async def approve_payment(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    lang = get_lang(user_id)
    
    invite_link = await create_vip_invite_link(lang)
    
    try:
        await bot.send_message(
            user_id, 
            f"{TEXTS[lang]['success_pay']}\n{invite_link}", 
            parse_mode="HTML"
        )
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(f"✅ Доступ на 1 месяц подтвержден для ID {user_id}. Ссылка отправлена!")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка отправки сообщения пользователю: {e}")

@dp.callback_query(F.data.startswith("reject_"))
async def reject_payment(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    lang = get_lang(user_id)
    
    try:
        await bot.send_message(
            user_id, 
            TEXTS[lang]["rejected_pay"].format(admin=ADMIN_USERNAME), 
            parse_mode="HTML"
        )
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(f"❌ Чек отклонен для ID {user_id}.")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка отправки сообщения пользователю: {e}")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
