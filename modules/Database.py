import sqlite3
import asyncio
from sqlite3 import Error

from datetime import date, datetime, timedelta
from ast import literal_eval

import json

from modules.Logger import *
from modules.Utils import Utils

class Database:

    def __init__(self, db_name=Utils.get_patch_db("main")):
        self.name = db_name
        self.conn = self.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

        self.conn_log = self.connect(Utils.get_patch_db("log"))
        self.cursor_log = self.conn_log.cursor()

    def connect(self, db_name):
        try:
            return sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES, timeout=10)
        except Error as e:
            logger.error(e)
            pass

    def create_tables(self):

        try:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS users \
                (member_id INTEGER NOT NULL, \
                marry INTEGER NOT NULL DEFAULT 0, \
                money INTEGER NOT NULL DEFAULT 100, \
                themes TEXT NOT NULL, \
                inst TEXT, \
                vk TEXT, \
                tg TEXT, \
                tiktok TEXT, \
                daily TEXT NOT NULL DEFAULT 0, \
                theme TEXT NOT NULL)")

            self.cursor.execute("CREATE TABLE IF NOT EXISTS marrieges \
                (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                partner_1 INTEGER NOT NULL, \
                partner_2 INTEGER NOT NULL, \
                balance INTEGER NOT NULL DEFAULT 0, \
                reg_marry TEXT, \
                loveRoom TEXT, \
                id_l TEXT, \
                themes TEXT NOT NULL, \
                theme TEXT NOT NULL)")

            self.cursor.execute("CREATE TABLE IF NOT EXISTS personal_roles \
                (role_id TEXT NOT NULL, \
                owner TEXT NOT NULL, \
                black_list TEXT NOT NULL, \
                time INTEGER NOT NULL)")
            
            self.cursor.execute("CREATE TABLE IF NOT EXISTS transactions \
                (member_id INTEGER NOT NULL, \
                category TEXT NOT NULL, \
                value INTEGER NOT NULL, \
                time INTEGER NOT NULL)")

            self.cursor.execute("CREATE TABLE IF NOT EXISTS voiceactivity_all \
                (member_id	INTEGER NOT NULL, \
                joined_at	VARCHAR(255), \
                left_at	VARCHAR(255), \
                total_hours INTEGER NOT NULL, \
                total_minutes INTEGER NOT NULL)")


        except Error as e:
            logger.error(e)
            return False

        self.conn.commit()
        return True

    # GENERIC FUNCTIONS

    def execute_statement(self, statement):

        try:
            self.cursor.execute(statement)
        except Error as e:
            logger.error(e)
            return False
        return True

    def get_value(self, member_id, table, attribute):

        if self.member_exists(member_id):

            statement = f"SELECT {attribute} FROM {table} WHERE member_id = {int(member_id)}"

            if self.execute_statement(statement):

                result = self.cursor.fetchall()
                return result[0][0]
            
            return 0
        
        return 0

    # Economy

    # Добавляем нового пользователя в основную базу
    def write_new_user(self, member):
        self.cursor.execute(f"SELECT member_id FROM users WHERE member_id={member.id}")

        if not member.bot:
            if self.cursor.fetchone() is None:
                self.cursor.execute(f"INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (member.id, 0, 0, '[]', None, None, None, None, 0, 'theme_default'))
            else:
                pass
            self.conn.commit()

    # def write_new_user(self, member):
    #     if not member.bot:
    #         self.cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (member.id, 0, 0, None, None, None, None, 0))
    #         self.conn.commit()

    # Получаем баланс
    def get_balance(self, member_id):
        self.cursor.execute('SELECT money FROM users WHERE member_id=?', (member_id,))
        result = self.cursor.fetchone()

        if result is not None:
            return result[0]
        else:
            return 0

    # Передача денег можно использовать get_balance
    def transfer_money(self, member_1, member_2, amount):
        for row in self.cursor.execute(f'SELECT money FROM users where member_id=?', (member_1.id,)):
            self.cursor.execute(f'UPDATE users SET money="{int(row[0]) - int(amount)}" where member_id=?', (member_1.id,))

            for row_1 in self.cursor.execute(f'SELECT money FROM users where member_id=?', (member_2.id,)):
                self.cursor.execute(f'UPDATE users SET money="{int(row_1[0]) + int(amount)}" where member_id=?', (member_2.id,))

        self.conn.commit()

    # Получаем нужную соц.сеть
    def get_social(self, member_id, type):
        for row in self.cursor.execute(f'SELECT {type} from users where member_id=?', (member_id,)):
            if str(row[0]).__len__() > 1:
                if row[0] == False or row[0] == None:
                    return " "
                else:
                    return row[0]
            else:
                return False

    # Устанавлием нужную соц.сеть
    def set_social(self, social, social_id, member_id):
        social_id = social_id.replace(' ', '')

        if social == "inst":
            self.cursor.execute(f'UPDATE users SET inst="{social_id}" where member_id=?', (member_id,))
        elif social == "vk":
            self.cursor.execute(f'UPDATE users SET vk="{social_id}" where member_id=?', (member_id,))
        elif social == "tg":
            self.cursor.execute(f'UPDATE users SET tg="{social_id}" where member_id=?', (member_id,))
        elif social == "tiktok":
            self.cursor.execute(f'UPDATE users SET tiktok="{social_id}" where member_id=?', (member_id,))
        
        self.conn.commit()

    # Получаем все темы пользователя
    def get_themes(self, member):
        self.cursor.execute('SELECT themes FROM users WHERE member_id=?', (member.id,))
        result = self.cursor.fetchone()

        if result is not None:
            return literal_eval(result[0])
        else:
            return 0
        
    # Выдаём тему
    def give_theme(self, member, theme):
        themes = self.get_themes(member)

        themes.append(theme)

        self.cursor.execute(f'UPDATE users SET themes=? where member_id=?', (json.dumps(themes), member.id,))

        self.conn.commit()
        
    # Получаем установленную тему у пользователя
    def get_active_theme(self, member):
        self.cursor.execute('SELECT theme FROM users WHERE member_id=?', (member.id,))
        result = self.cursor.fetchone()

        if result is not None:
            return result[0]
        else:
            return 0
        
    # Устанавливаем тему
    def set_active_theme(self, member, theme):
        self.cursor.execute(f'UPDATE users SET theme="{theme}" where member_id=?', (member.id,))

        self.conn.commit()

    # Получаем общий голосовой онлайн
    def get_total_online(self, member_id):
        for row in self.cursor.execute(f'SELECT total_hours, total_minutes FROM voiceactivity_all where member_id=?', (member_id,)):
            total_online = f"{row[0]} ч."
            return total_online

    # Получаем последнюю дату получение ежедневной награды
    def get_daily_award(self, member_id):
        self.cursor.execute('SELECT daily FROM users WHERE member_id=?', (member_id,))
        result = self.cursor.fetchone()

        if result is not None:
            return result[0]
        else:
            return 0

    # Обновляем дату получения ежедневной награды
    def update_daily_award(self, member_id, newdate):
        statement = "UPDATE users SET daily = ? WHERE member_id = ?"
        if self.cursor.execute(statement, [newdate, member_id]):
            self.conn.commit()
            return True
        return False

    # Устанавливаем определенный баланс
    def set_money(self, member_id, money):
        statement = "UPDATE users SET money = ? WHERE member_id = ?"
        if self.execute_statement(statement, (money, member_id)):
            self.conn.commit()
            return True
        return False

    # Выдача денег
    def give_money(self, member_id, money):
        statement = f"UPDATE users SET money = money + {int(money)} WHERE member_id = {int(member_id)}"
        if self.execute_statement(statement):
            self.conn.commit()
            return True
        return False

    # Списание денег
    def take_money(self, member_id, money):
        statement = f"UPDATE users SET money = money - {int(money)} WHERE member_id = {int(member_id)}"
        if self.execute_statement(statement):
            self.conn.commit()
            return True
        return False

    # Получить топ пользователей по голосовому онлайну
    def get_top_users_online(self):
        self.cursor.execute(f'SELECT member_id, total_hours, total_minutes FROM voiceactivity_all ORDER BY total_hours DESC, total_minutes DESC LIMIT 30')
        row = self.cursor.fetchall()
        
        return row

    # Получить топ пользователей по балансу
    def get_top_users_balance(self):
        self.cursor.execute(f'SELECT member_id, money FROM users ORDER BY money DESC LIMIT 30')
        row = self.cursor.fetchall()
        
        return row
    
    # Получить топ пользователей по сообщениям
    def get_top_users_messages(self):
        self.cursor_log.execute(f'SELECT member_id, count FROM messages ORDER BY count DESC LIMIT 30')
        row = self.cursor_log.fetchall()

        return row

    # Transactions

    # Записываем пользователю новую транзакцию
    def write_new_transactions(self, member, category, value):
        self.cursor.execute(f"INSERT INTO transactions VALUES (?, ?, ?, ?)", (member.id, category, value, int(datetime.now().timestamp())))

        self.conn.commit()

    # Получаем все транзакции пользователя
    def get_user_transactions(self, member):
        self.cursor.execute(f'SELECT member_id, category, value, time FROM transactions WHERE member_id={member.id} ORDER BY time DESC')
        row = self.cursor.fetchall()
        
        return row

    # Marry

    # Записываем новый брак
    def write_new_marry(self, member_1, member_2):
        actual_date = datetime.now()
        end = actual_date + timedelta(days=30)

        room = {"name": 0, "total_hours": 0, "total_minutes": 0, "joined_at": 0, "id": 0}

        statement = f"INSERT INTO marrieges (partner_1, partner_2, balance, reg_marry, loveRoom, id_l, themes, theme) VALUES ({member_1.id}, '{member_2.id}', 0, '{int(actual_date.timestamp())}', '{json.dumps(room)}', 0, '[]', 'theme_default')"
        if self.execute_statement(statement):
            self.conn.commit()

            for row in self.cursor.execute(f'SELECT id FROM marrieges where partner_1=? OR partner_2=?', (member_1.id, member_2.id,)):
                self.cursor.execute(f'UPDATE users SET marry="{row[0]}" where member_id=?', (member_1.id,))
                self.cursor.execute(f'UPDATE users SET marry="{row[0]}" where member_id=?', (member_2.id,))

                self.conn.commit()
                
                return True
        return False

    # Есть ли у него уже брак?
    def is_marry(self, member_id):
        for row in self.cursor.execute(f'SELECT marry FROM users where member_id=?', (member_id,)):
            if row[0] != 0:
                return True
            else:
                return False

    # Получаем информацию о браке
    def get_info_marriege(self, member):
        for row in self.cursor.execute(f'SELECT id, partner_1, partner_2, balance, reg_marry, loveRoom FROM marrieges where partner_1=? OR partner_2=?', (member.id, member.id,)):
            return row

    def write_data_loveRoom(self, member, type, value):
        if type == 'id':
            loveRoom_data = self.get_data_loveRoom(member)
            
            loveRoom_data['id'] = 0

            self.cursor.execute("UPDATE marrieges SET loveRoom=?, id_l=? WHERE partner_1=? OR partner_2=?", (json.dumps(loveRoom_data), value, member.id, member.id,))
        else:
            loveRoom_data = self.get_data_loveRoom(member)

            loveRoom_data[type] = value

            self.cursor.execute("UPDATE marrieges SET loveRoom=? WHERE partner_1=? OR partner_2=?", (json.dumps(loveRoom_data), member.id, member.id,))

        self.conn.commit()

    def update_data_loveRoom(self, id):
        self.cursor.execute("UPDATE marrieges SET id_l=? WHERE id_l=?", (0, id,))
        self.conn.commit()

    def get_data_loveRoom(self, member):
        try:
            loveRoom_data = []

            for row in self.cursor.execute("SELECT loveRoom, id_l FROM marrieges WHERE partner_1=? OR partner_2=?", (member.id, member.id,)):
                loveRoom_data = json.loads(row[0])
                loveRoom_data['id'] = int(row[1])

            return loveRoom_data
        except Exception:
            return False

    def get_balance_marry(self, member):
        for row in self.cursor.execute("SELECT balance FROM marrieges WHERE partner_1=? OR partner_2=?", (member.id, member.id,)):
            return row[0]

    # Получаем все темы
    def get_themes_lprofile(self, member):
        self.cursor.execute('SELECT themes FROM marrieges WHERE partner_1=? OR partner_2=?', (member.id, member.id,))
        result = self.cursor.fetchone()

        if result is not None:
            return literal_eval(result[0])
        else:
            return 0
        
    # Выдаём тему
    def give_theme_lprofile(self, member, theme):
        themes = self.get_themes_lprofile(member)

        themes.append(theme)

        self.cursor.execute(f'UPDATE marrieges SET themes=? where partner_1=? OR partner_2=?', (json.dumps(themes), member.id, member.id,))

        self.conn.commit()
        
    # Получаем установленную тему у пользователя
    def get_active_theme_lprofile(self, member):
        self.cursor.execute('SELECT theme FROM marrieges WHERE partner_1=? OR partner_2=?', (member.id, member.id,))
        result = self.cursor.fetchone()

        if result is not None:
            return result[0]
        else:
            return 0
        
    # Устанавливаем тему
    def set_active_theme_lprofile(self, member, theme):
        self.cursor.execute(f'UPDATE marrieges SET theme="{theme}" where partner_1=? OR partner_2=?', (member.id, member.id,))

        self.conn.commit()

    # Устанавливаем определенный баланс
    def set_money_marry(self, member, money):
        statement = f"UPDATE marrieges SET balance = {money} WHERE partner_1 = {member.id} OR partner_2 = {member.id}"

        if self.execute_statement(statement):
            self.conn.commit()
            return True
        return False

    # Выдаём деньги
    def give_balance_marry(self, member, value):
        current_balance = self.get_balance_marry(member)

        self.cursor.execute("UPDATE marrieges SET balance=? WHERE partner_1=? OR partner_2=?", (int(current_balance + value), member.id, member.id,))

        self.conn.commit()

    # Списание денег
    def take_money_marry(self, member, money):
        current_balance = self.get_balance_marry(member)
        statement = f"UPDATE marrieges SET balance = {current_balance - money} WHERE partner_1 = {member.id} OR partner_2 = {member.id}"
        
        if self.execute_statement(statement):
            self.conn.commit()
            return True
        return False
    
    def write_log_in_history(self, partner_1, partner_2, type):
        self.cursor_log.execute(f"INSERT INTO marries_history VALUES (?, ?, ?, ?)", (partner_1.id, partner_2.id, type, int(datetime.now().timestamp())))

        self.conn_log.commit()

    def get_marries_history(self, member):
        self.cursor_log.execute(f'SELECT partner_1, partner_2, type, time FROM marries_history WHERE partner_1={member.id} OR partner_2={member.id} ORDER BY type ASC')
        row = self.cursor_log.fetchall()
        
        return row

    # Развод :(
    def divorce_marriege(self, partner_1, partner_2):
        self.cursor.execute(f'DELETE FROM marrieges WHERE partner_1=?', (partner_1,))

        self.cursor.execute(f'UPDATE users SET marry=0 where member_id=?', (partner_1,))
        self.cursor.execute(f'UPDATE users SET marry=0 where member_id=?', (partner_2,))

        self.conn.commit()

    # Personal roles

    # Добавляем новую личную роль в базу
    def write_new_role(self, member, role):
        time_pay = datetime.now() + timedelta(days=30)

        self.cursor.execute(f"INSERT INTO personal_roles VALUES ({role.id}, {member.id}, '[]', {int(time_pay.timestamp())})")

        self.conn.commit()

    # Есть у пользователя личные роли? 
    def is_exists_role(self, member):
        self.cursor.execute(f"SELECT role_id FROM personal_roles WHERE owner={member.id}")

        if self.cursor.fetchone() is None:
            return False
        else:
            return True
        
    def is_exists_role_in_shop(self, role):
        self.cursor.execute(f"SELECT role FROM shop WHERE role={role.id}")

        if self.cursor.fetchone() is None:
            return False
        else:
            return True

    # Получаем все личные роли пользователя
    def get_all_roles(self, member):
        roles_id = []

        for row in self.cursor.execute(f'SELECT role_id FROM personal_roles where owner=?', (member.id,)):
            roles_id.append(row[0])

        return roles_id
    
    # Удаляем личную роль
    def delete_role(self, role):
        self.cursor.execute(f'DELETE FROM personal_roles WHERE role_id=?', (role.id,))

        self.conn.commit()

    def get_time_to_pay(self, role):
        self.cursor.execute(f"SELECT time FROM personal_roles WHERE role_id={role.id}")

        result = self.cursor.fetchone()

        if result is None:
            return False
        else:
            return result[0]

    # Tracker

    # Записываем нового пользователя в базу трекера
    def write_new_user_tracker(self, member):
        self.cursor.execute(f"SELECT member_id FROM voiceactivity_all where member_id={member.id}")

        if not member.bot:
            if self.cursor.fetchone() is None:
                self.cursor.execute(f"INSERT INTO voiceactivity_all VALUES ({member.id}, 0, 0, 0, 0)")
            else:
                pass
            self.conn.commit()

    # Получаем данные из трекера
    def get_data(self, member):
        for row in self.cursor.execute(f"SELECT joined_at, left_at, total_hours, total_minutes FROM voiceactivity_all where member_id={member.id}"):
            return row

    # Записываем действие пользователя
    def user_set_action_channel(self, member, action):
        if action == "join":
            self.cursor.execute(f"UPDATE voiceactivity_all SET joined_at={int(datetime.timestamp(datetime.now()))} where member_id={member.id}")
        elif action == "left":
            self.cursor.execute(f"UPDATE voiceactivity_all SET left_at={int(datetime.timestamp(datetime.now()))} where member_id={member.id}")

        self.conn.commit()

    # Обновляем данные в базе
    def update_data(self, member, type, total_hours, total_minutes):
        if type == 'default':
            self.cursor.execute(f"UPDATE voiceactivity_all SET total_hours={total_hours}, total_minutes={total_minutes} where member_id={member.id}")
            self.conn.commit()
        elif type == 'love':
            loveRoom_data = self.get_data_loveRoom(member)

            loveRoom_data["total_hours"] = total_hours
            loveRoom_data["total_minutes"] = total_minutes

            self.cursor.execute(f"UPDATE marrieges SET loveRoom=? WHERE partner_1=? OR partner_2=?", (json.dumps(loveRoom_data), member.id, member.id,))
            self.conn.commit()

    # Убираем даты входа и выхода
    def set_null_dates(self, member):
        self.cursor.execute(f"UPDATE voiceactivity_all SET joined_at=0, left_at=0 where member_id={member.id}")
        self.conn.commit()

    # Shop

    # Получаем роли добавленные в магазин
    def get_shop_roles(self):
        roles = []

        for row in self.cursor.execute(f"SELECT * FROM shop"):
            roles.append(row)

        return roles

    def give_purchase(self, role):
        for row in self.cursor.execute(f'SELECT count FROM shop where role=?', (role.id,)):
            self.cursor.execute(f"UPDATE shop SET count={int(row[0]) + 1} where role={role.id}")
            
        self.conn.commit()

    # Counter messages

    def log_write_new_user(self, member):
        self.cursor_log.execute(f"SELECT member_id FROM messages WHERE member_id={member.id}")

        if not member.bot:
            if self.cursor_log.fetchone() is None:
                self.cursor_log.execute(f"INSERT INTO messages VALUES ({member.id}, 0)")
            else:
                pass
            self.conn_log.commit()

    def get_message_count(self, member):
        for row in self.cursor_log.execute(f'SELECT count FROM messages WHERE member_id={member.id}'):
            return row[0]

    def save_message_count(self, dict):
        if dict:
            for key, value in dict.items():
                for row in self.cursor_log.execute(f'SELECT count FROM messages where member_id=?', (key,)):
                    self.cursor_log.execute(f"UPDATE messages SET count={int(row[0]) + int(value)} where member_id={key}")

                    self.conn_log.commit()

    # Personal Rooms

    def write_new_personal_room(self, member, name):
        self.cursor.execute(f"INSERT INTO personal_rooms VALUES (?, ?, ?, ?, ?, ?)", (member.id, '[]', '[]', name, '0', int(datetime.now().timestamp()),))

        self.conn.commit()