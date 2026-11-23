# HTTP-запросы: requests, JSON и restcountries

Учебный проект по материалам урока: **venv**, **requests**, меню GET/POST, API стран, цветной вывод **colorama**.

## Структура

| Файл | Назначение |
|------|------------|
| `main.py` | Меню: GET, POST, GET по стране, выход |
| `country_info.py` | Ввод страны → запрос к API → форматированный цветной вывод |
| `requirements.txt` | `requests`, `colorama` |

## Запуск

```powershell
cd assignments/11-http-requests-api
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Меню запросов

```powershell
python main.py
```

- **1** — GET (пример: `https://dog.ceo/api/breeds/image/random`)
- **2** — POST (по умолчанию `https://httpbin.org/post`)
- **3** — страна через [restcountries.com](https://restcountries.com/)
- **4** — выход

### Красивый вывод о стране

```powershell
python country_info.py
```

Введите, например: `Italy`, `Russia`, `Japan`.

> **Про API:** в коде по-прежнему URL с урока `restcountries.com/v3.1/name/...`.  
> Сервис сейчас отвечает про deprecation; модуль `api_client.py` тогда подгружает 
> открытый JSON с той же структурой полей, чтобы задание работало без правок вручную.

## Задание

1. Сделать запросы **вручную** (браузер / Postman) и **через программу**.
2. Получить ответ в формате **JSON**.
3. Выделить **2–3 ключевых поля** (в `country_info.py` в конце показан пример: `name.common`, `capital`, `population`).

Для погоды с полем вроде `main_temp` можно аналогично разобрать JSON другого API — логика та же: `response.json()` и доступ по ключам.

## Сдача

Папка в репозитории `learning-assignments`: `assignments/11-http-requests-api`.  
В архив не включать `venv/`.