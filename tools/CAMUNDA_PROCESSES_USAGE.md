# Скрипт получения списка процессов Camunda

## Описание
`camunda_processes.py` - сервисный скрипт для получения детальной информации о процессах в Camunda через REST API.

## Возможности
- 📋 **Определения процессов** - список всех BPMN моделей
- 🏃 **Экземпляры процессов** - активные и завершенные процессы
- ⚡ **Внешние задачи** - External Tasks ожидающие обработки
- 👤 **Пользовательские задачи** - Human Tasks для пользователей
- 📊 **Статистика** - общий обзор системы
- 📁 **Экспорт в JSON** - сохранение данных в файл

## Быстрый старт

### Показать всю информацию:
```bash
python camunda_processes.py
```

### Показать только статистику:
```bash
python camunda_processes.py --stats
```

### Экспортировать данные в JSON:
```bash
python camunda_processes.py --export camunda_data.json
```

## Все доступные команды

| Команда | Описание |
|---------|----------|
| `python camunda_processes.py` | Показать всю информацию |
| `python camunda_processes.py --stats` | Только общая статистика |
| `python camunda_processes.py --definitions` | Только определения процессов |
| `python camunda_processes.py --instances` | Только активные экземпляры |
| `python camunda_processes.py --instances --all-instances` | Все экземпляры (включая завершенные) |
| `python camunda_processes.py --external-tasks` | Только внешние задачи |
| `python camunda_processes.py --user-tasks` | Только пользовательские задачи |
| `python camunda_processes.py --export file.json` | Экспорт всех данных в JSON |

## Примеры вывода

### Общая статистика:
```
🔗 Подключение к Camunda: https://camunda.eg-holding.ru
🔐 Аутентификация: Включена

================================================================================
🏗️  ИНФОРМАЦИЯ О ДВИЖКЕ CAMUNDA
================================================================================
Version: 7.21.0
Date: 2024-11-15

================================================================================
📊 ОБЩАЯ СТАТИСТИКА
================================================================================
Определений процессов: 5
Активных экземпляров: 12
Внешних задач: 8
Пользовательских задач: 3

Внешние задачи по топикам:
  bitrix_create_task: 3
  send_email: 2
  telegram_notify: 2
  yandex_disk: 1

Активные экземпляры по процессам:
  project_management: 7
  document_approval: 3
  user_registration: 2
```

### Внешние задачи:
```
================================================================================
⚡ ВНЕШНИЕ ЗАДАЧИ (8)
================================================================================

1. Task ID: abc123-def456-ghi789
   Topic Name: bitrix_create_task
   Worker ID: universal-worker
   Process Instance ID: pi-123456
   Process Definition Key: project_management
   Activity ID: CreateBitrixTask
   Retries: 3
   Priority: 50
   Lock Expiration: 2025-12-15 10:30:00
```

## Настройка
Скрипт использует конфигурацию из `config.py`:
- URL Camunda: `camunda_config.base_url`
- Аутентификация: `camunda_config.auth_username` / `camunda_config.auth_password`

## Устранение неполадок

### Ошибка подключения:
```
❌ Ошибка при запросе к https://camunda.eg-holding.ru/engine-rest/version: Connection refused
```
**Решение:** Проверьте доступность Camunda сервера и правильность URL в `config.py`

### Ошибка аутентификации:
```
❌ Ошибка при запросе к https://camunda.eg-holding.ru/engine-rest/version: 401 Unauthorized
```
**Решение:** Проверьте логин/пароль в `config.py` или файле `.env`

### SSL ошибки:
Скрипт автоматически отключает проверку SSL сертификатов для самоподписанных сертификатов.

## Интеграция с другими инструментами

### Мониторинг через cron:
```bash
# Каждые 5 минут сохранять статистику
*/5 * * * * cd /opt/camunda-worker && ./venv/bin/python camunda_processes.py --stats >> /var/log/camunda-monitoring.log
```

### Экспорт для анализа:
```bash
# Ежедневный экспорт данных
python camunda_processes.py --export "camunda_$(date +%Y%m%d).json"
```

### Автоматическое оповещение:
```bash
# Отправка уведомления при большом количестве задач
EXTERNAL_TASKS=$(python camunda_processes.py --external-tasks | grep -c "Task ID")
if [ "$EXTERNAL_TASKS" -gt 10 ]; then
    echo "Внимание: $EXTERNAL_TASKS внешних задач в очереди" | mail -s "Camunda Alert" admin@company.com
fi
```

## Требования
- Python 3.7+
- requests >= 2.25.0
- Доступ к Camunda REST API

## Дополнительные возможности

### Фильтрация по процессам:
Можно легко добавить фильтрацию по конкретным процессам, изменив параметры запроса в методе `get_process_instances()`.

### Расширенная статистика:
Скрипт можно расширить для получения дополнительной информации, такой как:
- История выполнения задач
- Метрики производительности
- Анализ узких мест в процессах

---

**💡 Совет:** Используйте комбинацию параметров для получения нужной информации. Например, для мониторинга только внешних задач используйте `--external-tasks --stats`. 