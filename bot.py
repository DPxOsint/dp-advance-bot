import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from groq import Groq
from typing import Union  # <--- YEH LINE ZAROORI HAI

# Config
BOT_TOKEN = "8282154443:AAETxZBlaU0ZHsVNFtmCgHSHTk_o9FWmGBY"
GROQ_API_KEY = "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"

# 3 channels
REQUIRED_CHANNELS = [
    "@DPxOsintCommunity",
    "@TeamxDP",
    "@BotsxCommunity"
]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_API_KEY)

async def is_user_member(user_id: int, chat_id: Union[str, int]) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

async def check_subscription(user_id: int):
    not_joined = []
    for channel in REQUIRED_CHANNELS:
        if not await is_user_member(user_id, channel):
            not_joined.append(channel)
    return len(not_joined) == 0, not_joined

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Hello friend! I AM ADVANCE AI BOT OF @cyb_pixel ASK ME ANYTHING😼")

@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    joined, not_joined = await check_subscription(user_id)
    
    if not joined:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        for channel in not_joined:
            invite_link = f"https://t.me/{channel.lstrip('@')}"
            button = InlineKeyboardButton(text=f"Join {channel}", url=invite_link)
            keyboard.inline_keyboard.append([button])
        
        refresh_button = InlineKeyboardButton(text="I JOIN🔄", callback_data="check_join")
        keyboard.inline_keyboard.append([refresh_button])
        
        await message.answer(
            "JOIN ALL REQUIRED CHANNELS FOR USING ADVANCE AI BOT🔥 :",
            reply_markup=keyboard
        )
        return
    
    # Groq answer
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": message.text}],
            model="llama-3.1-8b-instant",  # yeh abhi bhi chal raha hai (fast aur free)
        )
        
        response = chat_completion.choices[0].message.content
        await message.answer(response)
    except Exception as e:
        error_msg = str(e)
        print("Groq Error (terminal mein dekho):", error_msg)
        await message.answer(f"ai bot error: {error_msg}\nAN ERROR ! PLEASE CONTACT @cyb_pixel.👾")

@dp.callback_query(lambda c: c.data == "check_join")
async def check_join_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    joined, not_joined = await check_subscription(user_id)
    
    if joined:
        await callback.message.edit_text("NICE !! YOU CAN CHAT WITH ME NOW ")
        await callback.answer("Joined successfully!")
    else:
        await callback.answer("JOIN ALL REQUIRED CHANNELS FOR USING ADVANCE AI BOT", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":  
    asyncio.run(main())