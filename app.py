from flask import Flask

app = Flask(__name__)

from proxy_pool.database import RedisClient


redis_client = RedisClient()

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/proxy-ip')
def proxyIp():
    res = redis_client.pop_proxy()
    return "\r\n".join(res)


if __name__ == '__main__':
    """
    FLASK_APP=app.py flask run
    """
    app.run(host='0.0.0.0', port=80, debug=True)