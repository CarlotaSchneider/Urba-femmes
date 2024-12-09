from flask import Flask, request, jsonify
import hmac

app = Flask(__name__)

# Clé secrète pour la signature
secret = b"AEeyJhbGciOiJIUzUxMiIsImlzcyI6"

def verify_signature(request):
    # Récupérer la signature et le timestamp depuis les headers
    signature_with_timestamp = request.headers.get("Petzi-Signature")
    if not signature_with_timestamp:
        return False  # Pas de signature dans les headers
    
    try:
        # Extraire les parties de la signature
        signature_parts = dict(part.split("=") for part in signature_with_timestamp.split(","))
        timestamp = signature_parts["t"]
        signature = signature_parts["v1"]
    except (ValueError, KeyError):
        return False  # Signature mal formée
    
    # Préparer la chaîne à signer
    body_to_sign = f'{timestamp}.{request.data.decode()}'.encode()
    
    # Calculer la signature attendue
    expected_signature = hmac.new(secret, body_to_sign, "sha256").hexdigest()
    
    # Comparer les signatures
    return hmac.compare_digest(expected_signature, signature)

@app.route('/')
def home():
    return "Bienvenue sur l'API Petzi !"

@app.route('/webhook', methods=['POST'])
def webhook():
    # Récupérer le corps de la requête JSON
    body = request.get_json()
    if not body:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Vérifier la signature
    if not verify_signature(request):
        return jsonify({"error": "Invalid signature"}), 403

    # Extraire les détails du ticket
    ticket = body.get('details', {}).get('ticket', {})
    ticket_number = ticket.get('number', 'N/A')
    ticket_title = ticket.get('title', 'N/A')
    ticket_category = ticket.get('category', 'N/A')
    ticket_price = ticket.get('price', {}).get('amount', 'N/A')
    
    # Extraire les informations de l'acheteur
    buyer = body.get('details', {}).get('buyer', {})
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
    app.run(debug=True, host="127.0.0.1", port=5000)
