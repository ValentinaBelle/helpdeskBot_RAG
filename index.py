import os
from langchain.document_loaders import TextLoader
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain_anthropic import ChatAnthropic
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from bot_prompts import CONTEXT_PROMPT
from logger import ChatLogger

# Загружаем ключи из env
load_dotenv()

# Запускаем логгер
logger = ChatLogger("logs/chat_log.json")

KB_FILE = "knowledge_base.txt"
CHROMA_DB_DIR = "chroma_db"

# Загрузка файла с базой знаний
def load_knowledge_base(file_path: str) -> list:
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"База знаний не найдена: {file_path}")
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()
        if not documents:
            raise ValueError(f"Документы не были загружены {file_path}")
        print(f"✅ Загружено {len(documents)} документ(ов)")
        return documents
    except Exception as e:
        raise Exception(f"Ошибка загрузки базы знаний: {e}")

# Создание векторной базы данных
def create_vector_db(documents, persist_directory="chroma_db"):
    try:
        if os.path.exists(persist_directory):
            print(f"📦 Загружаю существующую базу из {persist_directory}...")
            embeddings = OpenAIEmbeddings()
            vectordb = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings
            )
            return vectordb

        print("🔨 Создаю новую векторную базу...")
        text_splitter = CharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=50
        )
        docs = text_splitter.split_documents(documents)
        print(f"📄 Разделено на {len(docs)} частей")

        embeddings = OpenAIEmbeddings()
        vectordb = Chroma.from_documents(
            docs,
            embeddings,
            persist_directory=persist_directory
        )
        print(f"✅ Векторная база создана")
        return vectordb

    except Exception as e:
        raise Exception(f"Ошибка создания векторной базы: {e}")

# Создаем QA цепочки для ответов
def create_qa_chain(vectordb):
    try:
        prompt_template = CONTEXT_PROMPT
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY не найден в переменных окружения")

        llm = ChatAnthropic(
            model="claude-3-haiku-20240307",
            anthropic_api_key=api_key,
            temperature=0.7,
            max_tokens=1000
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectordb.as_retriever(search_kwargs={"k": 2}),
            return_source_documents=False,
            chain_type_kwargs={"prompt": PROMPT}
        )
        return qa_chain

    except Exception as e:
        raise Exception(f"Ошибка создания QA цепочки: {e}")

# Отправляем вопрос боту
def ask_bot(qa_chain, question: str) -> str:
    try:
        if not question.strip():
            return "Задайте корректный вопрос"

        result = qa_chain({"query": question})
        answer = result["result"]

        logger.log(
            question=question,
            answer=answer,
            metadata={"model": "claude-3-haiku"}
        )
        return answer

    except Exception as e:
        error_msg = f"Ошибка обработки вопроса: {e}"
        logger.log(
            question=question,
            answer=error_msg,
            metadata={"model": "claude-3-haiku", "error": True}
        )
        return error_msg

# Запускаем бот
def main():
    try:
        # Проверяем API ключи
        openai_key = os.environ.get("OPENAI_API_KEY")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

        if not openai_key:
            raise ValueError("OPENAI_API_KEY не найден в переменных окружения")
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY не найден в переменных окружения")

        print("Инициализация бота...\n")

        # Загружаем базу знаний
        documents = load_knowledge_base(KB_FILE)

        # Создаём векторную базу
        vectordb = create_vector_db(documents)

        # Создаём цепочку
        qa_chain = create_qa_chain(vectordb)

        print("Чат-бот банка 'BNP Paribas' готов!")
        print("Введите 'выход', 'exit' или 'quit' для выхода")

        # Основной цикл чата
        while True:
            try:
                question = input("👤 Вы: ").strip()

                if not question:
                    continue

                if question.lower() in ["выход", "exit", "quit"]:
                    print("👋 До свидания!")
                    break

                answer = ask_bot(qa_chain, question)
                print(f"Бот: {answer}")

            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
            except Exception as e:
                print(f"Ошибка: {e}")

    except FileNotFoundError as e:
        print(f"Ошибка файла: {e}")
        print(f"Убедитесь, что файл '{KB_FILE}' находится в текущей папке")
    except ValueError as e:
        print(f"Ошибка конфигурации: {e}")
        print("Проверьте файл .env и переменные окружения")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        raise


if __name__ == "__main__":
    main()
