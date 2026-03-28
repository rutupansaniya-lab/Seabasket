from config.db_config import engine
from models.users_table import users_table

class DBHelper:
    def get_user_by_email(email: str):
        with engine.connect() as db:
            return db.execute(users_table.select().where(users_table.c.email == email)).fetchone()

    def get_user_by_id(id: int):
        with engine.connect() as db:
            return db.execute(users_table.select().where(
                users_table.c.id == id)).fetchone()
 