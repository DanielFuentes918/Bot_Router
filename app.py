from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from Config import Config
from Utils import pull
config = Config()

app = Flask(__name__)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Manejo de verificación del webhook
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        # Determinar el verify_token correcto
        if verify_token == config.PROD_VERIFY_TOKEN:
            return str(challenge), 200
        else:
            return "Verificación de token fallida", 403

    elif request.method == 'POST':
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
                            print(config.PROD_BOT_PHONENUMBER)
                            print(config.DEV_BOT_PHONENUMBER)
                            if phone_number == config.PROD_BOT_PHONENUMBER:
                                forward_url = config.PROD_URL
                            elif phone_number == config.DEV_BOT_PHONENUMBER:
                                forward_url = config.DEV_URL
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

@app.route('/pull', methods=['GET', 'POST'])
def pullIdentification():
    response = {"status": "success", "message": "Operación recibida y en proceso."}

    try:
        # Obtener los datos del JSON enviado en la solicitud
        data = request.json
        print(f"Datos recibidos: {data}")

        # Verificar si el campo 'ref' existe en los datos
        if 'ref' in data:
            # Extraer la rama (sin la parte 'refs/heads/')
            branch = data['ref'].replace('refs/heads/', '')
            print(f"La rama en la que se hizo el commit es: {branch}")
            if branch.lower() == 'main':
                load_dotenv()
                repo_path = os.getenv("repo_path")
                service = os.getenv("service")
                pull(repo_path, service)
            elif branch.lower() == 'dev':
                load_dotenv()
                repo_path = os.getenv("repo_path2")
                service = os.getenv("service2")
                pull(repo_path, service)
            else:
                response = {"status": "error", "message": "Rama no válida."}
        else:
            response = {"status": "error", "message": "Campo 'ref' no encontrado en los datos recibidos."}

    except Exception as e:
        response = {"status": "error", "message": f"Error interno: {str(e)}"}


    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
