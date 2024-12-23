from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Configuraciones desde las variables de entorno
PROD_URL = os.getenv("PROD_URL")  # Webhook de producción
DEV_URL = os.getenv("DEV_URL")  # Webhook de desarrollo
PROD_API_URL = os.getenv("PROD_API_URL")  # API de WhatsApp para producción
DEV_API_URL = os.getenv("DEV_API_URL")  # API de WhatsApp para desarrollo
PROD_VERIFY_TOKEN = os.getenv("PROD_VERIFY_TOKEN")  # Verify token para producción
DEV_VERIFY_TOKEN = os.getenv("DEV_VERIFY_TOKEN")  # Verify token para desarrollo

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Manejo de verificación del webhook
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        # Determinar el verify_token correcto
        if verify_token == PROD_VERIFY_TOKEN:
            return str(challenge), 200
        elif verify_token == DEV_VERIFY_TOKEN:
            return str(challenge), 200
        else:
            return "Verificación de token fallida", 403

    elif request.method == 'POST':
        # Determinar el destino (producción o desarrollo) según el origen del API de WhatsApp
        data = request.get_json()
        print("Datos recibidos en webhook:", data)

        # Validar el campo "messages" y el origen de la API de WhatsApp
        if 'entry' in data:
            for entry in data['entry']:
                if 'changes' in entry:
                    for change in entry['changes']:
                        if 'value' in change:
                            value = change['value']
                            # Detectar el API de WhatsApp usado
                            api_url = value.get('metadata', {}).get('api_url')
                            if api_url == PROD_API_URL:
                                forward_url = PROD_URL
                            elif api_url == DEV_API_URL:
                                forward_url = DEV_URL
                            else:
                                return jsonify({"error": "API desconocida"}), 400
                            print("Redireccionando.... :",forward_url)
                            # Reenviar la solicitud al destino adecuado
                            response = requests.post(
                                forward_url,
                                json=data,
                                headers={
                                    "Content-Type": "application/json",
                                    "Authorization": request.headers.get("Authorization")
                                }
                            )
                            print(f"Reenviando a {forward_url}: {response.status_code}")
                            return jsonify({"status": "success"}), response.status_code

        return jsonify({"error": "Datos no válidos"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
