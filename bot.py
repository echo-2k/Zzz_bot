import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from account_registration import register_account, generate_password, read_files
from email_authentication import get_confirmation_code

API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

DATA_DIR = 'user_data'

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, 'users.json')

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def get_user_data_file(user_id, data_type):
    return os.path.join(DATA_DIR, f"{user_id}_{data_type}.json")

def create_profile(user_id, user_name):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {
            'id': user_id,
            'username': user_name
        }
        save_users(users)
        with open(get_user_data_file(user_id, 'emails'), 'w') as f:
            json.dump([], f)
        with open(get_user_data_file(user_id, 'proxies'), 'w') as f:
            json.dump([], f)
        with open(get_user_data_file(user_id, 'accounts'), 'w') as f:
            json.dump([], f)

def get_profile(user_id):
    users = load_users()
    user = users.get(str(user_id))
    if user:
        with open(get_user_data_file(user_id, 'emails'), 'r') as f:
            emails = json.load(f)
        with open(get_user_data_file(user_id, 'proxies'), 'r') as f:
            proxies = json.load(f)
        return f"🆔 ID: {user['id']}\n" \
               f"👤 Username: {user['username']}\n" \
               f"📧 Number of Emails: {len(emails)}\n" \
               f"🔐 Number of Proxies: {len(proxies)}"
    else:
        return "Profile not found."

def update_user_data(user_id, data_type, data):
    with open(get_user_data_file(user_id, data_type), 'w') as f:
        json.dump(data, f)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    create_profile(message.from_user.id, message.from_user.username)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📋 Profile"), 
                 KeyboardButton("📤 Upload Email"), 
                 KeyboardButton("📤 Upload Proxy"), 
                 KeyboardButton("📝 Register Accounts"))
    await message.reply("👋 Welcome! Use the buttons below to interact with the bot.", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "📋 Profile")
async def show_profile(message: types.Message):
    profile_info = get_profile(message.from_user.id)
    await message.reply(profile_info)

@dp.message_handler(lambda message: message.text == "📤 Upload Email")
async def upload_email(message: types.Message):
    await message.reply("📧 Please upload the email file.")

@dp.message_handler(lambda message: message.text == "📤 Upload Proxy")
async def upload_proxy(message: types.Message):
    await message.reply("🔐 Please upload the proxy file.")

@dp.message_handler(lambda message: message.text == "📝 Register Accounts")
async def register_accounts(message: types.Message):
    user_id = message.from_user.id

    emails_file = get_user_data_file(user_id, 'emails')
    proxies_file = get_user_data_file(user_id, 'proxies')

    if not os.path.exists(emails_file) or not os.path.exists(proxies_file):
        await message.reply("❗ Please upload both email and proxy files.")
        return

    with open(emails_file, 'r') as f:
        emails = json.load(f)
    with open(proxies_file, 'r') as f:
        proxies = json.load(f)

    if not emails or not proxies:
        await message.reply("❗ Please upload the necessary files.")
        return

    registered_accounts = []
    for i in range(min(len(emails), len(proxies))):
        email = emails[i]
        proxy = proxies[i]
        password = generate_password()
        email_password = "YOUR_EMAIL_PASSWORD"  # Не забудьте изменить на реальный пароль
        register_account(email, password, proxy, email_password)
        registered_accounts.append({'email': email, 'password': password, 'proxy': proxy})

    update_user_data(user_id, 'accounts', registered_accounts)
    await message.reply("✅ Registration completed.")

@dp.message_handler(content_types=[types.ContentType.DOCUMENT])
async def handle_file(message: types.Message):
    file_id = message.document.file_id
    file_name = message.document.file_name
    file = await bot.get_file(file_id)
    file_path = file.file_path

    destination = os.path.join(os.getcwd(), file_name)
    await bot.download_file(file_path, destination)

    user_id = message.from_user.id

    if file_name == "emails.txt":
        emails, _ = read_files(destination, None)
        update_user_data(user_id, 'emails', emails)
        await message.reply(f"✅ {file_name} uploaded and processed.")
    elif file_name == "proxy.txt":
        _, proxies = read_files(None, destination)
        update_user_data(user_id, 'proxies', proxies)
        await message.reply(f"✅ {file_name} uploaded and processed.")
    else:
        await message.reply("❗ Please upload only emails.txt or proxy.txt files.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
