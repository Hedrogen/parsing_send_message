"""

    Парсит сайт www.wg-gesucht.de

"""

import json
import requests

import settings
import auth

from time import sleep
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def get_html(link, info=False):

    """ Получает html и возвращает из него content """

    request = requests.get(link, headers={'User-Agent': UserAgent().chrome})

    if info:
        print('\nSTATUS CODE:' + str(request.status_code) + '\n')
        for key, value in request.request.headers.items():
            print(key+": "+value)
        print('\n\n')

    if request.status_code >= 400:
        raise ConnectionError('Не удалось соедениться. Ошибка: ' + str(request.status_code))

    content = request.content

    return content


def get_soup(content):

    """ Переводит html.content в soup """

    soup = BeautifulSoup(content, 'lxml')
    return soup


def parse(link, write=False):

    """ Парсит"""

    soup = get_soup(get_html(link, True))
    json_dict = dict()
    base = soup.find_all('div', {'class': 'col-sm-8 card_body'})
    for element in base:
        id_ = element.parent.parent.get('data-id') # У рекламы id == None
        if id_:
            href = settings.SEND_LINK + str(element.find('a')['href'])
            name = element.find('span', {'class': 'ml5'}).text
            json_dict[id_] = [href, name]
    if write:
        with open('data.json', 'w') as file_:
            json.dump(json_dict, file_, indent=2, ensure_ascii=False)
    return json_dict


def create_list(mismatch_list=[], original_json=[]):

    """ Возвращает список по ключам, которые есть в mismatch_list """

    if mismatch_list and original_json:
        return [original_json.get(i) for i in mismatch_list]
    if original_json:
        return [original_json.get(i) for i in original_json]

def read_data(link):

    """ Cчитывает данные из data.json """
    try:
        with open('data.json', 'r') as file_:
            data = file_.read()
        return data
    except FileNotFoundError:
        return parse(link, write=True)


def main(time=60, send=False):

    """ Функция логики """


    iteration_number = 1

    while True:

        print('\nНомер итерации: ' + str(iteration_number) + '\n')
        data = read_data(settings.LINK)
        old_json = json.loads(data)
        new_json = parse(settings.LINK, True)
        mismatch_list = list(new_json.keys() - old_json.keys())
        if old_json != new_json:
            print('Отличия: \n', mismatch_list)
        if mismatch_list:
            send_dict = create_list(mismatch_list, new_json)
            print('1. Отправка содердимого боту')
            auth.Bot(send_dict)
        elif send: # Только тест
            print('2. Принудительная отправка содердимого боту')
            dict_ = create_list(original_json=new_json)
            print(dict_)
            auth.Bot(dict_)
        else:
            print('Ничего нового\n')

        sleep(int(time))
        iteration_number += 1

if __name__ == '__main__':
    main(time=settings.TIME)
