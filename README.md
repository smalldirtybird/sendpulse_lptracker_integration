# Интеграция сервисов [SendPulse](https://login.sendpulse.com) и [LPTracker](https://my.lptracker.ru)
После запуска скрипт в автоматическом режиме находит новые сделки в воронке [SendPulse](https://login.sendpulse.com) и переносит их в [LPTracker](https://my.lptracker.ru).

## Подготовка

Скачайте репозиторий на компьютер любым удобным способом и следуйте инструкциям ниже.

### Настройка окружения

1. Убедитесь, что на компьютере установлен Python 3. При необходимости скачайте с [официального сайта](https://www.python.org/downloads/). Работа скрипта протестирована на версии Python 3.10.

2. Установите необходимые для работы пакеты с помощью команды:
```
pip install -r requirements.txt
```
Просто скопируйте и запустите из командной строки.

3. Создайте в корневой папке репозитория файл .env (для этого отлично подойдёт приложение [Notepad++](https://notepad-plus-plus.org/downloads/)). Данный файл предназначен для хранения чувствительных данных.

4. Перейдите на страницу настроек аккаунта SendPulse, [вкладку "API"](https://login.sendpulse.com/settings/#api) и добавьте в файл .env следующие строки:
```
SP_ID = ID_аккаунта_SendPulse
SP_SECRET = Secret_аккаунта_SendPulse
```

5. Добавьте в файл .env следующие строки:
```
LPTRACKER_LOGIN = email_главного_аккаунта_LPTracker
LPTRACKER_PASSWORD = пароль_главного_аккаунта_LPTracker
```
ВАЖНО: Перед запуском нужно написать боту любое сообщение, чтобы он "подхватил" id чата. Это нужно делать только при первом запуске.

Заполненный .env файл должен выглядеть так:
``` python
LPTRACKER_LOGIN = example@email.co
LPTRACKER_PASSWORD = eXaMPlepWd
SP_ID = bsbo1m9e6tae1xct3dbo7n9oetcc7o0p2y5
SP_SECRET = s1o2maedt4e7x7tdd1o6n8oet0ccobp3y7

```


## Настройка файла конфигурации

Создайте и заполните файл `config.json` по образцу ниже. Этот файл содержит настройки, необходимые для работы скрипта. Ниже приведено описание полей и значений данного файла.
Изменять ключи в файле категорически запрещено, это неизбежно приведёт к поломке скрипта.
```json
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

## Запуск

После выполнения всех описанных выше действий, запустите скрипт из терминала с помощью команды:
```
python3 main.py
```
Для запуска скрипта в фоновом режиме добавьте к команде символ ` &`:
```
python3 main.py &
```
Для вывода скрипта из фонового режима используйте команду `fb`.
Для прекращения работы используйте комбинацию `Ctrl + C`.
