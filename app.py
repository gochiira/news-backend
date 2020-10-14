from flask import Flask, g, request, jsonify
from flask_cors import CORS
from general import (
    app_before_request,
    app_after_request,
    app_teardown_appcontext,
    app_index,
    app_favicon,
    error_unauthorized,
    error_not_found,
    error_server_bombed
)
import json
import requests


NOTIFY_CHANNEL_ID = "WE6R3AP5qv2pAVaxcGGLvo"
NOTIFY_CHANNEL_SECRET = "6NsSmRpCpoCDG4HW7HYarEsZdCHrT0d2VlBP61K7qDv"
NOTIFY_ENDPOINT = "https://notify-bot.line.me/oauth/token"
NOTIFY_REDIRECT_URI_CONNECT = "https://news.gochiusa.team/connect"


def connectLineNotify():
    if request.method != "POST":
        return jsonify(status=400, message="bad request")
    params = request.get_json()
    if not params:
        return jsonify(status=400, message="bad request")
    if "code" not in params:
        return jsonify(status=400, message="bad request")
    code = params["code"]
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": NOTIFY_REDIRECT_URI_CONNECT,
        "client_id": NOTIFY_CHANNEL_ID,
        "client_secret": NOTIFY_CHANNEL_SECRET
    }
    notifyResp = requests.post(
        NOTIFY_ENDPOINT,
        headers=headers,
        data=params
    )
    if notifyResp.status_code != 200:
        return jsonify(status=401, message="authorization failed")
    notifyToken = notifyResp.json()['access_token']
    g.db.edit(
        "INSERT INTO data_user (userLineToken) VALUES (%s)",
        (notifyToken,)
    )
    return jsonify(status=200, message="ok")


def createApp():
    app = Flask(__name__)
    # 設定
    app.config['JSON_AS_ASCII'] = False
    app.config['JSON_SORT_KEYS'] = False
    # 各ページルールを登録
    app.add_url_rule(
        '/', 'index',
        app_index,
        strict_slashes=False
    )
    app.add_url_rule(
        '/connect', 'connect',
        connectLineNotify,
        strict_slashes=False
    )
    app.add_url_rule('/favicon.ico', 'favicon.ico', app_favicon)
    # リクエスト共通処理の登録
    app.before_request(app_before_request)
    app.after_request(app_after_request)
    app.teardown_appcontext(app_teardown_appcontext)
    # エラーハンドリングの登録
    app.register_error_handler(401, error_unauthorized)
    app.register_error_handler(404, error_not_found)
    app.register_error_handler(500, error_server_bombed)
    # Flask-CORSの登録 (CORSは7日間キャッシュする)
    CORS(
        app,
        methods=["GET", "POST", "OPTIONS"],
        origins=["http://localhost:3000", "https://news.gochiusa.team"],
        max_age=604800
    )
    return app


app = createApp()

if __name__ == '__main__':
    app.debug = True
    app.run(host="localhost")
