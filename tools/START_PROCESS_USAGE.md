# Скрипт запуска экземпляров процессов Camunda

## Описание
`start_process.py` - сервисный скрипт для запуска новых экземпляров процессов в Camunda через REST API.

## Возможности
- 🚀 **Запуск процессов по ключу** - создание новых экземпляров BPMN процессов
- 📝 **Передача переменных** - поддержка JSON и key=value форматов
- 🔑 **Business Key** - уникальный идентификатор для бизнес-логики
- 🎯 **Выбор версии** - запуск конкретной версии процесса
- 📋 **Информация о процессе** - просмотр метаданных без запуска
- 🧪 **Dry-run режим** - тестирование без фактического запуска
- 📋 **Список версий** - просмотр всех версий процесса

## Быстрый старт

### Простой запуск процесса:
```bash
python start_process.py TestProcess
```

### Запуск с переменными:
```bash
python start_process.py TestProcess --variables "userName=John,amount=100"
```

### Просмотр информации о процессе:
```bash
python start_process.py TestProcess --info
```

## Все доступные команды

| Команда | Описание |
|---------|----------|
| `python start_process.py ProcessKey` | Простой запуск процесса |
| `python start_process.py ProcessKey --info` | Информация о процессе без запуска |
| `python start_process.py ProcessKey --list-versions` | Показать все версии процесса |
| `python start_process.py ProcessKey --variables "key=value"` | Запуск с переменными (key=value) |
| `python start_process.py ProcessKey --variables '{"key": "value"}'` | Запуск с переменными (JSON) |
| `python start_process.py ProcessKey --business-key "BK-123"` | Запуск с business key |
| `python start_process.py ProcessKey --version 2` | Запуск конкретной версии |
| `python start_process.py ProcessKey --dry-run` | Проверка данных без запуска |

## Форматы переменных

### 1. Key=Value формат (простой)
```bash
python start_process.py TestProcess --variables "userName=John,amount=100,approved=true"
```

**Поддерживаемые типы:**
- `userName=John` → String
- `amount=100` → Integer
- `price=19.99` → Double
- `approved=true` → Boolean
- `approved=false` → Boolean

### 2. JSON формат (расширенный)
```bash
python start_process.py TestProcess --variables '{"userName": "John", "amount": 100, "metadata": {"source": "api"}}'
```

**Примеры JSON переменных:**
```json
{
  "userName": "John Doe",
  "amount": 1500,
  "approved": true,
  "tags": ["urgent", "priority"],
  "metadata": {
    "source": "web-form",
    "timestamp": "2024-12-15T10:30:00Z"
  }
}
```

## Примеры использования

### 1. Простой запуск без переменных
```bash
python start_process.py TestProcess
```

**Вывод:**
```
🔗 Подключение к Camunda: https://camunda.eg-holding.ru
🔐 Аутентификация: Включена
🔍 Поиск процесса 'TestProcess'...

================================================================================
📋 ИНФОРМАЦИЯ О ПРОЦЕССЕ
================================================================================
Название: TestProcess
Ключ: TestProcess
ID: TestProcess:3:b39c5036-55b6-11f0-a3a6-00b436387543
Версия: 3

🚀 Готов к запуску процесса 'TestProcess'
Запустить процесс? (Y/n): Y

⏳ Запуск процесса...

================================================================================
🚀 ЭКЗЕМПЛЯР ПРОЦЕССА СОЗДАН
================================================================================
ID экземпляра: 12345-67890-abcde
Business Key: N/A
Process Definition ID: TestProcess:3:b39c5036-55b6-11f0-a3a6-00b436387543

🔗 Ссылки:
Cockpit: https://camunda.eg-holding.ru/camunda/app/cockpit/default/#/process-instance/12345-67890-abcde
Tasklist: https://camunda.eg-holding.ru/camunda/app/tasklist/default/

✅ Операция завершена успешно
```

### 2. Запуск с переменными и business key
```bash
python start_process.py TestProcess \
  --variables "userName=John,amount=1500,approved=true" \
  --business-key "ORDER-2024-001"
```

### 3. Запуск с JSON переменными
```bash
python start_process.py TestProcess \
  --variables '{"order": {"id": 123, "items": ["laptop", "mouse"]}, "priority": "high"}'
```

### 4. Запуск конкретной версии
```bash
python start_process.py TestProcess --version 2 --variables "test=true"
```

### 5. Dry-run тестирование
```bash
python start_process.py TestProcess \
  --variables "userName=TestUser,amount=100" \
  --business-key "TEST-123" \
  --dry-run
```

**Вывод dry-run:**
```
🧪 DRY RUN - Данные для отправки:
{
  "variables": {
    "userName": "TestUser",
    "amount": 100
  },
  "businessKey": "TEST-123"
}
```

### 6. Просмотр всех версий процесса
```bash
python start_process.py TestProcess --list-versions
```

**Вывод:**
```
📋 Найдено версий: 3

1. Версия 3
   ID: TestProcess:3:b39c5036-55b6-11f0-a3a6-00b436387543
   Название: TestProcess
   Deployment ID: b3985894-55b6-11f0-a3a6-00b436387543
   Приостановлен: Нет

2. Версия 2
   ID: TestProcess:2:17349955-54cc-11f0-a3a6-00b436387543
   ...
```

## Интеграция с внешними системами

### 1. Интеграция с bash скриптами
```bash
#!/bin/bash
# order_processor.sh

ORDER_ID="ORDER-$(date +%Y%m%d)-$(uuidgen | cut -d'-' -f1)"
USER_NAME="$1"
AMOUNT="$2"

echo "Создание заказа: $ORDER_ID"

# Запуск процесса в Camunda
python start_process.py OrderProcess \
  --business-key "$ORDER_ID" \
  --variables "userName=$USER_NAME,amount=$AMOUNT,orderDate=$(date -Iseconds)"

if [ $? -eq 0 ]; then
    echo "✅ Заказ $ORDER_ID успешно создан в Camunda"
else
    echo "❌ Ошибка при создании заказа"
    exit 1
fi
```

