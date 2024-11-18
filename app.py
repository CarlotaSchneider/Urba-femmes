from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Bienvenue sur l'API Petzi !"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()  # Récupérer les données JSON envoyées
    print(data)  # Afficher dans la console pour le débogage
    return jsonify({"message": "Webhook reçu !"}), 200

if __name__ == '__main__':
    app.run(debug=True)
