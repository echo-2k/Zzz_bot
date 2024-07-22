import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

def get_confirmation_code(email):
    return "123456"  # Имплементация получения кода из почты

def register_account(email, password, proxy):
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

        confirmation_code = get_confirmation_code(email)

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
    return "examplepassword"  # Или используйте генератор случайных паролей

def read_files():
    emails = []
    proxies = []
    if os.path.exists("emails.txt"):
        with open("emails.txt", "r") as email_file:
            emails = [line.strip() for line in email_file]
    if os.path.exists("proxy.txt"):
        with open("proxy.txt", "r") as proxy_file:
            proxies = [line.strip() for line in proxy_file]
    return emails, proxies
  
