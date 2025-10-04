import os
import psycopg2
import pandas as pd
from datetime import datetime
import sys
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class DatabaseExporter:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'cargo_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }

        self.export_path = os.getenv('EXPORT_PATH', '/data/exports')

    def connect(self):
        """Установка соединения с БД"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            sys.exit(1)

    def export_table(self, table_name):
        """Экспорт данных таблицы в CSV"""
        conn = self.connect()

        try:
            query = f"SELECT * FROM {table_name}"
            params = None

            # Читаем данные в DataFrame
            df = pd.read_sql_query(query, conn)

            # Создаем директорию для экспорта если не существует
            os.makedirs(self.export_path, exist_ok=True)

            # Формируем имя файла
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{table_name}_{timestamp}.csv"
            filepath = os.path.join(self.export_path, filename)

            # Сохраняем в CSV
            df.to_csv(filepath, index=False)

            print(f"Экспортировано {len(df)} строк из таблицы {table_name} в {filepath}")
            return filepath

        except Exception as e:
            print(f"Ошибка экспорта таблицы {table_name}: {e}")
            return None
        finally:
            conn.close()

def main():
    if len(sys.argv) != 2:
        print("Использование: python exporter.py <table_name>")
        print("Доступные таблицы: shipments, shipment_events, drivers, vehicles, clients")
        sys.exit(1)

    table_name = sys.argv[1]
    valid_tables = ['shipments', 'shipment_events', 'drivers', 'vehicles', 'clients']

    if table_name not in valid_tables:
        print(f"Неверное имя таблицы. Доступные: {valid_tables}")
        sys.exit(1)

    # Экспорт данных за текущий день
    today = datetime.now().strftime('%Y-%m-%d')

    exporter = DatabaseExporter()
    result = exporter.export_table(table_name)

    if result:
        print(f"Экспорт успешно завершен: {result}")
        sys.exit(0)
    else:
        print("Экспорт завершился с ошибкой")
        sys.exit(1)

if __name__ == "__main__":
    main()