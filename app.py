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

@app.route('/send_notification', methods=['POST'])
def send_notification():
    print("Datos recibidos en send_notification:", request.json)
    try:
        # Obtener los datos de la solicitud
        data = request.get_json()
        # headers = dict(request.headers)  # Copiar los encabezados

        # URL al puerto interno 5002
        forward_url = "http://127.0.0.1:5002/send_notification"

        # Reenviar la solicitud al puerto 5002
        response = requests.post(forward_url, json=data)

        # Devolver la respuesta del servidor interno
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/all_truck_details', methods=['GET'])
def redirect_all_truck_details():
    print("Solicitud recibida en /all_truck_details")

    try:
        # URL al puerto interno donde se procesan las solicitudes relacionadas con AllTruckDetails
        forward_url = "http://127.0.0.1:5002/all_truck_details"

        # Pasar los parámetros de la solicitud GET a la redirección
        params = request.args

        # Realizar la redirección mediante una solicitud GET al forward_url
        response = requests.get(forward_url, params=params)

        # Devolver la respuesta del servidor interno
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/activar_gps', methods=['POST'])
def redirect_activar_gps():
    print("Solicitud recibida en /activar_gps")
    try:
        data = request.get_json()
        print("Datos recibidos:", data)

        # URL del servicio real del scraper
        forward_url = "http://127.0.0.1:5002/activar_gps"

        response = requests.post(forward_url, json=data)
        print("Respuesta del servicio:", response.text)

        return jsonify(response.json()), response.status_code
    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
