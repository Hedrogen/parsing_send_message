"""

    Бот отвечает за авторизацию и отправку сообщений
    Класс Bot принимает content(ссылку и имя человека) и текст.

"""

from time import sleep
from selenium import webdriver

import settings
import os

class Bot:

    """ Бот отвечает за авторизацию и отправку сообщений """

    def __init__(self, base_content):

        """

            Инициализация данных
        [
            base_content[0]-ссылка
            base_content[1]- имя человека,
        ],

        """

        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(executable_path=os.environ.get\
                ('CHROMEDRIVER_PATH'), chrome_options=chrome_options)

        self.site_login(settings.LOGIN, settings.PASSWORD)
        print('\n\n\n BASE \n', base_content[0])
        if len(base_content) > 0:
            for content in base_content:  #content список
                if len(content) > 0:
                    text = self.make_string(name=content[1])
                    try:
                        self.send_message(url=content[0], text=text)
                        sleep(2.5)
                    except:
                        continue
        print('\nОтправка сообщений закончена\n')

    def site_login(self, login, password):

        """ Авторизация """

        try:
            self.driver.get(settings.HOME_LINK)

            button_login = self.driver.find_element_by_xpath("//a[contains(text(), 'Login')]")
            button_login.click()

            sleep(2)

            email_window = self.driver.find_element_by_id('login_email_username')
            password_window = self.driver.find_element_by_id('login_password')
            email_window.send_keys(login)

            sleep(0.5)

            password_window.send_keys(password)
            button_login_window = self.driver.find_element_by_id('login_submit')
            button_login_window.click()

            sleep(0.5)

        except:                                 # На случай если выходит окно об использовании куки
            self.driver.get(settings.HOME_LINK)
            sleep(2)
            self.driver.find_element_by_xpath("//span[@id='cmpbntyestxt']").click()
            self.site_login(login, password)

    @staticmethod
    def make_string(name):

        """ Функция генерирует необходимый текст """

        if not settings.TEXT:
            raise ValueError('Поле text пустое')

        names = name.split(' ')
        firstname = names[0]

        try:
            secondname = names[1]
        except IndexError:
            secondname = firstname

        if 'frau' in name.lower():
            data = "Hallo " + 'Frau ' + secondname + ' '
        elif 'herr' in name.lower():
            data = "Hallo " + 'Herr ' + secondname + ' '
        elif len(firstname) > 2:
            data = "Hallo " + firstname + ' '
        else:
            data = 'Hallo ' + secondname + ' '
        data += settings.TEXT
        return data

    def send_message(self, url, text):

        """ Функция отправки сообщения """

        self.driver.get(url)

        if self.driver.find_elements_by_id('sicherheit_bestaetigung'):
            print('выполняет нажатие на согласен')
            attention_button = self.driver.find_element_by_id('sicherheit_bestaetigung')
            sleep(0.5)
            attention_button.click()

        try:
            print('Отправляет сообщение\n' + str(text))
            text_area = self.driver.find_element_by_id('message_input')
            text_area.send_keys(text)
            button_send = self.driver.find_element_by_class_name('create_new_conversation')
            button_send.click()
        except:
            print('Сообщение уже отпралено')
