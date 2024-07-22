import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from account_registration import register_account, generate_password, read_files
from email_authentication import get_confirmation_code

API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_profiles = {}

def create_profile(user_id, user_name):
    user_profiles[user_id] = {
        'id': user_id,
        'username': user_name,
        'emails': [],
        'proxies': []
    }

def get_profile(user_id):
    profile = user_profiles.get(user_id, {})
    return f"ID: {profile.get('id', 'N/A')}\n" \
           f"Username: {profile.get('username', 'N/A')}\n" \
           f"Number of Emails: {len(profile.get('emails', []))}\n" \
           f"Number of Proxies: {len(profile.get('proxies', []))}"

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    create_profile(message.from_user.id, message.from_user.username)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Profile"), KeyboardButton("Upload Email"), KeyboardButton("Upload Proxy"), KeyboardButton("Register Accounts"))
    await message.reply("Welcome! Use the buttons below to interact with the bot.", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Profile")
async def show_profile(message: types.Message):
    profile_info = get_profile(message.from_user.id)
    await message.reply(profile_info)

@dp.message_handler(lambda message: message.text == "Upload Email")
async def upload_email(message: types.Message):
    await message.reply("Please upload the email file.")

@dp.message_handler(lambda message: message.text == "Upload Proxy")
async def upload_proxy(message: types.Message):
    await message.reply("Please upload the proxy file.")

@dp.message_handler(lambda message: message.text == "Register Accounts")
async def register_accounts(message: types.Message):
    if not os.path.exists("emails.txt") or not os.path.exists("proxy.txt"):
        await message.reply("Please upload both email and proxy files.")
        return

    emails, proxies = read_files()
    profile = user_profiles.get(message.from_user.id, {})
    
    if not emails or not proxies:
        await message.reply("Please upload the necessary files.")
        return

    for i in range(min(len(emails), len(proxies))):
        email = emails[i]
        proxy = proxies[i]
        password = generate_password()
        register_account(email, password, proxy)

    await message.reply("Registration completed.")

@dp.message_handler(content_types=[types.ContentType.DOCUMENT])
async def handle_file(message: types.Message):
    file_id = message.document.file_id
    file_name = message.document.file_name
    file = await bot.get_file(file_id)
    file_path = file.file_path

    if file_name == "emails.txt":
        destination = os.path.join(os.getcwd(), file_name)
        await bot.download_file(file_path, destination)
        user_id = message.from_user.id
        user_profiles[user_id]['emails'] = read_files()[0]
        await message.reply(f"{file_name} uploaded and processed.")
    elif file_name == "proxy.txt":
        destination = os.path.join(os.getcwd(), file_name)
        await bot.download_file(file_path, destination)
        user_id = message.from_user.id
        user_profiles[user_id]['proxies'] = read_files()[1]
        await message.reply(f"{file_name} uploaded and processed.")
    else:
        await message.reply("Please upload only emails.txt or proxy.txt files.")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
  
