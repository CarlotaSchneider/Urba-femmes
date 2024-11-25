from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Bienvenue sur l'API Petzi !"


""" @app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()  # Récupérer les données JSON envoyées
    print(data)  # Afficher dans la console pour le débogage
    return jsonify({"message": "Webhook reçu !"}), 200 """

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()  # Récupérer les données JSON envoyées
    ticket = data.get('details', {}).get('ticket', {})
    ticket_number = ticket.get('number', 'N/A')
    ticket_title = ticket.get('title', 'N/A')
    ticket_category = ticket.get('category', 'N/A')
    ticket_price = ticket.get('price', {}).get('amount', 'N/A')
    
    buyer = data.get('details', {}).get('buyer', {})
    buyer_name = f"{buyer.get('firstName', 'N/A')} {buyer.get('lastName', 'N/A')}"

    # Afficher directement dans le navigateur
    return f"""
    <h1>Webhook reçu et traité !</h1>
    <p><strong>Ticket Number:</strong> {ticket_number}</p>
    <p><strong>Ticket Title:</strong> {ticket_title}</p>
    <p><strong>Category:</strong> {ticket_category}</p>
    <p><strong>Price:</strong> {ticket_price}</p>
    <p><strong>Buyer:</strong> {buyer_name}</p>
    """




if __name__ == '__main__':
    app.run(debug=True)
