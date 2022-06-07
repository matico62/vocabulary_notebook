import datetime
import os
import random
import re
from functools import wraps

import account
import login
import vocabulary
from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)

app.secret_key = os.urandom(64)
app.permanent_session_lifetime = datetime.timedelta(minutes=30)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # ユーザのセッションがない場合ログイン画面へ遷移
        if 'user' not in session:
            return redirect("/vocabulary_notebook")
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def login_page():
    error = request.args.get("error")
    # ログイン画面
    return render_template("login.html", error=error)


@app.route("/top", methods=["POST"])
def top_post():
    mail = request.form.get("mail")
    pw = request.form.get("pw")

    login_user = login.login_check(mail, pw)

    if login_user is not None:
        session["user"] = login_user
        return render_template("top.html")
    else:
        return redirect(url_for('login_page', error="ログインに失敗しました。"))


@app.route("/top", methods=["GET"])
@login_required
def top_get():
    return render_template("top.html")


@app.route("/create_account")
def create_account():
    error = request.args.get("error")

    year = [i for i in range(1900, datetime.date.today().year + 1)[::-1]]
    month = [i for i in range(1, 13)[::-1]]
    day = [i for i in range(1, 32)[::-1]]

    # アカウント登録画面
    return render_template("create_account.html", year=year, month=month, day=day, error=error)


@app.route("/check_account", methods=["POST"])
def check_account():
    # 受け取ったパスワードをマスキング
    mask_pw = re.sub("[a-z]", "●", request.form.get("pw"))
    mask_pw = re.sub("[A-Z]", "●", mask_pw)

    # 登録画面で入力されたユーザ情報
    tmp_account = {
        'first_name': request.form.get("first_name"),
        'last_name': request.form.get("last_name"),
        'first_fri': request.form.get("first_fri"),
        'last_fri': request.form.get("last_fri"),
        'year': request.form.get("year"),
        'month': request.form.get("month"),
        'day': request.form.get("day"),
        'mail': request.form.get("mail"),
        'pw': request.form.get("pw"),
        'mask_pw': mask_pw,
    }

    # 仮のユーザをセッションに格納
    session['tmp_account'] = tmp_account

    # アカウント確認画面
    return render_template("check_account.html", tmp_account=tmp_account)


@app.route("/mail_activate")
def mail_activate():
    error = request.args.get("error")

    # コード認証のコードを作成
    code = random.randrange(10 ** 5, 10 ** 6)
    # メールを送る
    account.activate_mail(code, session['tmp_account'])
    # セッションに作成したコードを格納
    session['code'] = code
    # メール送信完了画面
    return render_template("mail_activate.html", error=error)


@app.route("/result_account")
def result_account():
    # 入力されたコードを取得
    # answer = request.form.get("code")

    # 入力されたコードが正しいか
    # if answer == str(session['code']):
    tmp_account = session['tmp_account']
    # ユーザの登録
    insert_check = account.insert_account(
        first_name=tmp_account['first_name'],
        last_name=tmp_account['last_name'],
        first_fri=tmp_account['first_fri'],
        last_fri=tmp_account['last_fri'],
        year=tmp_account['year'],
        month=tmp_account['month'],
        day=tmp_account['day'],
        mail=tmp_account['mail'],
        pw=tmp_account['pw']
    )

    # 登録できたかチェック
    if insert_check is True:
        # 登録完了メールの送信
        # account.send_mail(session['tmp_account'])
        session['user'] = tmp_account['mail']
        # 登録完了画面へ遷移
        return redirect(url_for('top_get'))
    else:
        # 登録できなかった場合アカウント作成画面へ遷移
        return redirect(url_for('create_account', error='アカウントの登録に失敗しました。'))


# else:
# コードが正しくなかった場合メール送信完了画面へ遷移
# return redirect(url_for('mail_activate', error='コード認証に失敗しました。'))


@app.route("/vocabulary_top")
@login_required
def vocabulary_top():
    # ユーザが登録している英単語の取得
    word = vocabulary.select_vocabulary(session['user'])
    # 英単語帳トップ画面へ遷移
    return render_template("vocabulary_top.html", word=word)


@app.route("/vocabulary_search")
@login_required
def vocabulary_search():
    # 英単語の検索ワードを取得
    search = request.args.get("search")
    # 英単語を検索する
    search_result = vocabulary.search_vocabulary(search_word=search, mail=session['user'])
    # 英単語帳トップページへ遷移
    return render_template("vocabulary_top.html", word=search_result)


@app.route("/vocabulary_insert")
@login_required
def vocabulary_insert():
    error = request.args.get("error")
    # 英単語登録画面へ遷移
    return render_template("vocabulary_insert.html", error=error)


