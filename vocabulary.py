import db_connection


def select_vocabulary(mail):
    conn = db_connection.get_connection()
    cur = conn.cursor()

    sql = "select id, word, meaning from vocabulary_lists where mail = %s"

    try:
        cur.execute(sql, (mail,))
    except Exception as e:
        cur.close()
        conn.close()
        return None

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result


def quiz_vocabulary(mail):
    conn = db_connection.get_connection()
    cur = conn.cursor()

    sql = "select word, meaning from vocabulary_lists where mail = %s"

    try:
        cur.execute(sql, (mail,))
    except Exception as e:
        cur.close()
        conn.close()
        return None

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result


def search_vocabulary(search_word, mail):
    conn = db_connection.get_connection()
    cur = conn.cursor()

    sql = "select id, word, meaning from vocabulary_lists where word like %s and mail = %s"

    try:
        cur.execute(sql, ("%" + search_word + "%", mail))
    except Exception as e:
        cur.close()
        conn.close()
        return None

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result


def insert_vocabulary(word, meaning, mail):
    conn = db_connection.get_connection()
    cur = conn.cursor()

    sql = "insert into vocabulary_lists(word, meaning, mail) values(%s, %s, %s)"

    try:
        cur.execute(sql, (word, meaning, mail))
    except Exception as e:
        cur.close()
        conn.close()
        return False

    cur.close()
    conn.commit()
    conn.close()

    return True


def delete_vocabulary(word_ids, mail):
    conn = db_connection.get_connection()
    cur = conn.cursor()

    in_operator = ','.join(['%s'] * len(word_ids))
    select_sql = f"select word, meaning from vocabulary_lists where id in ({in_operator}) and mail = %s"
    delete_sql = "delete from vocabulary_lists where id = %s and mail = %s"

    try:
        word_ids.append(mail)
        cur.execute(select_sql, word_ids)
        result = cur.fetchall()

        for word_id in word_ids[:-1]:
            cur.execute(delete_sql, (word_id, mail))

        cur.close()
        conn.commit()
        conn.close()

        return result
    except Exception as e:
        cur.close()
        conn.close()
        return None
