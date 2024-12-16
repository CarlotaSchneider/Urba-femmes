from flask import Flask, request, jsonify
import hmac
import pymysql
import json  # Pour convertir la charge utile en JSON

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

def insert_ticket_to_db(ticket_number, ticket_title, ticket_category, ticket_price, buyer_name, status, json_payload):
    try:
        connection = pymysql.connect(**db_settings)
        with connection.cursor() as cursor:
            # Préparer la requête SQL pour insérer les données
            sql_query = """
            INSERT INTO tickets (number, title, category, price, buyer_name, status, json)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_query, (ticket_number, ticket_title, ticket_category, ticket_price, buyer_name, status, json_payload))
            connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Erreur lors de l'insertion : {e}")
        return False

@app.route('/')
def home():
    return "TicketHub"

@app.route('/tickets', methods=["GET"])
def view_data():
    try:
        connection = pymysql.connect(**db_settings)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tickets")
            rows = cursor.fetchall()
            connection.close()

        # Transformer les données en dictionnaire avec des clés explicites
        tickets = []
        for row in rows:
            tickets.append({
                "Ticket Number": row[1],
                "Title": row[2],
                "Category": row[3],
                "Price": float(row[4]),
                "Buyer Name": row[5],
                "Status": row[6],
                "Created At": row[8]  # Inclure la date/heure
            })
        
        # Afficher dans le navigateur
        return jsonify(tickets)
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

    # Statut
    status = "reçu"

    # Convertir la charge utile en JSON pour la sauvegarde
    json_payload = json.dumps(body)  # Transformer la totalité de la requête en JSON

    # Insérer dans la base
    if insert_ticket_to_db(ticket_number, ticket_title, ticket_category, ticket_price, buyer_name, status, json_payload):
        print("Donnees inserees avec succes dans la base de donnees.")
        return jsonify({"message": "Webhook traite avec succes !"}), 200
    else:
        print("Erreur lors de l'insertion dans la base de donnees.")
        return jsonify({"error": "Database insertion failed"}), 500


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)
