import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram.utils import executor
import requests

API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
account_count = 0

# Функция для получения кода подтверждения с почты
def get_confirmation_code(email):
    # Имплементация получения кода из почты
    return "123456"  # Вернуть реальный код подтверждения

# Функция для регистрации аккаунта
def register_account(email, password, proxy):
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server=socks5://{proxy}')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get("https://zenless.hoyoverse.com/en-us/main")
        wait = WebDriverWait(driver, 10)

        # Ввод почты
        email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_input.send_keys(email)

        # Отправка формы для получения кода подтверждения
        submit_email_button = driver.find_element(By.CSS_SELECTOR, "button.submit-email")
        submit_email_button.click()

        # Получение кода подтверждения из почты
        confirmation_code = get_confirmation_code(email)

        # Ввод кода подтверждения
        code_input = wait.until(EC.presence_of_element_located((By.NAME, "verificationCode")))
        code_input.send_keys(confirmation_code)

        # Ввод пароля
        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(password)
        repeat_password_input = driver.find_element(By.NAME, "confirmPassword")
        repeat_password_input.send_keys(password)

        # Отправка формы регистрации
        submit_button = driver.find_element(By.CSS_SELECTOR, "button.submit")
        submit_button.click()
        time.sleep(5)

        success_message = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.success-message")))
        print(f"Registration successful for {email}: {success_message.text}")

    except Exception as e:
        print(f"Registration failed for {email}: {e}")

    finally:
        driver.quit()

# Пример генерации пароля
def generate_password():
    return "examplepassword"  # Или используйте генератор случайных паролей

# Чтение почт и прокси из файлов
def read_files():
    with open("emails.txt", "r") as email_file:
        emails = [line.strip() for line in email_file]
    with open("proxy.txt", "r") as proxy_file:
        proxies = [line.strip() for line in proxy_file]
    return emails, proxies

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправьте файл emails.txt и proxy.txt для начала.")

@dp.message_handler(commands=['setcount'])
async def setcount(message: types.Message):
    global account_count
    try:
        count = int(message.get_args())
        if count > 0:
            account_count = count
            await message.reply(f"Количество аккаунтов для создания установлено: {count}")
        else:
            await message.reply("Количество должно быть положительным числом.")
    except ValueError:
        await message.reply("Пожалуйста, укажите допустимое количество аккаунтов после команды /setcount.")

@dp.message_handler(content_types=[types.ContentType.DOCUMENT])
async def handle_file(message: types.Message):
    file_id = message.document.file_id
    file_name = message.document.file_name
    file = await bot.get_file(file_id)
    file_path = file.file_path

    if file_name == "emails.txt" or file_name == "proxy.txt":
        destination = os.path.join(os.getcwd(), file_name)
        await bot.download_file(file_path, destination)
        await message.reply(f"{file_name} загружен.")
    else:
        await message.reply("Пожалуйста, загрузите emails.txt или proxy.txt")

@dp.message_handler(commands=['register'])
async def register(message: types.Message):
    global account_count
    if not os.path.exists("emails.txt") or not os.path.exists("proxy.txt"):
        await message.reply("Пожалуйста, загрузите оба файла: emails.txt и proxy.txt")
        return

    emails, proxies = read_files()
    if account_count == 0:
        await message.reply("Пожалуйста, укажите количество аккаунтов для создания с помощью команды /setcount.")
        return

    for i in range(account_count):
        if i >= len(emails) or i >= len(proxies):
            await message.reply("Недостаточно данных в файлах для указанного количества аккаунтов.")
            break
        email = emails[i]
        proxy = proxies[i]
        password = generate_password()
        register_account(email, password, proxy)

    await message.reply("Регистрация завершена.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
