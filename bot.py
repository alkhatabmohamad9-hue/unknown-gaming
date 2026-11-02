import os
import logging
import sqlite3
from contextlib import closing

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DB_PATH = os.getenv("DB_PATH", "unknown.db")

logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


def db():
    return sqlite3.connect(DB_PATH)


def init_db():
    with closing(db()) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                points INTEGER NOT NULL DEFAULT 0,
                referred_by INTEGER,
                joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        con.commit()


def get_user(user_id: int):
    with closing(db()) as con:
        return con.execute(
            "SELECT user_id, username, first_name, points FROM users WHERE user_id=?",
            (user_id,)
        ).fetchone()


def register_user(user, referrer=None):
    with closing(db()) as con:
        exists = con.execute(
            "SELECT user_id FROM users WHERE user_id=?", (user.id,)
        ).fetchone()
        if exists:
            return False
        valid_referrer = None
        if referrer and referrer != user.id:
            found = con.execute(
                "SELECT user_id FROM users WHERE user_id=?", (referrer,)
            ).fetchone()
            if found:
                valid_referrer = referrer
                con.execute(
                    "UPDATE users SET points=points+5 WHERE user_id=?",
                    (valid_referrer,)
                )
        con.execute(
            "INSERT INTO users(user_id, username, first_name, referred_by) VALUES(?,?,?,?)",
            (user.id, user.username, user.first_name, valid_referrer)
        )
        con.commit()
        return True


def main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🎮 الألعاب", callback_data="games")
    kb.button(text="⭐ رصيدي", callback_data="balance")
    kb.button(text="👥 دعوة الأصدقاء", callback_data="invite")
    kb.button(text="ℹ️ طريقة الاستخدام", callback_data="help")
    kb.adjust(2, 2)
    return kb.as_markup()


def games_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Rocket (تجريبية قريباً)", callback_data="coming")
    kb.button(text="💣 Mines (تجريبية قريباً)", callback_data="coming")
    kb.button(text="⚔️ PVP (قريباً)", callback_data="coming")
    kb.button(text="⬅️ القائمة الرئيسية", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


@dp.message(CommandStart())
async def start(message: Message):
    args = (message.text or "").split(maxsplit=1)
    referrer = None
    if len(args) == 2 and args[1].startswith("ref_"):
        try:
            referrer = int(args[1][4:])
        except ValueError:
            pass
    register_user(message.from_user, referrer)
    await message.answer(
        f"👑 أهلاً بك في <b>𝑈𝑁𝐾𝑁𝑂𝑊𝑁</b>\\n"
        f"منصة ألعاب تيليجرام بنظام نقاط افتراضي.\\n\\n"
        f"اختر من القائمة:",
        reply_markup=main_keyboard()
    )


@dp.message(Command("admin"))
async def admin(message: Message):
    if message.from_user.id != ADMIN_ID or ADMIN_ID == 0:
        await message.answer("⛔ هذا الأمر مخصص للمدير.")
        return
    with closing(db()) as con:
        count = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total = con.execute("SELECT COALESCE(SUM(points),0) FROM users").fetchone()[0]
    await message.answer(
        f"🛠 <b>لوحة المدير</b>\\nالمستخدمون: {count}\\nمجموع النقاط: {total}"
    )


@dp.callback_query(F.data == "home")
async def home(call: CallbackQuery):
    await call.message.edit_text(
        "👑 <b>𝑈𝑁𝐾𝑁𝑂𝑊𝑁</b>\\nاختر من القائمة:",
        reply_markup=main_keyboard()
    )
    await call.answer()


@dp.callback_query(F.data == "games")
async def games(call: CallbackQuery):
    await call.message.edit_text(
        "🎮 <b>منطقة الألعاب</b>\\nالألعاب ستُفعّل تدريجياً.",
        reply_markup=games_keyboard()
    )
    await call.answer()


@dp.callback_query(F.data == "balance")
async def balance(call: CallbackQuery):
    user = get_user(call.from_user.id)
    points = user[3] if user else 0
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ رجوع", callback_data="home")
    await call.message.edit_text(
        f"⭐ رصيدك الحالي: <b>{points}</b> نقطة\\n"
        "هذا رصيد افتراضي تجريبي وليس مالاً قابلاً للسحب.",
        reply_markup=kb.as_markup()
    )
    await call.answer()


@dp.callback_query(F.data == "invite")
async def invite(call: CallbackQuery):
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start=ref_{call.from_user.id}"
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ رجوع", callback_data="home")
    await call.message.edit_text(
        "👥 <b>دعوة الأصدقاء</b>\\n"
        "شارك رابطك. تحصل على 5 نقاط افتراضية عند انضمام صديق جديد:\\n"
        f"<code>{link}</code>",
        reply_markup=kb.as_markup()
    )
    await call.answer()


@dp.callback_query(F.data == "help")
async def help_page(call: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ رجوع", callback_data="home")
    await call.message.edit_text(
        "ℹ️ <b>طريقة الاستخدام</b>\\n"
        "ابدأ من القائمة، راجع رصيدك، وادعُ أصدقاءك.\\n"
        "الألعاب حالياً قيد التطوير وتستخدم نقاطاً افتراضية فقط.",
        reply_markup=kb.as_markup()
    )
    await call.answer()


@dp.callback_query(F.data == "coming")
async def coming(call: CallbackQuery):
    await call.answer("هذه اللعبة ستُضاف في مرحلة لاحقة.", show_alert=True)


async def main():
    init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
