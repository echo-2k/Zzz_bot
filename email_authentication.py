import imaplib
import email
from email.header import decode_header

def get_confirmation_code(email_address, email_password):
    # Подключение к почтовому серверу Rambler
    imap_host = "imap.rambler.ru"
    imap_user = email_address
    imap_pass = email_password

    # Создание IMAP4 объекта и подключение к серверу
    mail = imaplib.IMAP4_SSL(imap_host)
    mail.login(imap_user, imap_pass)
    mail.select("inbox")

    # Поиск всех писем
    status, messages = mail.search(None, 'ALL')

    # Получение списка номеров писем
    mail_ids = messages[0].split()

    # Получение последнего письма
    latest_email_id = mail_ids[-1]

    # Получение тела последнего письма
    status, msg_data = mail.fetch(latest_email_id, "(RFC822)")

    # Парсинг содержимого письма
    msg = email.message_from_bytes(msg_data[0][1])

    # Декодирование заголовка
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding if encoding else "utf-8")

    # Поиск кода подтверждения в теле письма
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode()

    # Здесь предполагается, что код подтверждения находится в теле письма
    # Вам нужно адаптировать этот код под формат ваших писем
    confirmation_code = extract_confirmation_code(body)

    # Закрытие соединения и выход
    mail.close()
    mail.logout()

    return confirmation_code

def extract_confirmation_code(email_body):
    # Реализуйте извлечение кода подтверждения из тела письма
    # Пример:
    import re
    match = re.search(r'\b\d{6}\b', email_body)
    if match:
        return match.group(0)
    return None
