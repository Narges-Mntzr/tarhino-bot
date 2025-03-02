import psycopg2

from models import User, Poster
import config


class Database:
    connection = psycopg2.connect(
        dbname="postgres",  # Default database
        user="postgres",
        password=config.POSTGRES_PASS,
        host=config.POSTGRES_HOST,
        port="5432",
    )

    @classmethod
    def create_tables(cls):
        cls.create_bot_users_table()
        cls.create_poster_table()

    @classmethod
    def create_bot_users_table(cls):
        sql = """
        CREATE TABLE IF NOT EXISTS bot_users (
            user_id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            phone_number TEXT,
            is_admin BOOLEAN,
            font TEXT,
            color1 TEXT,
            color2 TEXT,
            color_text TEXT
        )
        """
        cursor = cls.connection.cursor()
        cursor.execute(sql)
        cls.connection.commit()
        cursor.close()

    @classmethod
    def create_poster_table(cls):
        sql = """
        CREATE TABLE IF NOT EXISTS poster_table (
            id SERIAL PRIMARY KEY,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER REFERENCES bot_users(user_id),
            font TEXT,
            color1 TEXT,
            color2 TEXT,
            text_color TEXT,
            template TEXT,
            orientation TEXT,
            initial_image TEXT,
            title TEXT,
            message_text TEXT,
            output_image TEXT
        )
        """
        cursor = cls.connection.cursor()
        cursor.execute(sql)
        cls.connection.commit()
        cursor.close()

    @classmethod
    def insert_user(cls, user):
        sql = """INSERT INTO bot_users (user_id, name, phone_number, is_admin, font, color1, color2, color_text)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor = cls.connection.cursor()
        cursor.execute(
            sql,
            (
                user.id,
                user.name,
                user.phone_number,
                user.is_admin,
                user.font,
                user.color1,
                user.color2,
                user.color_text,
            ),
        )
        cls.connection.commit()
        cursor.close()

    @classmethod
    def update_user(cls, user):
        sql = """UPDATE bot_users 
                 SET name = %s, phone_number = %s, is_admin = %s, font = %s, color1 = %s, color2 = %s, color_text = %s
                 WHERE user_id = %s"""
        cursor = cls.connection.cursor()
        cursor.execute(
            sql,
            (
                user.name,
                user.phone_number,
                user.is_admin,
                user.font,
                user.color1,
                user.color2,
                user.color_text,
                user.id,
            ),
        )
        cls.connection.commit()
        cursor.close()

    @classmethod
    def save_user(cls, user):
        result = cls.select_user(user.id)
        if result is None:
            cls.insert_user(user)
        else:
            cls.update_user(user)

    @classmethod
    def select_user(cls, user_id):
        sql = """SELECT * FROM bot_users WHERE user_id = %s"""
        cursor = cls.connection.cursor()
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    @classmethod
    def load_user(cls, user_id):
        result = cls.select_user(user_id)
        if result is None:
            return User(user_id)
        return User(*result)

    @classmethod
    def insert_poster(cls, poster):
        sql = """INSERT INTO poster_table (user_id, font, color1, color2, text_color, template, orientation, initial_image, title, message_text, output_image)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cursor = cls.connection.cursor()
        cursor.execute(
            sql,
            (
                poster.user_id,
                poster.font,
                poster.color1,
                poster.color2,
                poster.text_color,
                poster.template,
                poster.orientation,
                poster.initial_image,
                poster.title,
                poster.message_text,
                poster.output_image,
            ),
        )
        cls.connection.commit()
        cursor.close()

    @classmethod
    def load_posters_by_user(cls, user_id):
        result = cls.select_poster(user_id)
        user_result = cls.select_user(user_id)
        if result is None:
            if user_result:
                user = User(*user_result)
                return Poster(
                    id=None,
                    user_id=user.id,
                    font=user.font,
                    color1=user.color1,
                    color2=user.color2,
                    text_color=user.color_text,
                )
            else:
                return Poster(user_id=user_id)
        return Poster(*result)

    @classmethod
    def update_poster(cls, poster):
        sql = """UPDATE poster_table 
                SET user_id = %s, font = %s, color1 = %s, color2 = %s, text_color = %s,
                    template = %s, orientation = %s, initial_image = %s,
                    title = %s, message_text = %s, output_image = %s
                WHERE id = %s"""
        cursor = cls.connection.cursor()
        cursor.execute(
            sql,
            (
                poster.user_id,
                poster.font,
                poster.color1,
                poster.color2,
                poster.text_color,
                poster.template,
                poster.orientation,
                poster.initial_image,
                poster.title,
                poster.message_text,
                poster.output_image,
                poster.id,
            ),
        )
        cls.connection.commit()
        cursor.close()

    @classmethod
    def select_poster(cls, user_id):
        sql = """
            SELECT * FROM poster_table 
            WHERE user_id = %s AND output_image IS NULL 
            ORDER BY date DESC LIMIT 1
        """
        cursor = cls.connection.cursor()
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    @classmethod
    def save_poster(cls, poster):
        result = cls.select_poster(poster.user_id)
        if result is None:
            cls.insert_poster(poster)
        else:
            cls.update_poster(poster)


Database.create_tables()
