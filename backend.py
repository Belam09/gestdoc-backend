from flask import Flask, send_file, jsonify
from flask_cors import CORS
from gerar_pdf import gerar_documento
import os

app = Flask(__name__, static_folder=".")
CORS(app)

@app.route("/gerar/<int:num>/<cnpj>")
def gerar(num, cnpj):
    resultado = gerar_documento(num, cnpj, pasta_saida="/tmp/docs")
    if resultado["sucesso"]:
        return send_file(resultado["caminho"], as_attachment=True)
    return jsonify(resultado), 400

@app.route("/")
def index():
    return "GestDoc Backend rodando!"

if __name__ == "__main__":
    os.makedirs("/tmp/docs", exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
