import mariadb
import os

def get_db_connection():
    """
    ຟັງຊັນນີ້ເຊື່ອມຕໍ່ຖານຂໍ້ມູນໃຊ້ mariadb connector.
    ຕັ້ງຄ່າຈາກ Environment Variables.
    """
    try:
        connection = mariadb.connect(
            host=os.getenv("DB_SIT_HOST"),
            user=os.getenv("DB_SIT_USER"),
            password=os.getenv("DB_SIT_PASSWORD"),
            database=os.getenv("DB_SIT_NAME"),
            port=int(os.getenv("DB_SIT_PORT"))
        )
        return connection
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        raise 