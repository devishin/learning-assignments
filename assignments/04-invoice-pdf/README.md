# Генератор PDF-счетов

Учебный CLI-скрипт: выбор CSV/JSON + HTML-шаблона → PDF в `/output`.

## Структура

```
04-invoice-pdf/
├── main.py
├── data_loader.py
├── pdf_service.py
├── platform_utils.py
├── data/
├── templates/
├── fonts/
└── output/
```

## Установка

```powershell
cd D:\learning-assignments\assignments\04-invoice-pdf
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### WeasyPrint на Windows

1. Установите зависимости Python: `pip install -r requirements.txt`
2. Установите **GTK3 Runtime** для WeasyPrint:  
   https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows  
   Или: `winget install tschoonj.GTKForWindows`  
   При генерации PDF скрипт добавляет `GTK3-Runtime Win64\bin` в PATH (Windows).

### WeasyPrint на macOS

```bash
brew install pango libffi
pip install -r requirements.txt
```

### Шрифт для кириллицы

Скопируйте `DejaVuSans.ttf` в папку `fonts/`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\download_font.ps1
```

## Итоговое задание (упрощённое)

| Требование | Файл |
|------------|------|
| CSV 3–5 строк (товар, цена, количество) | `data/products.csv` |
| HTML с `{{ product }}`, `{{ price }}`, `{{ qty }}` | `templates/product_simple.html` |
| CLI → PDF в `output/` + автооткрытие | `generate_pdf.py` |

```powershell
python generate_pdf.py
```

Расширенный сценарий со счетами (CSV/JSON + Jinja2): `python main.py`.

## Запуск (счета)

```powershell
python main.py
```

## Сценарий

1. Показываются файлы в `data/` и шаблоны в `templates/`.
2. Вы выбираете один файл данных и один HTML-шаблон.
3. Выбираете `invoice id`.
4. PDF сохраняется в `output/` и открывается автоматически.

## macOS

```bash
python3 main.py
```

PDF открывается через команду `open`.
