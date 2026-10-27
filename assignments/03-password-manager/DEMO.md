# Демонстрация для сдачи

## Мастер-пароль

```text
StudyDemo123!
```

## Скриншоты (3 этапа)

```powershell
cd D:\learning-assignments\assignments\03-password-manager
pip install mss
python capture_real_screenshots.py
```

| Файл | Содержание |
|------|------------|
| `01_master_password_login.png` | вход / установка мастер-пароля |
| `02_first_account_generated.png` | первая учётка `Gmail` с `--generate` |
| `03_two_accounts_passwords.png` | `Telegram` + `list` + `get` для обеих учёток |

Закройте `password_manager.py menu`, если открыт, чтобы не блокировался `passwords.db`.

## Ручная проверка

```powershell
python password_manager.py list
python password_manager.py --master-password StudyDemo123! add Gmail user@gmail.com --generate --length 16
python password_manager.py --master-password StudyDemo123! get Gmail
```
