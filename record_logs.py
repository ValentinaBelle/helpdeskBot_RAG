import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Создаем класс для для сохранения разговоров с ботом в JSON файл
class ChatLogger:
    def __init__(self, log_file: str = "logs/chat_log.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.log_file.exists():
            self.log_file.write_text("[]", encoding='utf-8')

    # Создаем функцию для чтения всех логов из файла
    def _read_logs(self) -> List[Dict]:
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
            return logs
        except json.JSONDecodeError:
            print("Файл с логом поврежден")
            return []
        except Exception as e:
            print(f"Ошибка чтения логов: {e}")
            return []

    # Создаем функцию для записи логов
    def _write_logs(self, logs: List[Dict]) -> None:
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка записи логов: {e}")

    # Создаем функцию для логирования разговора
    def log(self, question: str, answer: str, metadata: Optional[Dict] = None) -> Dict:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "metadata": metadata or {}
        }
        logs = self._read_logs()
        logs.append(entry)
        self._write_logs(logs)
        return entry

    # Создаем функцию для получения последние N логов
    def get_logs(self, limit: int = 10) -> List[Dict]:
        logs = self._read_logs()
        return logs[-limit:] if logs else []

    # Создаем функцию для получения всех логов
    def get_all_logs(self) -> List[Dict]:
        return self._read_logs()

    # Создаем функцию для поиска логов по запросу
    def search(self, query: str) -> List[Dict]:
        logs = self._read_logs()
        results = []
        for log in logs:
            if query.lower() in log["question"].lower():
                results.append(log)
        return results

    # Создаем функцию для получения статистики разговоров
    def stats(self) -> Dict:
        logs = self._read_logs()

        if not logs:
            return {
                "total_conversations": 0,
                "first_conversation": None
            }
        return {
                "total_conversations": len(logs),
                "first_conversation": logs[0]["timestamp"],
                "last_conversation": logs[-1]["timestamp"]
            }
