import MySQLdb
import os


def get_connection():
    return MySQLdb.connect(
        host=os.environ["DATABASE_HOST"],
        port=int(os.environ["DATABASE_PORT"]),
        user=os.environ["DATABASE_USER"],
        passwd=os.environ["DATABASE_PASS"],
        db="flask_vocabulary",
        charset="utf8"
    )
