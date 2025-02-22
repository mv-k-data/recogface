import sqlite3


class SqliteDatabaseHelper:
    DB_NAME = "search_results.db"

    def __init__(self):
        self.init_db()

    def init_db(self):
        """Ініціалізація бази даних (створення таблиці, якщо її немає)."""
        with sqlite3.connect(self.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_request (
                    uuid TEXT PRIMARY KEY,
                    image_name TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_responce (
                    uuid TEXT,
                    search_engine TEXT,
                    image_name TEXT,
                    image_url TEXT,
                    image_text TEXT,
                    full_image_name TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(uuid, search_engine, image_name)
                )
            """)
            conn.commit()

    def save_original_image(self, uuid, image_name):
        """Збереження результату пошуку в базу даних."""
        with sqlite3.connect(self.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR IGNORE INTO search_request (uuid, image_name)
                VALUES (?, ?)
            """,
                (uuid, image_name),
            )
            conn.commit()

    def save_search_result(self, search_results):
        """Збереження результату пошуку в базу даних."""
        with sqlite3.connect(self.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                """
                INSERT OR IGNORE INTO search_responce (uuid, search_engine, image_name, image_url, image_text, full_image_name)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (search_results),
            )
            conn.commit()

    def get_history_details(self, uuid):
        with sqlite3.connect(self.DB_NAME) as conn:
            cursor = conn.cursor()  
            cursor.execute(f"""
                SELECT 
                    req.image_name as original_image,  
                    res.search_engine,
                    res.image_text,
                    res.image_url,
                    res.full_image_name
                FROM search_request req 
                LEFT JOIN search_responce res
                ON req.uuid= res.uuid
                and req.uuid = '{uuid}'           
            """)
        return cursor.fetchall()      

    def get_search_history(self):
        """Отримання всіх збережених результатів."""
        with sqlite3.connect(self.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                        WITH res AS (
                        SELECT uuid, group_concat(search_engine, ';') as search_engines, sum(cnt) as cnt
                            FROM (
                            SELECT uuid, search_engine, count(1) as cnt
                            FROM search_responce
                            GROUP BY uuid, search_engine
                            )
                        GROUP BY uuid
                        )
                        SELECT req.uuid, req.image_name, req.created_at, res.search_engines, res.cnt
                        FROM search_request req 
                        LEFT JOIN res 
                        ON req.uuid= res.uuid
                        ORDER BY req.created_at DESC                          
                           """)
            return cursor.fetchall()
