# Инструкция по установке скрипта на сервере

В данной инструкции описаны шаги, необходимые для установки и запуска скрипта на сервере под управлением Linux Ubuntu 20.04.

### Примечания:

- в данной инструкции приведены команды для командной строки Linux. Для работы с ними в Windows можно использовать [подсистему Linux](https://g-ek.com/kak-zapustit-bash-v-windows-10) или [Windows PowerShell](https://docs.microsoft.com/ru-ru/powershell/scripting/overview?view=powershell-7.2);
- в примерах команд в фигурных скобках `{}` указаны переменные значения, которые необходимо заменить на фактические;
- в процессе выполнения приведённых команд система может запрашивать подтверждение выполняемых действий, соглашаемся, нажав `Y`, потом `Enter`.


## Подключение к серверу

Откройте терминал и выполните команду:
```
ssh {user}@{server_ip_address}
```
где {user} - имя пользователя, {server_ip_address} - ip-адрес сервера.

По требованию сервера введите пароль.

## Установка ПО

1. Скрипт написан на Python3.10, устанавливаем его командой:
```
sudo apt-get install python3.10
```

2. Все данные приложения размещены на удалённом репозитории Git, устанавливаем пакет для работы с ним:
```
sudo apt install git
```

3. Устанавливаем средство работы с виртуальным окружением virtualenv:
```
pip install virtualenv
```


## Установка файлов приложения

1. Переходим в директорию Git на сервере командой
```
cd ~/git
```
2. Скачиваем репозиторий на сервер:
```
git clone https://github.com/smalldirtybird/sendpulse_lptracker_integration.git
```
3. Проверяем результат:
```
ls -lah
```
Отобразится список папок с репозиториями, в котором должна присутствовать `sendpulse_lptracker_integration`.


## Настройка приложения

1. Переходим в директорию с проектом:
```
cd ~/git/sendpulse_lptracker_integration
```
и устанавливаем виртуальное окружение командой
```
virtualenv -p /usr/bin/python3.10 --pip 22.2.2 venv

```
Далее активируем окружение:
```
source venv/bin/activate
```
и устанавливаем библиотеки:
```
pip install -r requirements.txt
```

2. Создаём файл .env для переменных окружения с помощью встроенного текстового редактора nano:
```
nano .env
```
В файл вносим следующие строки:
``` python
LPTRACKER_LOGIN = {email_главного_аккаунта_LPTracker}
LPTRACKER_PASSWORD = {пароль_главного_аккаунта_LPTracker}
SP_ID = {ID_пользователя_API_SendPulse}
SP_SECRET = {Secret_пользователя_API_SendPulse}
```
Данные Sendpulse берём [со вкладки API страницы настроек акканута](https://login.sendpulse.com/settings/#api).
Комбинацией `Ctrl + X` выходим из редактора, подтверждаем сохранение `Y` и имя файла `Enter`.

Пример заполненного файла:
``` python
LPTRACKER_LOGIN = example@email.co
LPTRACKER_PASSWORD = eXaMPlepWd
SP_ID = bsbo1m9e6tae1xct3dbo7n9oetcc7o0p2y5
SP_SECRET = s1o2maedt4e7x7tdd1o6n8oet0ccobp3y7
```

2. Создаём файл конфигурации с настройками скрипта. Для этого запускаем кофигуратор следующей командой:
```
python3 set_default_config.py
```
По итогу будет создан файл config.json с базовыми настройками, а так же в терминале будут показаны параметры проектов и воронок LPTracker и SendPulse.
Откройте файл командой
```
nano config.json
```
Проверяем корректность данных и при необходимости меняем. Ниже приведено пояснение к содержимому файла:
``` json
{
  "time_reserve": 60, # запас времени в секундах при запросе нового токена
  "delay_time": 1, # время задержки перед запуском нового цикла скрипта
  "lpt_token_lifetime": 86400, # время жизни токена LPTracker в секундах
  "lpt_project_id": 94698, # id проекта LPTracker
  "lpt_new_lead_step": 1708039, # id шага воронки LPTracker, в который попадает сделка при переносе
  "lpt_lead_owner_id": 33327, # id владельца сделки в LPTracker
  "lpt_callback": false, # запрос обратного звонка
  "sp_search_status_ids": [1], # массив с id статусов сделок Sendpulse, по которым ведётся поиск новых сделок
  "sp_step_ids": [142896], # массив с id шагов воронки Sendpulse, по которым ведётся поиск новых сделок
  "sp_pipeline_ids": [43308], # массив с id воронки Sendpulse, в которым ведётся поиск новых сделок
  "sp_success_status": 3, # id статуса сделок Sendpulse, в который переводится сделка при успешном переносе
  "sp_fail_status": 2, # id статуса сделок Sendpulse, в который переводится сделка при неуспешном переносе
  "exception_delay": 60 # задержка перед возобновлением работы скрипта при возникновении ошибок в секундах
}
```
Выходим, сохраняем и подтверждаем `Ctrl + X`, `Y`, `Enter`.

ВНИМАНИЕ: повторный запуск команды `set_default_config.py` перезапишет все данные в файле базовыми, все изменения будут удалены.


## Запуск и остановка скрипта

#### Для запуска скрипта последовательно выполните следующие команды:

1. Переходим в папку с репозиторием:
```
cd git/sendpulse_lptracker_integration/
```
2. Активируем виртуальное окружение:
```
source venv/bin/activate
```
3. Запускаем скрипт:
```
python3 main.py
```
Так же скрипт можно запустить в фоновом режиме, чтобы не блокировать ввод с терминала:
```
python3 main.py &
```
### Остановка работы скрипта

Если скрипт запущен в фоновом режиме, выполните команду
```
fg
```
Далее, выключаем скрипт комбинацией `Ctrl + C`


## Обновление скрипта

Чтобы скачать последнюю версию скрипта с репозитория, выполняем следующие команды:

1. Переходим в папку с репозиторием:
```
cd git/sendpulse_lptracker_integration/
```
2. Скачиваем все обновления:
```
git pull
```