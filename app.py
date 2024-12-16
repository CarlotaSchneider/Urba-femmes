from flask import Flask, request, jsonify
import hmac
import pymysql

app = Flask(__name__)

# Clé secrète pour la signature
secret = b"AEeyJhbGciOiJIUzUxMiIsImlzcyI6"

def verify_signature(request):
    signature_with_timestamp = request.headers.get("Petzi-Signature")
    if not signature_with_timestamp:
        return False
    
    try:
        signature_parts = dict(part.split("=") for part in signature_with_timestamp.split(","))
        timestamp = signature_parts["t"]
        signature = signature_parts["v1"]
    except (ValueError, KeyError):
        return False
    
    body_to_sign = f'{timestamp}.{request.data.decode()}'.encode()
    expected_signature = hmac.new(secret, body_to_sign, "sha256").hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)

# Paramètres de connexion MySQL
db_settings = {
    "host": "localhost",
    "user": "myuser",
    "password": "mypassword",
    "database": "mydb"
}

def insert_ticket_to_db(ticket_number, ticket_title, ticket_category, ticket_price, buyer_name, status):
    try:
        connection = pymysql.connect(**db_settings)
        with connection.cursor() as cursor:
            # Préparer la requête SQL pour insérer les données
            sql_query = """
            INSERT INTO tickets (number, title, category, price, buyer_name, status) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_query, (ticket_number, ticket_title, ticket_category, ticket_price, buyer_name, status))
            connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Erreur lors de l'insertion : {e}")
        return False

@app.route('/')
def home():
    return "Bienvenue sur l'API MySQL avec Flask!"

@app.route('/database', methods=["GET"])
def view_data():
    try:
        connection = pymysql.connect(**db_settings)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tickets")
            rows = cursor.fetchall()
            connection.close()
        
        # Afficher dans le navigateur
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    body = request.get_json()
    if not body:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Vérifier la signature
    if not verify_signature(request):
        return jsonify({"error": "Invalid signature"}), 403

    # Extraire les données du ticket
    ticket = body.get('details', {}).get('ticket', {})
    ticket_number = ticket.get('number', 'N/A')
    ticket_title = ticket.get('title', 'N/A')
    ticket_category = ticket.get('category', 'N/A')
    ticket_price = float(ticket.get('price', {}).get('amount', 0))
    
    # Extraire les informations de l'acheteur
    buyer = body.get('details', {}).get('buyer', {})
    buyer_name = f"{buyer.get('firstName', 'N/A')} {buyer.get('lastName', 'N/A')}"

    # Statut (par exemple : "reçu", "confirmé", etc.)
    status = "reçu"

    # Insérer dans la base
    if insert_ticket_to_db(ticket_number, ticket_title, ticket_category, ticket_price, buyer_name, status):
        return f"""
        <h1>Webhook traité avec succès !</h1>
        <p><strong>Ticket Number:</strong> {ticket_number}</p>
        <p><strong>Ticket Title:</strong> {ticket_title}</p>
        <p><strong>Category:</strong> {ticket_category}</p>
        <p><strong>Price:</strong> {ticket_price} CHF</p>
        <p><strong>Buyer:</strong> {buyer_name}</p>
        <p><strong>Status:</strong> {status}</p>
        """
    else:
        return jsonify({"error": "Database insertion failed"}), 500


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)
