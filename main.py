from abc import ABC, abstractmethod
import requests
import json


class StandardVacancy:
    """
    Родительский класс для указания переменных и их инкапсуляции
    """

    def __init__(self, name, page, count):
        self.__name = name
        self.__page = page
        self.__count = count

    def __repr__(self):
        return f'{self.__name}'

    @property
    def name(self):
        return self.__name

    @property
    def page(self):
        return self.__page

    @page.setter
    def page(self, new_page):
        self.__page = new_page

    @property
    def count(self):
        return self.__count


class MixinFuncs(ABC):
    """
    Миксин класс для обязывания дочерних классов к определенным методам
    """

    @abstractmethod
    def get_vacancies(self):
        pass

    @abstractmethod
    def vacancies_to_lstdir(self):
        pass


class SuperJob(StandardVacancy, MixinFuncs):
    """
    Класс для работы по API ключу с сайтом SuperJob.ru
    """
    api = 'v3.r.137906801.9a37685201b56dac6bf051def5f91e1841db45c0.9c7f03907437c65f5e2484500ea72a594c46d23b'
    url = 'https://api.superjob.ru/2.0/vacancies/'

    def __init__(self, name, page, count):
        super().__init__(name, page, count)

    def get_vacancies(self):
        """
        :return: json-словарь с вакансиями по пользовательским ключам
        """
        headers = {'X-Api-App-Id': SuperJob.api}
        vacancies = requests.get(SuperJob.url, headers=headers,
                                 params={'keywords': self.name, 'page': self.page, 'count': self.count}).json()
        return vacancies

    def vacancies_to_lstdir(self):
        """
        :return: список словарей, где каждый словарь - вакансия с определенными данными о ней
        """
        lst_vacancies = []
        sj_dict = self.get_vacancies()

        for element in sj_dict['objects']:
            if element['payment_from'] and element['payment_to'] != 0:
                payment = str(element['payment_from']) + '-' + str(element['payment_to'])
            elif element['payment_from'] == 0 and element['payment_to'] == 0:
                payment = "Зарплата не указана"
            elif element['payment_from'] == 0:
                payment = 'До ' + str(element['payment_to'])
            elif element['payment_to'] == 0:
                payment = 'От ' + str(element['payment_from'])
            else:
                payment = "Зарплата не указана"

            vacancy = {
                "Должность": element['profession'],
                "Зарплата": payment,
                "Город": element['town']['title'],
                "График работы": element['type_of_work']['title'],
                "Обязанности": element['candidat'].replace('•', '').replace('\n', ''),
                "Платформа размещения вакансии": "SuperJob.ru"

            }
            lst_vacancies.append(vacancy)
        return lst_vacancies

    def print_info(self) -> str:
        """
        Используется для отладки
        :return: словарь в удобном формате
        """
        return json.dumps(self.get_vacancies(), indent=2, ensure_ascii=False)


class HH(StandardVacancy, MixinFuncs):
    """
    Класс для работы по API ключу с сайтом HH.ru
    """
    url = 'https://api.hh.ru/vacancies'

    def __init__(self, name, page, count):
        super().__init__(name, page, count)

    def get_vacancies(self):
        """
        :return: json-словарь с вакансиями по пользовательским ключам
        """
        vacancies = requests.get(HH.url,
                                 params={'text': self.name, 'page': self.page, 'per_page': self.count}).json()
        return vacancies

    def vacancies_to_lstdir(self):
        """
        :return: список словарей, где каждый словарь - вакансия с определенными данными о ней
        """
        lst_vacancies = []
        hh_dict = self.get_vacancies()
        for element in hh_dict['items']:
            if element['salary'] is None:
                payment = 'Зарплата не указана'
            elif element['salary']['from'] is None:
                payment = 'До ' + str(element['salary']['to'])
            elif element['salary']['to'] is None:
                payment = 'От ' + str(element['salary']['from'])
            elif element['salary']['from'] and element['salary']['to'] is not None:
                payment = str(element['salary']['from']) + '-' + str(element['salary']['to'])

            vacancy = {
                "Должность": element['name'],
                "Зарплата": payment,
                "Город": element['area']['name'],
                "График работы": element['schedule']['name'],
                "Обязанности": element['snippet']['responsibility'],
                "Платформа размещения вакансии": 'hh.ru'

            }
            lst_vacancies.append(vacancy)

        return lst_vacancies

    def print_info(self) -> str:
        """
        Используется для отладки
        :return: словарь в удобном формате
        """
        return json.dumps(self.get_vacancies(), indent=2, ensure_ascii=False)