### 2. Интеграция с Python приложениями
```python
import subprocess
import json
import sys

def start_camunda_process(process_key, variables=None, business_key=None):
    """Запуск процесса в Camunda из Python"""
    
    cmd = ["python", "start_process.py", process_key]
    
    if variables:
        cmd.extend(["--variables", json.dumps(variables)])
    
    if business_key:
        cmd.extend(["--business-key", business_key])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Процесс запущен успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {e.stderr}")
        return False

# Пример использования
if __name__ == "__main__":
    variables = {
        "userName": "John Doe",
        "amount": 1500,
        "priority": "high",
        "metadata": {
            "source": "python-script",
            "version": "1.0"
        }
    }
    
    success = start_camunda_process(
        "TestProcess", 
        variables=variables,
        business_key="PYTHON-001"
    )
    
    if not success:
        sys.exit(1)
```

### 3. Автоматизация через cron
```bash
# Еженедельный отчет - каждый понедельник в 9:00
0 9 * * 1 cd /opt/camunda-worker && ./venv/bin/python start_process.py WeeklyReport --business-key "REPORT-$(date +\%Y\%W)"

# Ежемесячная очистка - первое число месяца в 02:00
0 2 1 * * cd /opt/camunda-worker && ./venv/bin/python start_process.py MonthlyCleanup --variables "month=$(date +\%Y-\%m)"
```

## Обработка ошибок

### 1. Процесс не найден
```
❌ Процесс с ключом 'NonExistentProcess' не найден

💡 Попробуйте команду для просмотра всех процессов:
python camunda_processes.py --definitions
```

### 2. Ошибка подключения
```
❌ Ошибка при запросе к https://camunda.eg-holding.ru/engine-rest/process-definition/key/TestProcess: Connection refused
```
**Решение:** Проверьте доступность Camunda сервера

### 3. Ошибка аутентификации
```
❌ Ошибка при запросе к https://camunda.eg-holding.ru/engine-rest/process-definition/key/TestProcess: 401 Unauthorized
```
**Решение:** Проверьте логин/пароль в `config.py`

### 4. Ошибка парсинга переменных
```
❌ Ошибка при парсинге переменных: invalid JSON format
Пример правильного формата: 'userName=John,amount=100' или '{"userName": "John"}'
```

### 5. Приостановленный процесс
```
⚠️  Внимание: Процесс приостановлен. Запуск может не сработать.
Продолжить? (y/N): 
```

## Настройка
Скрипт использует конфигурацию из `config.py`:
- URL Camunda: `camunda_config.base_url`
- Аутентификация: `camunda_config.auth_username` / `camunda_config.auth_password`

## Безопасность

### 1. Передача паролей в переменных
**НЕ ДЕЛАЙТЕ ТАК:**
```bash
# Пароль виден в истории команд
python start_process.py UserProcess --variables "password=secret123"
```

**ДЕЛАЙТЕ ТАК:**
```bash
# Используйте файл с переменными
echo '{"userName": "john", "password": "secret123"}' > /tmp/vars.json
python start_process.py UserProcess --variables "$(cat /tmp/vars.json)"
rm /tmp/vars.json
```

### 2. Business Key уникальность
Убедитесь, что business key уникален, если ваш процесс этого требует.

## Расширенные возможности

### 1. Пакетный запуск процессов
```bash
#!/bin/bash
# batch_start.sh - пакетный запуск процессов

PROCESSES=("TestProcess" "OrderProcess" "ReportProcess")
BASE_BUSINESS_KEY="BATCH-$(date +%Y%m%d)"

for i in "${!PROCESSES[@]}"; do
    BUSINESS_KEY="${BASE_BUSINESS_KEY}-${i}"
    echo "Запуск ${PROCESSES[$i]} с ключом $BUSINESS_KEY"
    
    python start_process.py "${PROCESSES[$i]}" \
        --business-key "$BUSINESS_KEY" \
        --variables "batchId=$BASE_BUSINESS_KEY,index=$i"
    
    if [ $? -ne 0 ]; then
        echo "❌ Ошибка при запуске ${PROCESSES[$i]}"
    else
        echo "✅ ${PROCESSES[$i]} запущен успешно"
    fi
    
    # Пауза между запусками
    sleep 2
done
```

### 2. Мониторинг запущенных процессов
```bash
#!/bin/bash
# monitor_started.sh

BUSINESS_KEY_PREFIX="$1"

if [ -z "$BUSINESS_KEY_PREFIX" ]; then
    echo "Использование: $0 <business_key_prefix>"
    exit 1
fi

echo "Поиск процессов с business key: $BUSINESS_KEY_PREFIX*"

# Получить список экземпляров и отфильтровать по business key
python camunda_processes.py --instances | grep -A 20 "Business Key: $BUSINESS_KEY_PREFIX"
```

## Требования
- Python 3.7+
- requests >= 2.25.0
- Доступ к Camunda REST API
- Настроенная аутентификация

## Дополнительные материалы

### Связанные скрипты:
- `camunda_processes.py` - просмотр процессов и экземпляров
- `status_check.py` - проверка доступности Camunda

### Полезные ссылки:
- [Camunda REST API](https://docs.camunda.org/manual/latest/reference/rest/)
- [BPMN 2.0 Guide](https://camunda.com/bpmn/)

---

**💡 Совет:** Используйте `--dry-run` для тестирования сложных переменных перед фактическим запуском процесса. 