import random
import os
import json
from datetime import datetime
from selenium.webdriver.remote.webdriver import WebElement
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta
import time
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from selenium.webdriver.chrome.options import Options
import pytz
from utils import logger


file_name_result = f"Мониторинг UI элементов МАРМ4 ({datetime.now().strftime('%Y%m%d_%H%M%S')}).txt"
logger_app = logger.get_logger(file_name_result)

CONNECTION_TIMEOUT = 40
auth_url = "https://marm.nalog.gov.ru:9085/auth/"

# Параметры письма
sender_email = "smtp_user@stm-labs.ru"
sender_password = "COgNF6FR"
receiver_email = ["kotyukovvv@rambler.ru"]
receiver_email_string = ", ".join(receiver_email)
subject = f"{'🔵' if not logger.COUNTER_ERROR else '🔴'} Мониторинг UI элементов МАРМ4"


# Функция отправки сообщений
def send_email(sender_email, sender_password, receiver_email, subject, file_name):
    # Создание объекта сообщения
    message = MIMEMultipart()
    message["From"] = sender_email
    message["Bcc"] = receiver_email
    message["Subject"] = subject

    # Добавление текстового содержимого к сообщению
    message.attach(MIMEText("Результаты выполнения программы во вложении."))

    # Получение последнего созданного файла в текущей директории
    with open(file_name, "rb") as file:
        attachment = MIMEApplication(file.read())
    attachment.add_header("Content-Disposition", "attachment", filename=file_name)
    message.attach(attachment)

    # Отправка сообщения
    with smtplib.SMTP_SSL("smtp.lancloud.ru", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(message)


# Функция получения данных страницы и элементов из json
def get_page_data_from_files(folder_path):
    page_data = []

    # Получение списка файлов в папке
    files = os.listdir(folder_path)

    # Чтение и обработка каждого файла
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as file:  # указание кодировки utf-8
                json_data = json.load(file)
                page_data.append(json_data)

    return page_data

# функция проверки элементов на странице
def navigate_to_auth_page(driver, logger_app):
    auth_form_locator = (By.XPATH, '//*[@id="root"]/div/div[1]/main/div/form')
    try:
        driver.get(auth_url)
        waiter = WebDriverWait(driver, timeout=10)
        auth_form = waiter.until(EC.presence_of_element_located(auth_form_locator))
        auth_form.find_element(By.ID, "login").send_keys("dev")
        auth_form.find_element(By.ID, "password").send_keys("8zq8=JRxOC$/Qe+")
        auth_form.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(3)
        logger_app.info("Форма авторизации заполнена", mark=True)
    except TimeoutException:
        logger_app.error(f"Переход на страницу авторизации - НЕ ОСУЩЕСТВЛЕН, ПРОВЕРЬТЕ РАБОТОСПОСОБНОСТЬ МАРМ-4", mark=True)
        logger_app.error("Форма авторизации не отображена! Необходимо проверить работоспособность МАРМ-4", mark=True)

def navigate_and_check_element(driver, page_data, logger_app):
    url = page_data[0].get("url")
    page_name = page_data[0].get("page_name")
    elements = page_data[0].get("elements")
    logger_app.info(f"\nПроверка элементов страницы {page_name}:\n")

    driver.get(url)

    for element in elements:
        locator_type, locator_value = element.get("locator").split("#", 1)
        name = element.get("name")

        try:
            if locator_type == "id":
                locator = (By.ID, locator_value)
            elif locator_type == "xpath":
                locator = (By.XPATH, locator_value)
            elif locator_type == "css_selector":
                locator = (By.CSS_SELECTOR, locator_value)
            elif locator_type == "class_name":
                locator = (By.CLASS_NAME, locator_value)
            else:
                raise ValueError(f"Неподдерживаемый тип локатора: {locator_type}")

            element_element = WebDriverWait(driver, 45).until(
                EC.visibility_of_element_located(locator)
            )

            logger_app.info(f"Элемент '{name}' на странице '{page_name}' видим.", mark=True)

        except NoSuchElementException:
            logger_app.error(f"Элемент '{name}' на странице '{page_name}' не найден.", mark=True)

        except TimeoutException:
            logger_app.error(f"Элемент '{name}' на странице '{page_name}' не отобразился.", mark=True)

        except ValueError as e:
            logger_app.error(str(e))



if __name__ == "__main__":
    folder_path = "pages_and_element"
    pages = get_page_data_from_files(folder_path)

    # Создание объекта MIMEMultipart
    msg = MIMEMultipart()

    # Получение текущей даты и времени по Московскому времени
    moscow_tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(moscow_tz)
    date_time = now.strftime("%d/%m/%Y %H:%M:%S")

    # Логгер
    file_name_result = f"Мониторинг UI элементов МАРМ4 {date_time} (Московское время).txt"
    logger_app = logger.get_logger(file_name_result)

    # Запуск браузера
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)

    # Переход на страницу авторизации и авторизация
    navigate_to_auth_page(driver, logger_app)

    # Проход по каждой странице и проверка элемента
    for page in pages:
        navigate_and_check_element(driver, page, logger_app)

    # Закрытие браузера
    driver.quit()

    # Сводная информация о проверках
    logger_app.info(f"\nВсего тестов: {logger.COUNTER_FULL}.")
    logger_app.info(f"Успешных тестов: {logger.COUNTER_SUCCESS}.", mark=True, counter=False)
    logger_app.error(f"Провальных тестов: {logger.COUNTER_ERROR}.", mark=True, counter=False)




