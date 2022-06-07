import os
import hashlib
import random
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

import db_connection


def insert_account(first_name, last_name, first_fri, last_fri, year, month, day, mail, pw):
    day = f"{year}-{month}-{day}"
    salt = "".join(random.choices(string.ascii_letters, k=16))

    b_pw = bytes(pw, "utf-8")
    b_salt = bytes(salt, "utf-8")
    hashed_pw = hashlib.pbkdf2_hmac("sha256", b_pw, b_salt, 10000).hex()

    conn = db_connection.get_connection()
    cur = conn.cursor()
    sql = "insert into users_accounts values(%s,%s,%s,%s,%s,%s,%s,%s)"

    try:
        cur.execute(sql, (last_name, first_name, first_fri, last_fri, day, mail, hashed_pw, salt))
    except Exception as e:
        return False

    cur.close()
    conn.commit()
    conn.close()

    return True


def activate_mail(code, tmp_account):
    ID = "tailangh830@gmail.com"
    PASS = "takukihime4"
    HOST = "smtp.gmail.com"
    PORT = 587

    body = f'''{tmp_account['last_name']}{tmp_account['first_name']} 様<br>
                単語帳をご利用いただき、誠にありがとうございます。<br>
                本メールは、「単語帳」の認証コード送信メールです。<br>
                下記の認証コードをアカウント登録画面に入力してアカウント認証手続きを進めてください。<br>
                -------------------------<br>
                認証コード：{code}<br>
                -------------------------
                '''
    subject = "【単語帳】認証コードをご確認ください。"
    to = tmp_account['mail']

    msg = MIMEMultipart()
    msg.attach(MIMEText(body, "html"))

    msg["Subject"] = subject
    msg["From"] = ID
    msg["To"] = to

    server = SMTP(HOST, PORT)
    server.starttls()

    server.login(ID, PASS)

    server.send_message(msg)

    server.quit()


def send_mail(tmp_account):
    ID = os.environ["MAIL_ID"]
    PASS = os.environ["MAIL_PASS"]
    HOST = os.environ["MAIL_HOST"]
    PORT = os.environ["MAIL_PORT"]

    body = f'''{tmp_account['last_name']+tmp_account['first_name']} 様<br>
                単語帳をご利用いただき、誠にありがとうございます。<br>
                会員登録が完了いたしましたので、お知らせいたします。<br>
                -------------------------<br>
                ご登録内容<br>
                -------------------------<br>
                お名前：{tmp_account['last_name']+tmp_account['first_name']}<br>
                生年月日：{tmp_account['year']}年{tmp_account['month']}月{tmp_account['day']}日<br>
                メールアドレス：{tmp_account['mail']}<br>
                -------------------------
                '''
    subject = "【単語帳】会員登録完了のお知らせ"
    to = tmp_account['mail']

    msg = MIMEMultipart()
    msg.attach(MIMEText(body, "html"))

    msg["Subject"] = subject
    msg["From"] = ID
    msg["To"] = to

    server = SMTP(HOST, PORT)
    server.starttls()

    server.login(ID, PASS)

    server.send_message(msg)

    server.quit()
