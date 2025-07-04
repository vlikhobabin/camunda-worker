#!/usr/bin/env python3
"""
Universal Camunda Worker на базе ExternalTaskClient
Stateless архитектура для обработки External Tasks
"""
import time
import signal
import sys
import threading
import traceback
from typing import Dict, Any, Optional
from loguru import logger

from camunda.client.external_task_client import ExternalTaskClient
from camunda.external_task.external_task import ExternalTask
from config import camunda_config, worker_config, routing_config
from rabbitmq_client import RabbitMQClient


class UniversalCamundaWorker:
    """Universal Worker на базе ExternalTaskClient с Stateless архитектурой"""
    
    def __init__(self):
        self.config = camunda_config
        self.worker_config = worker_config
        self.routing_config = routing_config
        
        # Компоненты
        self.client: Optional[ExternalTaskClient] = None
        self.rabbitmq_client = RabbitMQClient()
        
        # Управление работой
        self.running = False
        self.stop_event = threading.Event()
        self.worker_threads = []
        
        # Статистика
        self.stats = {
            "processed_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "start_time": None,
            "last_fetch": None
        }
        
        # Настройка обработки сигналов
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов завершения"""
        logger.info(f"Получен сигнал {signum}, завершение работы...")
        self.shutdown()
        sys.exit(0)
    
    def initialize(self) -> bool:
        """Инициализация компонентов"""
        try:
            logger.info("Инициализация Universal Camunda Worker...")
            
            # Подключение к RabbitMQ
            if not self.rabbitmq_client.connect():
                logger.error("Не удалось подключиться к RabbitMQ")
                return False
            
            if not self.rabbitmq_client.setup_infrastructure():
                logger.error("Не удалось создать инфраструктуру RabbitMQ")
                return False
            
            # Конфигурация ExternalTaskClient
            client_config = {
                "maxTasks": self.config.max_tasks,
                "lockDuration": self.config.lock_duration,
                "asyncResponseTimeout": self.config.async_response_timeout,
                "httpTimeoutMillis": self.config.http_timeout_millis,
                "timeoutDeltaMillis": self.config.timeout_delta_millis,
                "includeExtensionProperties": self.config.include_extension_properties,
                "deserializeValues": self.config.deserialize_values,
                "usePriority": True,
                "sorting": self.config.sorting,
                "isDebug": self.config.is_debug
            }
            
            if self.config.auth_enabled:
                client_config["auth_basic"] = {
                    "username": self.config.auth_username,
                    "password": self.config.auth_password
                }
            
            # Создание ExternalTaskClient
            self.client = ExternalTaskClient(
                worker_id=self.config.worker_id,
                engine_base_url=self.config.base_url,
                config=client_config
            )
            
            logger.info("Инициализация завершена успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации: {e}")
            return False
    
    def _fetch_and_process_loop(self, topic: str):
        """Основной цикл получения и обработки задач для топика"""
        logger.info(f"Запущен поток для топика: {topic}")
        
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while not self.stop_event.is_set():
            try:
                # Получение задач
                tasks = self.client.fetch_and_lock(topic)
                self.stats["last_fetch"] = time.time()
                
                if tasks:
                    consecutive_errors = 0  # Сброс счетчика ошибок при успешном получении
                    logger.info(f"Получено {len(tasks)} задач для топика {topic}")
                    
                    for task_data in tasks:
                        if self.stop_event.is_set():
                            break
                        self._process_task(task_data, topic)
                    
                    # Короткая пауза между обработками
                    self.stop_event.wait(1)
                else:
                    # Нет задач - ждем дольше
                    self.stop_event.wait(self.config.sleep_seconds)
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Ошибка в цикле обработки топика {topic}: {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.error(f"Слишком много ошибок подряд ({consecutive_errors}) для топика {topic}, останавливаю поток")
                    break
                
                # Увеличиваем паузу при ошибках
                error_sleep = min(30, 5 * consecutive_errors)
                logger.warning(f"Пауза {error_sleep}s после ошибки для топика {topic}")
                self.stop_event.wait(error_sleep)
        
        logger.info(f"Поток для топика {topic} завершен")
    
    def _process_task(self, task_data: Dict[str, Any], topic: str):
        """Обработка одной задачи"""
        task_id = task_data.get('id', 'unknown')
        
        try:
            logger.info(f"Обработка задачи {task_id} | Топик: {topic}")
            self.stats["processed_tasks"] += 1
            
            # Создание объекта ExternalTask
            task = ExternalTask(task_data)
            
            # Подготовка данных для RabbitMQ
            task_payload = {
                "id": task_id,
                "topic": topic,
                "variables": task.get_variables(),
                "processInstanceId": task.get_process_instance_id(),
                "activityId": task.get_activity_id(),
                "activityInstanceId": task_data.get("activityInstanceId"),  # Берем из исходных данных
                "workerId": task.get_worker_id(),
                "retries": task_data.get("retries"),
                "createTime": task_data.get("createTime"),
                "priority": task_data.get("priority", 0),
                "tenantId": task.get_tenant_id(),
                "businessKey": task.get_business_key()
            }
            
            # Определение целевой системы
            system = self.routing_config.get_system_for_topic(topic)
            logger.info(f"Задача {task_id} направляется в систему: {system}")
            
            # Отправка в RabbitMQ
            if self.rabbitmq_client.publish_task(topic, task_payload):
                self.stats["successful_tasks"] += 1
                logger.info(f"Задача {task_id} успешно отправлена в RabbitMQ")
                
                # В Stateless режиме задача остается заблокированной
                logger.info(f"Задача {task_id} остается заблокированной, ожидает ответа из {system}")
            else:
                raise Exception("Не удалось опубликовать задачу в RabbitMQ")
                
        except Exception as e:
            self._handle_task_error(task_id, topic, str(e))
    
    def _handle_task_error(self, task_id: str, topic: str, error: str):
        """Обработка ошибки задачи"""
        try:
            logger.error(f"Ошибка обработки задачи {task_id}: {error}")
            self.stats["failed_tasks"] += 1
            
            # Отправка ошибки в RabbitMQ
            self.rabbitmq_client.publish_error(topic, task_id, error)
            
            # Возврат задачи в Camunda с ошибкой
            retries = max(0, self.worker_config.retry_attempts - 1)
            
            success = self.client.failure(
                task_id=task_id,
                error_message=f"Task processing error: {error}",
                error_details=error,
                retries=retries,
                retry_timeout=self.worker_config.retry_delay * 1000
            )
            
            if success:
                logger.warning(f"Задача {task_id} возвращена с ошибкой (retries: {retries})")
            else:
                logger.error(f"Не удалось вернуть задачу {task_id} с ошибкой")
                
        except Exception as handle_error:
            logger.error(f"Ошибка обработки ошибки задачи {task_id}: {handle_error}")
    
    def start(self):
        """Запуск Worker"""
        try:
            if not self.initialize():
                logger.error("Инициализация не удалась")
                return False
            
            logger.info("Запуск Universal Camunda Worker...")
            self.stats["start_time"] = time.time()
            self.running = True
            
            # Получение списка топиков
            topics = list(self.routing_config.TOPIC_TO_SYSTEM_MAPPING.keys())
            logger.info(f"Запуск обработки {len(topics)} топиков: {topics}")
            
            # Создание потоков для каждого топика
            for topic in topics:
                thread = threading.Thread(
                    target=self._fetch_and_process_loop,
                    args=(topic,),
                    daemon=True,
                    name=f"Worker-{topic}"
                )
                thread.start()
                self.worker_threads.append(thread)
                logger.info(f"Запущен поток для топика: {topic}")
            
            # Поток мониторинга
            monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name="Monitor"
            )
            monitor_thread.start()
            self.worker_threads.append(monitor_thread)
            
            logger.info("Worker запущен и ожидает задачи...")
            
            # Ожидание завершения
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Получен сигнал прерывания")
                self.shutdown()
                
        except Exception as e:
            logger.error(f"Ошибка запуска Worker: {e}")
            traceback.print_exc()
            self.shutdown()
            return False
        
        return True
    
    def _monitor_loop(self):
        """Поток мониторинга статистики"""
        while not self.stop_event.is_set():
            try:
                if self.running and self.stats["start_time"]:
                    uptime = time.time() - self.stats["start_time"]
                    logger.info(
                        f"Monitor - Uptime: {uptime:.0f}s | "
                        f"Обработано: {self.stats['processed_tasks']} | "
                        f"Успешно: {self.stats['successful_tasks']} | "
                        f"Ошибки: {self.stats['failed_tasks']}"
                    )
                    
                    # Проверка соединения с RabbitMQ
                    if not self.rabbitmq_client.is_connected():
                        logger.warning("RabbitMQ соединение потеряно, попытка переподключения...")
                        self.rabbitmq_client.reconnect()
                
                # Мониторинг каждые 30 секунд
                self.stop_event.wait(30)
                
            except Exception as e:
                logger.error(f"Ошибка в мониторинге: {e}")
                self.stop_event.wait(10)
    
    def shutdown(self):
        """Корректное завершение работы"""
        logger.info("Завершение работы Universal Camunda Worker...")
        self.running = False
        self.stop_event.set()
        
        # Ожидание завершения потоков
        for thread in self.worker_threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        # Закрытие RabbitMQ соединения
        self.rabbitmq_client.disconnect()
        
        # Финальная статистика
        if self.stats["start_time"]:
            uptime = time.time() - self.stats["start_time"]
            logger.info(
                f"Финальная статистика - Uptime: {uptime:.0f}s | "
                f"Обработано: {self.stats['processed_tasks']} | "
                f"Успешно: {self.stats['successful_tasks']} | "
                f"Ошибки: {self.stats['failed_tasks']}"
            )
        
        logger.info("Universal Worker завершен")
    
    def get_status(self) -> Dict[str, Any]:
        """Получение текущего статуса Worker"""
        uptime = time.time() - self.stats["start_time"] if self.stats["start_time"] else 0
        
        return {
            "is_running": self.running,
            "uptime_seconds": uptime,
            "stats": self.stats.copy(),
            "architecture": "stateless",
            "active_threads": len([t for t in self.worker_threads if t.is_alive()]),
            "topics": list(self.routing_config.TOPIC_TO_SYSTEM_MAPPING.keys()),
            "lock_duration_minutes": self.config.lock_duration / (1000 * 60),
            "camunda_config": {
                "base_url": self.config.base_url,
                "worker_id": self.config.worker_id,
                "max_tasks": self.config.max_tasks,
                "lock_duration": self.config.lock_duration
            },
            "rabbitmq_connected": self.rabbitmq_client.is_connected(),
            "queues_info": self.rabbitmq_client.get_all_queues_info()
        }


def main():
    """Главная функция для тестирования"""
    logger.info("Запуск Universal Camunda Worker")
    
    worker = UniversalCamundaWorker()
    
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания")
    finally:
        worker.shutdown()


if __name__ == "__main__":
    main() 