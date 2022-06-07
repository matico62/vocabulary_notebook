import hashlib

import db_connection


def login_check(mail, pw):
    salt = search_salt(mail)

    if salt is None:
        return None

    b_pw = bytes(pw, "utf-8")
    b_salt = bytes(salt, "utf-8")
    hashed_pw = hashlib.pbkdf2_hmac("sha256", b_pw, b_salt, 10000).hex()

    result = search_account(mail, hashed_pw)

    return result


def search_salt(mail):
    conn = db_connection.get_connection()
    cur = conn.cursor()

    sql = "select salt from users_accounts where mail = %s"

    try:
        cur.execute(sql, (mail,))
    except Exception as e:
        print("SQL実行に失敗：", e)

    result = cur.fetchone()

    cur.close()
    conn.close()

    if result:
        return result[0]

    return None


def search_account(mail, pw):
    conn = db_connection.get_connection()
    cur = conn.cursor()

    sql = "select mail from users_accounts where mail = %s and password = %s"

    try:
        cur.execute(sql, (mail, pw))
    except Exception as e:
        print("SQL実行に失敗：", e)

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result
