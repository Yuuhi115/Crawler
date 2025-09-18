from flask import Flask
from bilibili.app.route import api

app = Flask(__name__)
app.register_blueprint(api.product_api_bp)
app.run(host='0.0.0.0', port=5000)