import csv
import os
import datetime
from datetime import datetime, timedelta
import telebot


token = os.getenv('TOKEN')
bot = telebot.TeleBot(token)

data: dict[int, dict[str, str | datetime | timedelta]] = {}
yesterday_duration: dict[int, list[float]] = {}
report_found: dict[int, bool] = {}


@bot.message_handler(commands=['start'])
def start_handler(message: telebot.types) -> None:
    """
    При получении команды start создается значение по умолчанию словаря
    data, где ключ - id пользователя, а значение - пустой словарь, в
    который впоследствии будет записываться информация пользователя.
    Выводится приветствие.
    :param message: Ввод команды start от пользователя
    :return: None
    """
    data.setdefault(message.from_user.id, {})
    bot.send_message(message.chat.id, 'Здравствуйте! '
                                      'Я ваш помощник в отслеживании качества сна. '
                                      'Используйте команду /sleep, '
                                      'когда будете ложиться спать, и команду /wake, '
                                      'когда проснетесь. '
                                      'Если не сможете уснуть, нажмите команду '
                                      '/sleep повторно при новой попытке.')


@bot.message_handler(commands=['sleep'])
def sleep_handler(message: telebot.types) -> None:
    """
    При получении команды sleep в словарь по ключу id пользователя
    записываются пары: 'date' - дата получения команды в формате str;
    'sleep_time' - момент времени получения команды.
    Выводится сообщение пользователю.
    :param message: Ввод команды sleep от пользователя
    :return: None
    """
    data[message.from_user.id]['date']: str = datetime.now().strftime('%d.%m.%Y')
    data[message.from_user.id]['sleep_time']: datetime = datetime.now()
    bot.send_message(message.chat.id, 'Спокойной ночи! Начинаю отсчет времени🌌')


@bot.message_handler(commands=['wake'])
def wake_handler(message: telebot.types) -> None:
    """
    При получении команды wake пробует выполниться код в блоке try:
    в словарь по ключу id пользователя записываются пары:
    'wake_time' - момент времени получения команды;
    'duration' - разница между моментами получения команд sleep и wake.
    Если команда sleep не была получена и в словаре нет ключа
    'sleep_time', обрабатывается исключение KeyError, пользователю
    выводится соответствующее сообщение.

    Если пользователь забыл нажать команду sleep при повторном
    использовании программы, и разница между временем получения команд
    sleep и wake больше суток, пользователю выводится соответствующее
    сообщение.

    Если разница между временем получения команд sleep и wake менее
    суток, пользователю выводится сообщение с указанием
    продолжительности сна. Если бот используется не впервые,
    открывается файл с данными пользователя формата .csv, где названием
    служит id пользователя. В файле ищется продолжительность сна за
    предыдущий день. Вчерашняя продолжительность сравнивается с
    сегодняшней и разница выводится пользователю.
    Пользователю выводится сообщение с предложением следующей команды.
    :param message: Ввод команды wake от пользователя
    :return: None
    """
    try:
        data[message.from_user.id]['wake_time']: datetime = datetime.now()
        data[message.from_user.id]['duration']: timedelta = (data[message.from_user.id]['wake_time']
                                                  - data[message.from_user.id]['sleep_time'])

    except KeyError:
        bot.send_message(message.chat.id, 'В прошлый раз вы забыли нажать команду /sleep.')


    if timedelta(days=1) < data[message.from_user.id]['duration']:
        bot.send_message(message.chat.id, 'В прошлый раз вы забыли нажать команду /sleep.')

    else:
        hours, minutes = (str(data[message.from_user.id]['duration']).split(':', maxsplit=2)[0],
                          str(data[message.from_user.id]['duration']).split(':', maxsplit=2)[1])
        bot.send_message(message.chat.id, f'Доброе утро!🌞 Вы спали: {hours} ч и {minutes} мин.')

        file_name: str = str(message.from_user.id) + '.csv'
        if os.path.exists(file_name):
            yesterday: datetime = datetime.now()-timedelta(days=1)

            with open(file_name, 'r', newline='') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    if row['date'] == yesterday.strftime('%d.%m.%Y'):
                        global yesterday_duration
                        yesterday_duration[message.from_user.id] = [float(i) for i in row['duration'].split(':')]

        if message.from_user.id in yesterday_duration:
            yesterday_dur_sec: float = timedelta.total_seconds(
                timedelta(hours=yesterday_duration[message.from_user.id][0],
                          minutes=yesterday_duration[message.from_user.id][1],
                          seconds=yesterday_duration[message.from_user.id][2]))
            difference: float = (timedelta.total_seconds(data[message.from_user.id]['duration'])
                              - yesterday_dur_sec)
            dif_h: float = abs(difference) // 3600
            dif_min: float = abs(difference)//60 % 60

            if difference > 0:
                bot.send_message(message.chat.id, f'Это на {int(dif_h)} ч и {int(dif_min)} мин '
                                                      f'больше, чем вчера. Так держать!')

            if difference < 0:
                bot.send_message(message.chat.id,
                                     f'Это на {int(dif_h)} ч и {int(dif_min)} мин меньше, чем вчера. '
                                     f'Желаю вам побольше сил сегодня!')

            del yesterday_duration[message.from_user.id]


        bot.send_message(message.chat.id, f'Установите качество сна по десятибальной шкале '
                                              f'с помощью команды /quality:')


