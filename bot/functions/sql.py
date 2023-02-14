import mariadb
import datetime

import os

class Database:
    def __init__(self):
        try:
            self.connection = mariadb.connect(
                                user= os.environ['db_user'],
                                password=os.environ['db_password'],
                                host=os.environ['db_host'],
                                port=os.environ['db_port'],
                                database=os.environ['db_database']
                                )
            self.cursor = self.connection.cursor()
        
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")


    def create_user_data_table(self):
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS user_data (
                                user_id INT PRIMARY KEY,
                                user_name VARCHAR(200)
                                )""")
            self.connection.commit()


    def add_user_name(self, user_id:str ,name:str):
            self.cursor.execute(f"""INSERT INTO user_data (user_id, user_name)
                                VALUES (?,?) ON DUPLICATE KEY UPDATE user_name=?
                                """, (user_id, name, name))
            self.connection.commit()

    
    def get_user_name(self, user_id:str):
        self.cursor.execute("""SELECT user_name FROM user_data WHERE
                            user_id=(?) """, (user_id,))
        list = []
        for item in self.cursor:
            list.append(item[0])
        return list


    def create_class_attendance_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS class_attendance (
                                id MEDIUMINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                                user_id INT,
                                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                shabbat boolean DEFAULT false
                                )""")
        self.connection.commit()

    
    def add_user_presence(self, user_id:str, shabbat:bool):
        self.cursor.execute("""INSERT INTO class_attendance (user_id, shabbat)
                                VALUES (?,?)""", (user_id, shabbat,))
        self.connection.commit()


    def get_users_presences(self, user_id:str = None, mounth:int=None, year:int=None):
        get_date = """MONTH(class_attendance.date) = (?) AND YEAR(class_attendance.date) = (?)"""
        get_by_user_id = """user_data.user_id = (?) AND YEAR(class_attendance.date) = (?)"""

        if user_id:
            request = get_by_user_id
            arg1 = user_id
            arg2 = datetime.date.today().year
        if mounth and year:
            request = get_date
            arg1 = mounth
            arg2 = year

        self.cursor.execute(f""" SELECT class_attendance.user_id AS class_attendance_user_id, class_attendance.date, class_attendance.shabbat, user_data.user_name
                                FROM user_data 
                                INNER JOIN class_attendance ON user_data.user_id = class_attendance.user_id
                                WHERE {request};""", (arg1, arg2,))

        list = []
        for item in self.cursor:
            list.append(item)
        return list
