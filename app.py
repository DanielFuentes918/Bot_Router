from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Configuraciones desde las variables de entorno
PROD_URL = os.getenv("PROD_URL")  # Webhook de producción
DEV_URL = os.getenv("DEV_URL")  # Webhook de desarrollo
PROD_BOT_PHONENUMBER = os.getenv("PROD_BOT_PHONENUMBER")  # Número de producción
DEV_BOT_PHONENUMBER = os.getenv("DEV_BOT_PHONENUMBER")  # Número de desarrollo
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
        # Depuración del request
        print("=== Debug del Request ===")
        print("URL de la solicitud:", request.url)
        print("Método HTTP:", request.method)
        print("Cabeceras:", request.headers)
        print("Argumentos en la URL:", request.args)
        print("Datos enviados (raw):", request.data)
        print("Datos parseados como JSON:", request.json)
        print("=========================")

        print (PROD_URL)
        print (DEV_URL)
        print (PROD_BOT_PHONENUMBER)
        print (DEV_BOT_PHONENUMBER)
        print (PROD_VERIFY_TOKEN)
        print (DEV_VERIFY_TOKEN)

        # Determinar el destino (producción o desarrollo) según display_phone_number
        data = request.get_json()
        print("Datos recibidos en webhook:", data)

        if 'entry' in data:
            for entry in data['entry']:
                if 'changes' in entry:
                    for change in entry['changes']:
                        if 'value' in change:
                            value = change['value']
                            print("Datos de la conversación:", value)

                            # Detectar el número asociado
                            phone_number = value.get('metadata', {}).get('display_phone_number')
                            print("Número detectado:", phone_number)
                            print(PROD_BOT_PHONENUMBER)
                            print(DEV_BOT_PHONENUMBER)
                            if phone_number == PROD_BOT_PHONENUMBER:
                                forward_url = PROD_URL
                            elif phone_number == DEV_BOT_PHONENUMBER:
                                forward_url = DEV_URL
                            else:
                                return jsonify({"error": "Número desconocido"}), 400

                            print("Redireccionando a:", forward_url)
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