@app.route("/vocabulary_insert_result")
@login_required
def vocabulary_insert_result():
    # 登録する単語・意味を取得
    word = request.args.get("word")
    meaning = request.args.get("meaning")

    # 単語の登録
    insert_check = vocabulary.insert_vocabulary(word=word, meaning=meaning, mail=session['user'])

    if insert_check is False:
        return redirect(url_for("vocabulary_insert", error="登録に失敗しました。"))
    return render_template("vocabulary_insert_result.html", word=[word, meaning], value="登録")


@app.route("/vocabulary_delete")
@login_required
def vocabulary_delete():
    error = request.args.get("error")
    # ユーザが登録している英単語の取得
    word = vocabulary.select_vocabulary(session['user'])
    # 英単語削除画面へ遷移
    return render_template("vocabulary_delete.html", word=word, error=error)


@app.route("/vocabulary_delete_search")
@login_required
def vocabulary_delete_search():
    error = request.args.get("error")
    # 英単語の検索ワードを取得
    search = request.args.get("search")
    # 英単語を検索する
    word = vocabulary.search_vocabulary(search_word=search, mail=session['user'])
    # 英単語削除画面へ遷移
    return render_template("vocabulary_delete.html", word=word, error=error)


@app.route("/vocabulary_delete_result")
@login_required
def vocabulary_delete_result():
    # 削除する英単語を取得
    word_ids = request.args.getlist("delete_checkbox")
    # 単語の削除
    delete_check = vocabulary.delete_vocabulary(word_ids=word_ids, mail=session['user'][0])

    # 削除できなかった時
    if delete_check is None:
        return redirect(url_for("vocabulary_delete", error="削除に失敗しました。"))

    return render_template("vocabulary_delete_result.html", word=delete_check, value="削除")


@app.route("/quiz_top")
@login_required
def quiz_top():
    error = request.args.get("error")

    # 単語クイズ画面へ遷移
    return render_template("quiz_top.html", error=error)


@app.route("/quiz")
@login_required
def question():
    # クイズの選択肢を取得する
    user_answer = request.args.getlist("ans")
    if user_answer:
        # 選択肢を取得出来たら回答を保存する
        user_answers = session['user_answers']
        user_answers.append(user_answer)
        session['user_answers'] = user_answers
        # 10問回答するまで繰り返す
        if session['quiz_index'] < 9:
            session['quiz_index'] += 1
            return render_template(
                "quiz.html",
                quiz_lists=session['quiz_lists'],
                answer_lists=session['answer_lists'],
                quiz_index=session['quiz_index']
            )
        else:
            # 回答し終わったら結果画面へ遷移する
            return redirect(url_for('quiz_result'))

    # 10問英単語クイズを作成する
    # 登録している単語全部を取得
    all_user_word = vocabulary.quiz_vocabulary(session['user'])
    user_word_list = [list(word) for word in all_user_word]

    # 登録している英単語が10単語以上あるか
    if len(all_user_word) >= 10:
        answer_lists = random.sample(user_word_list, 10)
        quiz_lists = answer_lists.copy()

        for (index, answer) in enumerate(quiz_lists):
            # 答え以外の選択肢を3個取得
            quiz_options = random.sample(user_word_list, 3)
            # 選択肢が答えと被らなくなるまで繰り返す
            while answer in quiz_options:
                quiz_options = random.sample(user_word_list, 3)
            quiz_lists[index] = [answer]
            quiz_lists[index].extend(quiz_options)
            # 選択肢をシャッフルする
            random.shuffle(quiz_lists[index])

        session['answer_lists'] = answer_lists
        session['quiz_lists'] = quiz_lists
        session['quiz_index'] = 0
        session['user_answers'] = []

        return render_template(
            "quiz.html",
            quiz_lists=quiz_lists,
            answer_lists=answer_lists,
            quiz_index=session['quiz_index']
        )
    else:
        return redirect(url_for('quiz_top', error='登録単語が10個以上で解禁されます。'))


@app.route("/quiz_result")
def quiz_result():
    # 回答と答えを取得
    answer_lists = session['answer_lists']
    user_answers = session['user_answers']

    correct_count = 0

    answer_results = answer_lists.copy()
    for (index, answer) in enumerate(answer_results):
        # 答えと回答が正しいチェック
        if answer == user_answers[index]:
            answer.append("O")
            correct_count += 1
        else:
            answer.append("X")
        answer.insert(2, user_answers[index][1])

    return render_template(
        "quiz_result.html",
        answer_results=answer_results,
        correct_count=correct_count
    )


@app.route("/logout")
def logout():
    # ログアウト
    session.clear()
    return redirect(url_for('login_page'))
