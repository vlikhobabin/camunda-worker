# Сервисные инструменты Universal Camunda Worker

Каталог содержит вспомогательные скрипты для управления, мониторинга и диагностики системы Universal Camunda Worker.

## Скрипты

### start_process.py

Запуск новых экземпляров процессов в Camunda через REST API.

#### Возможности

- Запуск процессов по ключу процесса
- Передача переменных в JSON и key=value форматах
- Установка business key для уникальной идентификации
- Выбор конкретной версии процесса
- Dry-run режим для тестирования без фактического запуска
- Просмотр информации о процессе
- Список всех версий процесса

#### Использование

```bash
# Простой запуск процесса
python start_process.py ProcessKey

# Запуск с переменными (key=value формат)
python start_process.py ProcessKey --variables "userName=John,amount=100,approved=true"

# Запуск с переменными (JSON формат)  
python start_process.py ProcessKey --variables '{"userName": "John", "amount": 100}'

# Запуск с business key
python start_process.py ProcessKey --business-key "ORDER-123"

# Запуск конкретной версии
python start_process.py ProcessKey --version 2

# Просмотр информации о процессе
python start_process.py ProcessKey --info

# Список всех версий процесса
python start_process.py ProcessKey --list-versions

# Тестирование без запуска
python start_process.py ProcessKey --variables "test=value" --dry-run
```

#### Примеры переменных

```bash
# Строковые переменные
--variables "userName=John Doe,email=john@example.com"

# Смешанные типы
--variables "name=John,age=30,active=true,score=95.5"

# JSON объекты
--variables '{"user": {"name": "John", "age": 30}, "config": {"debug": true}}'
```

### camunda_processes.py

Получение детальной информации о процессах, экземплярах и задачах в Camunda.

#### Возможности

- Просмотр определений процессов (BPMN модели)
- Мониторинг экземпляров процессов (активных и завершенных)
- Анализ внешних задач (External Tasks)
- Просмотр пользовательских задач (User Tasks)
- Общая статистика системы
- Экспорт данных в JSON формат

#### Использование

```bash
# Полная информация о системе
python camunda_processes.py

# Только статистика
python camunda_processes.py --stats

# Только внешние задачи
python camunda_processes.py --external-tasks

# Только определения процессов
python camunda_processes.py --definitions

# Только активные экземпляры
python camunda_processes.py --instances

# Все экземпляры (включая завершенные)
python camunda_processes.py --instances --all-instances

# Только пользовательские задачи
python camunda_processes.py --user-tasks

# Экспорт в JSON файл
python camunda_processes.py --export camunda_data.json

# Комбинирование опций
python camunda_processes.py --stats --external-tasks --export stats.json
```

#### Выходная информация

- **Определения процессов**: ID, ключ, название, версия, статус развертывания
- **Экземпляры процессов**: ID, ключ процесса, business key, статус, даты
- **Внешние задачи**: ID, топик, процесс, активность, worker ID, статус блокировки
- **Пользовательские задачи**: ID, название, назначение, процесс, даты
- **Статистика**: количество процессов, экземпляров, задач по статусам

### check_queues.py

Мониторинг состояния очередей RabbitMQ.

#### Возможности

- Просмотр всех очередей проекта
- Количество сообщений в каждой очереди
- Статус подключения к RabbitMQ
- Проверка инфраструктуры очередей

#### Использование

```bash
# Проверка всех очередей
python check_queues.py

# Непрерывный мониторинг (каждые 5 секунд)
python check_queues.py --watch

# Показать только очереди с сообщениями
python check_queues.py --non-empty

# Детальная информация
python check_queues.py --verbose
```

#### Выходная информация

```
=== СОСТОЯНИЕ ОЧЕРЕДЕЙ RABBITMQ ===

Подключение: ✓ Успешно (rmq.example.com:5672)

Очереди задач:
  ├── bitrix24.queue: 3 сообщения
  ├── openproject.queue: 0 сообщений  
  ├── 1c.queue: 1 сообщение
  ├── python-services.queue: 12 сообщений
  └── default.queue: 0 сообщений

Очереди ответов:
  └── camunda.responses.queue: 2 сообщения

Очереди ошибок:
  └── errors.camunda_tasks.queue: 0 сообщений

Итого: 18 сообщений в 6 очередях
```

### unlock_task.py

Разблокировка заблокированных задач в Camunda.

#### Возможности

- Разблокировка задач по ID
- Массовая разблокировка задач
- Разблокировка по топику
- Разблокировка по worker ID
- Безопасный режим с подтверждением