@bot.message_handler(commands=['quality'])
def quality_handler(message: telebot.types) -> None:
    """
    При получении команды quality вызывает функцию get_quality.
    :param message: Ввод команды quality от пользователя
    :return: None
    """
    bot.register_next_step_handler(message, get_quality)

def get_quality(message: telebot.types) -> None:
    """
    Текст полученного от пользователя сообщения записывается как
    значение ключа 'quality' в словарь по id пользователя.
    Пользователю выводится сообщение с предложением
    следующей команды.
    :param message: Оценка пользователем качества сна по
    десятибальной шкале
    :return: None
    """
    data[message.from_user.id]['quality']: str = message.text
    bot.send_message(message.chat.id, 'Качество сна установлено. '
                                      'Создайте заметку о качестве сна с помощью команды /notes:')


@bot.message_handler(commands=['notes'])
def notes_handler(message: telebot.types) -> None:
    """
    При получении команды notes вызывает функцию get_note.
    :param message: Ввод команды notes от пользователя
    :return: None
    """
    bot.register_next_step_handler(message, get_note)

def get_note(message: telebot.types) -> None:
    """
    Текст полученного от пользователя сообщения записывается как
    значение ключа 'notes' в словарь по id пользователя. Выводится
    сообщение пользователю. Вся полученная информация выводится
    еще раз в виде резюме. Открывается (если файл существует) или
    создается файл с названием id пользователя форматом .csv,
    и туда записывается вся полученная информация. Пользователю
    выводится сообщение с предложением следующей команды.
    :param message: Заметка о сне от пользователя
    :return: None
    """
    data[message.from_user.id]['notes']: str = message.text
    bot.send_message(message.chat.id, 'Заметка сохранена.')

    hours, minutes = (str(data[message.from_user.id]['duration']).split(':', maxsplit=2)[0],
                      str(data[message.from_user.id]['duration']).split(':', maxsplit=2)[1])
    bot.send_message(message.chat.id, f'Позвольте мне резюмировать: '
                                      f'сегодня {data[message.from_user.id]['date']} вы спали '
                                      f'{hours} ч и {minutes} мин.\n'
                                      f'Качество сна: {data[message.from_user.id]['quality']}.\n'
                                      f'Заметка: {data[message.from_user.id]['notes']}.')

    file_name: str = str(message.from_user.id) + '.csv'
    if not os.path.exists(file_name):
        with open(file_name, 'w', newline='') as f:
            fieldnames = ['date', 'sleep_time', 'wake_time', 'duration', 'quality', 'notes']
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerow(data[message.from_user.id])

    else:
        with open(file_name, 'a', newline='') as f:
            fieldnames = ['date', 'sleep_time', 'wake_time', 'duration', 'quality', 'notes']
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writerow(data[message.from_user.id])

    bot.send_message(message.chat.id,
                     'Чтобы посмотреть отчет за другой день нажмите команду '
                     '/report и введите дату в формате дд.мм.гггг:')


@bot.message_handler(commands=['report'])
def report_handler(message: telebot.types) -> None:
    """
    При получении команды report вызывает функцию get_report.
    :param message: Ввод команды report от пользователя
    :return: None
    """
    bot.register_next_step_handler(message, get_report)

def get_report(message: telebot.types) -> None:
    """
    Открывается файл с названием id пользователя, в нем ищется
    информация на полученную от пользователя дату. Если информация
    найдена, она выводится пользователю, если не найдена, выводится
    соответствующее сообщение.
    :param message: Дата, на которую пользователю нужен отчет
    :return: None
    """
    date: str = message.text
    file_name: str = str(message.from_user.id) + '.csv'
    with open(file_name, 'r', newline='') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['date'] == date:
                bot.send_message(message.chat.id, f'Информация на дату {row['date']}:\n'
                                              f'Вы легли спать в {row['sleep_time'][11:16]}\n'
                                              f'Вы проснулись в {row['wake_time'][11:16]}\n'
                                              f'Длительность сна составила {row['duration'].split(':', maxsplit=2)[0]} ч и '
                                              f'{row['duration'].split(':', maxsplit=2)[1]} мин\n'
                                              f'Качество сна {row['quality']}\nЗаметка: {row['notes']}')
                global report_found
                report_found[message.from_user.id] = True

    if message.from_user.id not in report_found or report_found[message.from_user.id] == False:
        bot.send_message(message.chat.id, 'На введенную дату отчета нет.')

    report_found[message.from_user.id] = False


bot.polling(none_stop=True)
