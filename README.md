# SleepyBot
Бот, помогающий отслеживать время и качество сна.
Умеет выполнять 5 команд: sleep, wake, quality, notes, report.

Команда **sleep** - бот запоминает время, когда пользователь ложится спать.

Команда **wake** - бот запоминает время, когда пользователь просыпается, вычитает из этого времени время отхода ко сну и выводит кол-во часов и минут сна пользователю. Если это не первый день использования бота, бот сравнивает количество времени сна с предыдущим днем и выводит разницу пользователю. 

Команда **quality** - считывает введенную пользователем отметку (по десятибальной шкале) и запоминает ее.

Команда **notes** - считывает введенную пользователем общую информацию о качестве сна и запоминает ее.

После выполнения этих команд бот еще раз выводит всю полученную информацию пользователю и сохраняет ее в файл csv.

Команда **report** - ищет данные на введеную пользователем дату и, если таковые находятся, выводит их на экран.
***
Для запуска бота понадобится установка библиотеки pyTelegramBotAPI. Токен скрыт в переменной окружения.
***
Бота можно протестировать, найдя по нику @SleepySupporter_bot.

