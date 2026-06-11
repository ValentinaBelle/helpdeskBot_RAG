from logger import ChatLogger
from datetime import datetime

# Создаем функцию для просмотра статистики и недавних разговоров
def main():
    try:
        logger = ChatLogger("logs/chat_log.json")
        print("Статистика разговоров с чат-ботом")

        # Get statistics
        stats = logger.stats()

        if stats["total_conversations"] == 0:
            print("No conversations logged yet.\n")
            return

        print(f"Total conversations: {stats['total_conversations']}")
        print(f"First conversation: {stats['first_conversation']}")
        print(f"Last conversation: {stats['last_conversation']}\n")

        # Получить и отобразить свежие логи
        print("RECENT CONVERSATIONS (Last 5)")

        logs = logger.get_logs(limit=5)

        for i, log in enumerate(reversed(logs), 1):
            timestamp = datetime.fromisoformat(log['timestamp'])
            formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")

            print(f"{i}.{formatted_time}")
            print(f"    👤Question: {log['question']}")

            # Обрезаем долгие ответы
            answer = log['answer']
            if len(answer) > 100:
                answer = answer[:100] + "..."
            print(f"Answer: {answer}")

            if log['metadata']:
                print(f"Metadata: {log['metadata']}")
            print()

        # Ищем разговор
        search_query = input("🔍 Найди разговор (или нажмите Enter для выхода): ").strip()

        if search_query:
            results = logger.search(search_query)

            if not results:
                print(f"\nНе найдено разговора с '{search_query}'")
            else:
                print(f"\nFound {len(results)} result(s):\n")
                for i, log in enumerate(reversed(results), 1):
                    timestamp = datetime.fromisoformat(log['timestamp'])
                    formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")

                    print(f"{i}. {formatted_time}")
                    print(f"    👤 {log['question']}")
                    print(f"{log['answer'][:80]}...")
                    print()

    except FileNotFoundError:
        print("Файл с логом не найден. Никакого разговора пока не залогировано.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
