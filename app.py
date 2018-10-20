from flask import Flask

app = Flask(__name__)

from proxy_pool.database import RedisClient


redis_client = RedisClient()

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/proxy-ip')
def proxyIp():
    res = redis_client.get_proxies(count=10)
    proxyIp = list()
    for ip in res:
        proxyIp.append(ip.strip('http://'))
    return "<br>".join(proxyIp)

if __name__ == '__main__':
    """
    FLASK_APP=app.py flask run
    """
    app.run(host='0.0.0.0', port=80, debug=True)