#### Использование

```bash
# Разблокировка конкретной задачи
python unlock_task.py --task-id abc123-def456-ghi789

# Разблокировка нескольких задач
python unlock_task.py --task-id id1,id2,id3

# Разблокировка всех задач топика
python unlock_task.py --topic bitrix_create_task

# Разблокировка задач конкретного worker
python unlock_task.py --worker-id universal-worker

# Разблокировка всех заблокированных задач (с подтверждением)
python unlock_task.py --all --confirm

# Просмотр заблокированных задач без разблокировки
python unlock_task.py --list

# Принудительная разблокировка без подтверждения
python unlock_task.py --task-id abc123 --force
```

#### Безопасность

Скрипт включает несколько уровней защиты:
- Подтверждение для массовых операций
- Проверка существования задач
- Валидация ID задач
- Логирование всех операций

### worker_diagnostics.py

Комплексная диагностика системы Universal Camunda Worker.

#### Возможности

- Проверка подключения к Camunda
- Проверка подключения к RabbitMQ
- Анализ конфигурации
- Тестирование API endpoints
- Проверка состояния очередей
- Валидация маппинга топиков

#### Использование

```bash
# Полная диагностика
python worker_diagnostics.py

# Быстрая проверка подключений
python worker_diagnostics.py --quick

# Проверка только Camunda
python worker_diagnostics.py --camunda-only

# Проверка только RabbitMQ  
python worker_diagnostics.py --rabbitmq-only

# Детальный отчет
python worker_diagnostics.py --detailed

# Экспорт результатов в файл
python worker_diagnostics.py --export diagnostics_report.json
```

#### Проверяемые компоненты

1. **Camunda Engine**
   - Доступность REST API
   - Аутентификация
   - Список определений процессов
   - Количество активных экземпляров
   - Внешние задачи

2. **RabbitMQ**
   - Подключение к серверу
   - Состояние очередей
   - Проверка exchanges
   - Права доступа

3. **Конфигурация**
   - Валидация параметров
   - Проверка маппинга топиков
   - Анализ routing rules

### status_check.py

Быстрая проверка состояния всех компонентов системы.

#### Возможности

- Статус Worker процесса
- Статус Response Handler
- Общая статистика обработки
- Время работы системы
- Последние ошибки

#### Использование

```bash
# Статус системы
python status_check.py

# Краткий статус
python status_check.py --brief

# Статус с деталями производительности
python status_check.py --performance

# JSON формат (для скриптов)
python status_check.py --json
```

## Общие параметры

Все скрипты поддерживают общие параметры:

```bash
# Помощь по использованию
python script_name.py --help

# Подробный вывод
python script_name.py --verbose

# Тихий режим (только ошибки)
python script_name.py --quiet

# Использование альтернативного config файла
python script_name.py --config custom_config.py
```

## Конфигурация

Все скрипты используют настройки из основного файла `config.py`. Для переопределения параметров:

1. Создайте файл `.env` в корне проекта
2. Установите переменные окружения
3. Или используйте параметр `--config` для указания альтернативного файла

## Логирование

Все скрипты ведут логи в:
- Консоль (с цветовой подсветкой)
- Файл `logs/tools.log` (опционально)
- Системный журнал (при запуске как сервис)

## Примеры использования

### Базовый мониторинг

```bash
# Ежедневная проверка системы
python worker_diagnostics.py --detailed
python check_queues.py
python camunda_processes.py --stats
```

### Обслуживание

```bash
# Очистка заблокированных задач
python unlock_task.py --list
python unlock_task.py --all --confirm

# Перезапуск процесса для тестирования
python start_process.py TestProcess --dry-run
python start_process.py TestProcess --variables "test=true"
```

### Отладка проблем

```bash
# При проблемах с задачами
python camunda_processes.py --external-tasks
python check_queues.py --non-empty
python unlock_task.py --topic problem_topic

# При проблемах с подключением
python worker_diagnostics.py --quick
python status_check.py --performance
```

## Интеграция

Скрипты можно интегрировать в:
- Cron jobs для автоматического мониторинга
- CI/CD pipeline для проверки деплоймента
- Мониторинговые системы (Nagios, Zabbix)
- Скрипты резервного копирования

### Пример cron job

```bash
# Проверка каждые 5 минут
*/5 * * * * /path/to/python /path/to/check_queues.py --brief >> /var/log/camunda_monitor.log

# Ежедневный отчет
0 9 * * * /path/to/python /path/to/worker_diagnostics.py --export /reports/daily_$(date +\%Y\%m\%d).json
``` 