import os
import urllib.parse
from peewee import SqliteDatabase, Model, CharField, IntegerField, PostgresqlDatabase
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from app import login


if os.environ.get("DATABASE_URL"):
    url = urllib.parse.urlparse(os.environ.get("DATABASE_URL"))
    db = PostgresqlDatabase(host=url.hostname, user=url.username, password=url.password, port=url.port,
                            database=url.path[1:])
else:
    db = SqliteDatabase('linkshortener.db')


@login.user_loader
def load_user(id):
    return User[id]


class User(UserMixin, Model):
    class Meta:
        database = db
        db_table = "users"

    username = CharField(max_length=32)
    email = CharField(max_length=32, unique=True)
    password = CharField(max_length=128)

    def __repr__(self):
        return f"<User {self.username}>"

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Url(Model):
    class Meta:
        database = db
        db_table = "urls"

    url = CharField(max_length=256)
    email = CharField(max_length=32, null=True)
    counter = IntegerField(default=0)


def start_db():

    if not User.table_exists():
        User.create_table()
        print("User db created!")

    if not Url.table_exists():
        Url.create_table()
        print('Url db created!')
