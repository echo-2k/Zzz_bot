import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from email_authentication import get_confirmation_code

def register_account(email, password, proxy, email_password):
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server=socks5://{proxy}')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get("https://zenless.hoyoverse.com/en-us/main")
        wait = WebDriverWait(driver, 10)

        email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_input.send_keys(email)

        submit_email_button = driver.find_element(By.CSS_SELECTOR, "button.submit-email")
        submit_email_button.click()

        confirmation_code = get_confirmation_code(email, email_password)

        code_input = wait.until(EC.presence_of_element_located((By.NAME, "verificationCode")))
        code_input.send_keys(confirmation_code)

        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(password)
        repeat_password_input = driver.find_element(By.NAME, "confirmPassword")
        repeat_password_input.send_keys(password)

        submit_button = driver.find_element(By.CSS_SELECTOR, "button.submit")
        submit_button.click()
        time.sleep(5)

        success_message = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.success-message")))
        print(f"Registration successful for {email}: {success_message.text}")

    except Exception as e:
        print(f"Registration failed for {email}: {e}")

    finally:
        driver.quit()

def generate_password():
    # Генерация случайного пароля
    return "examplepassword"

def read_files(emails_path, proxies_path):
    emails = []
    proxies = []
    if emails_path and os.path.exists(emails_path):
        with open(emails_path, "r") as email_file:
            emails = [line.strip() for line in email_file]
    if proxies_path and os.path.exists(proxies_path):
        with open(proxies_path, "r") as proxy_file:
            proxies = [line.strip() for line in proxy_file]
    return emails, proxies
