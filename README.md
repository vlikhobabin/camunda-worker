# Universal Camunda Worker

Universal Worker для обработки External Tasks от Camunda через RabbitMQ с Stateless архитектурой.

## Описание

Universal Camunda Worker - это независимый модуль для интеграции Camunda BPM с внешними системами через RabbitMQ. Реализует Stateless архитектуру с длительными блокировками задач.

### Основные возможности

- Мониторинг всех External Tasks от процессов Camunda
- Автоматическое определение целевой системы по топику задачи
- Отправка задач в соответствующие очереди RabbitMQ
- Асинхронное завершение задач через Response Handler
- Блокировка задач на длительный период (по умолчанию 10 минут)
- Устойчивость к перезагрузкам и сбоям
- Детальное логирование и мониторинг

### Поддерживаемые системы

- **Bitrix24** - CRM и управление проектами
- **OpenProject** - управление проектами  
- **1C** - учетные системы
- **Python Services** - специализированные сервисы

## Архитектура

### Компоненты системы

1. **Camunda Worker** - получение задач из Camunda и отправка в RabbitMQ
2. **Response Handler** - обработка ответов и завершение задач в Camunda
3. **RabbitMQ Client** - взаимодействие с очередями сообщений

### Workflow обработки

1. Worker получает External Task от Camunda
2. Блокирует задачу на указанный период
3. Определяет целевую систему по топику
4. Отправляет задачу в соответствующую очередь RabbitMQ
5. Внешняя система обрабатывает задачу (может занимать длительное время)
6. Система отправляет результат в очередь ответов
7. Response Handler получает ответ и завершает задачу в Camunda

### Организация очередей RabbitMQ

**Исходящие задачи (Exchange: camunda.external.tasks)**
- `bitrix24.queue` - задачи для Bitrix24
- `openproject.queue` - задачи для OpenProject  
- `1c.queue` - задачи для 1C
- `python-services.queue` - задачи для Python сервисов
- `default.queue` - все остальные задачи

**Ответные сообщения (Exchange: camunda.task.responses)**
- `camunda.responses.queue` - ответы от всех систем

## Установка

### Требования

- Python 3.8+
- RabbitMQ
- Camunda BPM Platform
- Доступ к REST API Camunda

### Быстрая установка

```bash
git clone <repository-url>
cd camunda-worker
pip install -r requirements.txt
```

### Конфигурация

Создайте файл `.env` на основе `config.env.example`:

```bash
# Camunda настройки
CAMUNDA_BASE_URL=https://your-camunda-server.com/engine-rest
CAMUNDA_WORKER_ID=universal-worker
CAMUNDA_MAX_TASKS=10
CAMUNDA_LOCK_DURATION=600000
CAMUNDA_AUTH_USERNAME=your_username
CAMUNDA_AUTH_PASSWORD=your_password

# RabbitMQ настройки  
RABBITMQ_HOST=your-rabbitmq-host.com
RABBITMQ_USERNAME=your_username
RABBITMQ_PASSWORD=your_password

# Логирование
LOG_LEVEL=INFO
```

## Запуск

### Основные команды

```bash
# Запуск через main.py (оба компонента)
python main.py

# Запуск только Worker
python camunda_worker.py

# Запуск только Response Handler
python response_handler.py
```

### Как сервис

```bash
# Создание systemd сервиса
sudo cp camunda-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable camunda-worker
sudo systemctl start camunda-worker

# Управление сервисом
systemctl status camunda-worker
systemctl restart camunda-worker
journalctl -u camunda-worker -f
```

## Конфигурация

### Основные параметры

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `CAMUNDA_BASE_URL` | URL REST API Camunda | `https://camunda.example.com/engine-rest` |
| `CAMUNDA_WORKER_ID` | Идентификатор Worker | `universal-worker` |
| `CAMUNDA_MAX_TASKS` | Максимум задач за запрос | `10` |
| `CAMUNDA_LOCK_DURATION` | Время блокировки (мс) | `600000` (10 мин) |
| `RABBITMQ_HOST` | Хост RabbitMQ | `localhost` |
| `RABBITMQ_PORT` | Порт RabbitMQ | `5672` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |

### Маппинг топиков

Worker автоматически определяет целевую систему по названию топика:

```python
# Примеры маппинга
"bitrix_create_task" → bitrix24.queue
"op_create_project" → openproject.queue  
"1c_sync_data" → 1c.queue
"send_email" → python-services.queue
```

Полный список маппингов определен в `config.py` в классе `RoutingConfig`.

## Мониторинг

### Логи

Система ведет несколько типов логов:

- **Основные логи**: `logs/camunda_worker.log`
- **Логи ошибок**: `logs/camunda_worker_errors.log`
- **Системные логи**: через `journalctl -u camunda-worker`

### Статистика

Worker выводит статистику каждые 30 секунд:

```
Monitor - Uptime: 3600s | Обработано: 150 | Успешно: 147 | Ошибки: 3
```

### Проверка состояния

Используйте сервисные скрипты из каталога `tools/`:

```bash
# Статус очередей RabbitMQ
python tools/check_queues.py

# Информация о процессах Camunda
python tools/camunda_processes.py --stats

# Диагностика Worker
python tools/worker_diagnostics.py
```

## API для внешних систем

### Формат ответного сообщения

Внешние системы должны отправлять ответы в очередь `camunda.responses.queue`:

```json
{
  "task_id": "task-uuid",
  "response_type": "complete",
  "worker_id": "universal-worker",
  "variables": {
    "result": {"value": "success", "type": "String"},
    "data": {"value": "{\"key\": \"value\"}", "type": "String"}
  }
}
```

### Типы ответов

- `complete` - успешное завершение задачи
- `failure` - ошибка с возможностью повтора
- `bpmn_error` - BPMN ошибка для обработки в процессе

## Разработка

### Структура проекта

```
camunda-worker/
├── main.py                 # Точка входа
├── camunda_worker.py       # Основной Worker
├── response_handler.py     # Обработчик ответов
├── rabbitmq_client.py      # RabbitMQ клиент
├── config.py              # Конфигурация
├── requirements.txt       # Зависимости
├── tools/                 # Сервисные скрипты
│   ├── start_process.py   # Запуск процессов
│   ├── camunda_processes.py # Мониторинг процессов
│   ├── check_queues.py    # Проверка очередей
│   └── unlock_task.py     # Разблокировка задач
└── logs/                  # Файлы логов
```

### Зависимости

- `camunda-external-task-client-python3` - клиент для Camunda
- `pika` - клиент для RabbitMQ
- `pydantic` - валидация конфигурации
- `requests` - HTTP запросы к Camunda API
- `loguru` - расширенное логирование

## Troubleshooting

### Частые проблемы

1. **Задачи не обрабатываются**: Проверьте подключение к Camunda и маппинг топиков
2. **Ошибки RabbitMQ**: Убедитесь в корректности credentials и доступности сервера
3. **Задачи зависают**: Проверьте время блокировки и работу Response Handler

### Диагностика

```bash
# Проверка подключений
python tools/worker_diagnostics.py

# Разблокировка зависших задач
python tools/unlock_task.py --task-id <task-id>

# Просмотр активных процессов
python tools/camunda_processes.py --instances
```

## Лицензия

MIT License 