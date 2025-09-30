from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
import clickhouse_connect
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import logging

def get_last_timestamp_from_clickhouse(client, table_name):
    try:
        if table_name == 'telemetry':
            result = client.query("SELECT max(timestamp) as last_timestamp FROM telemetry")
        elif table_name == 'users':
            result = client.query("SELECT max(created_at) as last_timestamp FROM users")
        
        last_timestamp = result.first_item.get('last_timestamp')
        
        if last_timestamp:
            logging.info(f"Последний timestamp в {table_name}: {last_timestamp}")
            return last_timestamp
        else:
            logging.info(f"В таблице {table_name} нет данных, загружаем все")
            return None
            
    except Exception as e:
        logging.warning(f"Ошибка при получении последнего timestamp из {table_name}: {e}")
        return None


def query_and_load_to_clickhouse():
    try:
        logging.info("Подключаемся к ClickHouse")
        ch_client = clickhouse_connect.get_client(
            host='clickhouse',
            port=8123,
            username='admin',
            password='admin123', 
            database='report'
        )

        logging.info("Подключаемся к PostgreSQL база MAIN")

        last_telemetry_timestamp = get_last_timestamp_from_clickhouse(ch_client, 'telemetry')

        engine_main = create_engine(
            'postgresql+psycopg2://app_user:app_password@main-db:5432/main_db'
        )
        
        logging.info("Успешное подключение к PostgreSQL")
        
        with engine_main.connect() as connection:

            if last_telemetry_timestamp:
                query = text("""
                    SELECT id, user_id, timestamp, valueA, valueB, valueC, valueD
                    FROM telemetry 
                    WHERE timestamp > :last_timestamp
                    ORDER BY timestamp DESC 
                """)
                params = {'last_timestamp': last_telemetry_timestamp}
                logging.info(f"Загружаем данные telemetry начиная с {last_telemetry_timestamp}")
            else:
                query = text("""
                    SELECT id, user_id, timestamp, valueA, valueB, valueC, valueD
                    FROM telemetry 
                    ORDER BY timestamp DESC 
                """)
                params = {}
                logging.info("Загружаем все данные telemetry")

            data_result = connection.execute(query, params)
            records = data_result.fetchall()

            if records:
                logging.info(f"Найдено {len(records)} записей в telemetry")
            
                telemetry_data = []
                for record in records:
                    telemetry_data.append([
                        record[0],       # id
                        record[1],       # user_id
                        record[2],       # timestamp
                        record[3] or 0,  # value_a
                        record[4] or 0,  # value_b
                        record[5] or 0,  # value_c
                        record[6] or 0   # value_d
                    ])
                
                ch_client.insert(
                    'telemetry',
                    telemetry_data,
                    column_names=['id', 'user_id', 'timestamp', 'valueA', 'valueB', 'valueC', 'valueD']
                )
                
                logging.info(f"Успешно загружено {len(telemetry_data)} записей в ClickHouse таблицу telemetry")

            else:
                logging.info("В таблице telemetry нет новых данных")


        logging.info("Подключаемся к PostgreSQL база CRM")
        
        engine_crm = create_engine(
            'postgresql+psycopg2://app_user:app_password@crm-db:5432/main_db'
        )
        
        logging.info("Успешное подключение к PostgreSQL CRM")

        last_users_timestamp = get_last_timestamp_from_clickhouse(ch_client, 'users')
        
        with engine_crm.connect() as connection:

            if last_users_timestamp:
                query = text("""
                    SELECT user_id, username, email, first_name, last_name, created_at
                    FROM users
                    WHERE created_at > :last_timestamp
                    ORDER BY created_at DESC                                  
                """)
                params = {'last_timestamp': last_users_timestamp}
                logging.info(f"Загружаем данные users начиная с {last_users_timestamp}")
            else:
                query = text("""
                    SELECT user_id, username, email, first_name, last_name, created_at
                    FROM users
                    ORDER BY created_at DESC                                  
                """)
                params = {}
                logging.info("Загружаем все данные users")

            data_result = connection.execute(query, params)

            records = data_result.fetchall()
            
            if records:
                logging.info(f"Найдено {len(records)} записей в users")
                
                users_data = []
                for record in records:
                    users_data.append([
                        record[0],        # user_id
                        record[1] or '',  # username
                        record[2] or '',  # email
                        record[3] or '',  # first_name
                        record[4] or '',  # last_name
                        record[5]         # created_at
                    ])
                
                ch_client.insert(
                    'users',
                    users_data,
                    column_names=['user_id', 'username', 'email', 'first_name', 'last_name', 'created_at']
                )
                logging.info(f"Успешно загружено {len(users_data)} записей в ClickHouse таблицу users")
            else:
                logging.info("В таблице users нет новых данных")
        
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        raise

def check_connection(db_host, db_name='main_db', db_user='app_user', db_password='app_password', db_port=5432):
    try:
        connection_string = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

        engine = create_engine(connection_string)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            test_value = result.scalar()

            logging.info(f"Подключение к %s - ОК (%s)", db_host, test_value)
        
    except Exception as e:
        logging.error(f"Ошибка подключения: {e}")
        raise

def check_main_connection():
    check_connection('main-db')


def check_crm_connection():
    check_connection('crm-db')

def test_clickhouse_connection():
    
    try:
        client = clickhouse_connect.get_client(
            host='clickhouse',
            port=8123,
            username='admin',
            password='admin123', 
            database='report'
        )
        logging.info("Успешное подключение к ClickHouse")
        
        users_exists = client.command("EXISTS TABLE users")
        
        if users_exists:
            logging.info("users - OK")

        telemetry_exists = client.command("EXISTS TABLE telemetry")
        
        if telemetry_exists:
            logging.info("telemetry - OK")
        
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        raise

with DAG(
    'postgres_to_clickhouse_ETL',
    description='Загрузка данных из main-db таблица telemetry и crm-db таблица users и последующая загрузка данных в clickhouse ',
    start_date=datetime(2025, 9, 28),
    schedule=timedelta(minutes=3),
    catchup=False,
    default_args={
        'retries': 5,
        'retry_delay': timedelta(seconds=10),
    },
    tags=['postgres', 'crm-db', 'main-db']
) as dag:

    check_connection_task_main = PythonOperator(
        task_id='check_connection_main',
        python_callable=check_main_connection,
    )

    check_connection_task_crm = PythonOperator(
        task_id='check_connection_crm',
        python_callable=check_crm_connection,
    )

    check_connection_task_clickhouse = PythonOperator(
        task_id ='test_clickhouse',
        python_callable = test_clickhouse_connection,
    )

    load_data_task = PythonOperator(
        task_id='load_data_to_clickhouse',
        python_callable=query_and_load_to_clickhouse,
    )

    check_connection_task_crm >> check_connection_task_main >> check_connection_task_clickhouse >> load_data_task