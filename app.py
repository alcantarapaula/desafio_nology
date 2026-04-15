from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
CORS(app)

def connect_db():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

def calcular_cashback(tipo_cliente, valor_compra, percentual_desconto):
  valor_final = valor_compra * (1 - percentual_desconto / 100)
  if valor_final > 500:
    cashback_base = valor_final * 0.10
  else:
    cashback_base = valor_final * 0.05
  if tipo_cliente == 'normal':
    valor_cashback = cashback_base
  else:
    valor_cashback = cashback_base + (cashback_base * 0.1)
  return valor_cashback

@app.route('/cashback', methods=['POST'])
def cashback():
  data = request.get_json()
  tipo_cliente = data['tipo_cliente']
  valor_compra = data['valor_compra']
  percentual_desconto = data['percentual_desconto']
  valor_cashback = calcular_cashback(tipo_cliente, valor_compra, percentual_desconto)
  ip = request.remote_addr
  db = connect_db()
  cursor = db.cursor()
  cursor.execute("""
    INSERT INTO compras (ip, tipo_cliente, valor_compra, percentual_desconto, valor_cashback)
    VALUES (%s, %s, %s, %s, %s)
  """, (ip, tipo_cliente, valor_compra, percentual_desconto, valor_cashback))
  db.commit()
  cursor.close()
  db.close()
  return jsonify({"valor_cashback": valor_cashback})

@app.route('/consulta', methods=['GET'])
def consulta():
  ip = request.remote_addr
  db = connect_db()
  cursor = db.cursor()
  cursor.execute("""
    SELECT tipo_cliente, valor_compra, valor_cashback, criado_em FROM compras WHERE ip = %s
  """, (ip,))
  resultados = cursor.fetchall()
  cursor.close()
  db.close()
  return jsonify([{
    "tipo_cliente": linha[0],
    "valor_compra": linha[1],
    "valor_cashback": linha[2],
    "criado_em": linha[3]
  } for linha in resultados])

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
