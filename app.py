from flask import Flask, request, jsonify
import hmac
import pymysql
import json

app = Flask(__name__)

# Clé secrète pour la signature
secret = b"AEeyJhbGciOiJIUzUxMiIsImlzcyI6"

# Paramètres de connexion MySQL
db_settings = {
    "host": "localhost",
    "user": "myuser",
    "password": "mypassword",
    "database": "mydb"
}


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


def insert_ticket_to_db(ticket_number, ticket_title, ticket_category, ticket_price, buyer_name, status, json_payload):
    try:
        connection = pymysql.connect(**db_settings)
        with connection.cursor() as cursor:
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
    try:
        connection = pymysql.connect(**db_settings)
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM tickets")
            ticket_count = cursor.fetchone()[0]

            cursor.execute("SELECT MAX(`created_at`) FROM tickets")
            last_sale_date = cursor.fetchone()[0]

        connection.close()

        # Génération du HTML avec le dégradé rose
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>TicketHub</title>
            <style>
                /* Réinitialiser les marges et paddings */
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                /* Dégradé rose en arrière-plan */
                body {{
                    font-family: 'Arial', sans-serif;
                    background: linear-gradient(to bottom, #ff9a9e, #fad0c4);
                    color: #333;
                }}

                header {{
                    background: #333;
                    color: white;
                    padding: 15px 0;
                    text-align: center;
                    font-size: 24px;
                    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.3);
                }}

                /* Section principale */
                .main-container {{
                    padding: 20px;
                    max-width: 1000px;
                    margin: 30px auto;
                    background: #fff;
                    border-radius: 12px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }}

                h1 {{
                    text-align: center;
                    margin: 20px 0;
                    font-size: 22px;
                    color: #555;
                }}

                /* Carte dynamique */
                .cards-container {{
                    display: flex;
                    justify-content: center;
                    margin: 20px 0;
                }}

                .ticket-card {{
                    border: 1px solid #ddd;
                    box-shadow: 2px 3px 6px rgba(0, 0, 0, 0.1);
                    border-radius: 8px;
                    padding: 15px;
                    width: 260px;
                    text-align: center;
                    transition: transform 0.2s ease-in-out;
                }}

                .ticket-card:hover {{
                    transform: scale(1.05);
                }}

                .ticket-title {{
                    font-size: 18px;
                    color: #555;
                    margin-bottom: 5px;
                }}

                .ticket-details {{
                    font-size: 14px;
                    color: #777;
                }}

                /* Bouton discret sous la carte */
                .refresh-btn {{
                    text-align: center;
                    margin: 10px auto;
                    font-size: 16px;
                    color: #555;
                    cursor: pointer;
                    transition: 0.2s ease-in-out;
                }}

                .refresh-btn:hover {{
                    text-decoration: underline;
                }}

                footer {{
                    padding: 10px;
                    font-size: 14px;
                    background: #333;
                    color: white;
                    text-align: center;
                    position: fixed;
                    bottom: 0;
                    width: 100%;
                }}
            </style>
        </head>
        <body>
            <header>
                🚀 <strong>TicketHub</strong> - Suivez vos ventes
            </header>
            <div class="main-container">
                <h1>Statistiques de vos ventes récentes</h1>
                <div class="cards-container">
                    <div class="ticket-card">
                        <div class="ticket-title">🎟️ Tickets vendus : {ticket_count}</div>
                        <div class="ticket-details">📆 Dernière vente : {last_sale_date if last_sale_date else 'Aucune vente'}</div>
                    </div>
                </div>
                <!-- Bouton discret juste sous la carte -->
                <div class="refresh-btn" onclick="window.location.reload()">
                    Actualiser les données
                </div>
            </div>
            <footer>
                &copy; 2024 - TicketHub - Développé avec passion
            </footer>
        </body>
        </html>
        """
        return html
    except Exception as e:
        return f"Erreur : {str(e)}", 500


@app.route('/tickets', methods=["GET"])
def view_data():
    try:
        connection = pymysql.connect(**db_settings)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tickets")
            rows = cursor.fetchall()
        connection.close()

        tickets = [
            {
                "Ticket Number": row[1],
                "Title": row[2],
                "Category": row[3],
                "Price": float(row[4]),
                "Buyer Name": row[5],
                "Status": row[6],
                "Created At": row[8]
            } for row in rows
        ]

        return jsonify(tickets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        body = request.get_json()
        if not body:
            return jsonify({"error": "Invalid JSON payload"}), 400

        if not verify_signature(request):
            return jsonify({"error": "Invalid signature"}), 403

        ticket = body.get('details', {}).get('ticket', {})
        ticket_number = ticket.get('number', 'N/A')
        ticket_title = ticket.get('title', 'N/A')
        ticket_category = ticket.get('category', 'N/A')
        ticket_price = float(ticket.get('price', {}).get('amount', 0))
        
        buyer = body.get('details', {}).get('buyer', {})
        buyer_name = f"{buyer.get('firstName', 'N/A')} {buyer.get('lastName', 'N/A')}"

        status = "reçu"
        json_payload = json.dumps(body)

        if insert_ticket_to_db(ticket_number, ticket_title, ticket_category, ticket_price, buyer_name, status, json_payload):
            return jsonify({"message": "Webhook traite avec succes"}), 200
        else:
            return jsonify({"error": "Erreur lors de l'insertion dans la base"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)
