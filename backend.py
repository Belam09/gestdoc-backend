from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
from gerar_pdf import gerar_documento
import os

app = Flask(__name__, static_folder=".")
CORS(app)

@app.route("/")
def index():
    return "GestDoc Backend rodando! OK"

@app.route("/gerar/<int:num>/<cnpj>")
def gerar(num, cnpj):
    try:
        os.makedirs("/tmp/docs", exist_ok=True)
        resultado = gerar_documento(num, cnpj, pasta_saida="/tmp/docs")
        if resultado["sucesso"]:
            return send_file(
                resultado["caminho"],
                as_attachment=True,
                download_name=f"doc{num}_{cnpj}.pdf",
                mimetype="application/pdf"
            )
        return jsonify(resultado), 400
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": str(e)}), 500

@app.route("/status")
def status():
    return jsonify({"status": "online", "versao": "1.0"})

if __name__ == "__main__":
    os.makedirs("/tmp/docs", exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