class JSONSaver:

    @classmethod
    def load_file(cls, file='Vacancies.json'):
        """
        Открывает json-файл с вакансиями
        :param file: json-файл
        :return: список словарей вакансий
        """
        with open(file, 'r', encoding='utf-8') as f:
            vacancies = json.load(f)
        return vacancies

    @classmethod
    def add_vacancy(cls, text: list):
        """
        Записывает в конец файла вакансии
        :param text: вакансии
        """
        vacancies = JSONSaver.load_file()
        with open('Vacancies.json', 'w', encoding='utf-8') as file:
            for vacancy in text:
                vacancies.append(vacancy)
            json.dump(vacancies, file, indent=2, ensure_ascii=False)

    @classmethod
    def clear_file(cls):
        """
        Метод полной очистки файла
        :return: Чистый файл
        """
        with open('Vacancies.json', 'w', encoding='utf-8') as file:
            file.write('[]')

    @classmethod
    def find_town(cls, town):
        """
        Метод для поиска вакансии в городе
        :param town: город
        :return: отфильтрованный по ключу 'Город' список
        """
        vacancies = JSONSaver.load_file()
        filtered_lst = []
        for vacancy in vacancies:
            if vacancy['Город'].lower() == town.lower():
                filtered_lst.append(vacancy)
        with open('Vacancies.json', 'w', encoding='utf-8') as file:
            json.dump(filtered_lst, file, indent=2, ensure_ascii=False)

    @classmethod
    def find_salary(cls, salary):
        """
        Метод для поиска вакансии по зарплате
        :param salary: Ожидаемая зарплата
        :return: отфильтрованный по ключу 'Зарплата' список
        """
        vacancies = JSONSaver.load_file()
        filtered_lst = []
        for vacancy in vacancies:
            try:
                splited_salary = vacancy['Зарплата'].split('-')
                if int(splited_salary[1]) >= salary:
                    filtered_lst.append(vacancy)
            except:
                if vacancy['Зарплата'] == 'Зарплата не указана':
                    pass
                elif int(vacancy['Зарплата'][3:]) >= salary:
                    filtered_lst.append(vacancy)
        with open('Vacancies.json', 'w', encoding='utf-8') as file:
            json.dump(filtered_lst, file, indent=2, ensure_ascii=False)


def find_vacancy():
    """
    Основной код программы. Создает бесконечный цикл, где создает/чистит файл перед последующей работой.
    Получает вакансии с hh.ru и superjob.ru, фильтрует вакансии по городу и зарплате.
    Если отфильтрованный список пустой автоматически переходит на следующую страницу поиска.
    выводит вакансии в удобном формате с возможностью просмотра вакансии дальше, иначе программа останавливается
    :return: None
    """
    count = 15
    page = 1
    name = input('Введите вакансию ')
    town = input('Введите город для поиска ')
    calary = int(input('Введите ожидаемую зарплату '))
    while True:
        JSONSaver.clear_file()
        sj = SuperJob(name, page, count)
        hh = HH(name, page, count)
        JSONSaver.add_vacancy(sj.vacancies_to_lstdir())
        JSONSaver.add_vacancy(hh.vacancies_to_lstdir())
        JSONSaver.find_salary(calary)
        JSONSaver.find_town(town)
        filtered_lst = JSONSaver.load_file()
        if filtered_lst == []:
            page += 1
            pass
        else:
            for vacancy in filtered_lst:
                print(f'\nДолжность - {vacancy["Должность"]}\n'
                      f'Зарплата - {vacancy["Зарплата"]}\n'
                      f'Город - {vacancy["Город"]}\n'
                      f'График работы - {vacancy["График работы"]}\n'
                      f'Обязанности - {vacancy["Обязанности"]}\n'
                      f'Платформа размещения вакансии - {vacancy["Платформа размещения вакансии"]}')
            next_page = input('Перейти на следующую страницу дa/нет ')
            if next_page == 'да' or next_page == 'д':
                print("_" * 8, "СЛЕДУЮЩАЯ СТРАНИЦА", "_" * 8)
                page += 1
            else:
                break


################################################################################################
find_vacancy()
