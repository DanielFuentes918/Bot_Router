from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Configuraciones desde las variables de entorno
load_dotenv()
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

import subprocess
from threading import Thread

@app.route('/pull', methods=['POST'])
def pull():
    """
    Ruta para ejecutar un git pull y reiniciar el servicio
    """
    try:
        # Responde inmediatamente para evitar tiempo de espera
        response = {"status": "success", "message": "Operación recibida y en proceso."}

        # Define una función para ejecutar las operaciones en segundo plano
        def execute_operations():
            try:
                repo_path = os.getenv("REPO_PATH", "/home/exasa/BotRouter/Bot_Router")  # Ruta del repositorio
                service_name = os.getenv("SERVICE_NAME", "router_flask")  # Nombre del servicio a reiniciar

                # Cambiar al directorio del repositorio
                print(f"Cambiando al directorio: {repo_path}")
                subprocess.run(["cd", repo_path], check=True, shell=True)

                # Ejecutar git pull
                print("Ejecutando git pull...")
                pull_result = subprocess.run(["git", "pull"], cwd=repo_path, capture_output=True, text=True)
                print(f"Git pull stdout: {pull_result.stdout}")
                print(f"Git pull stderr: {pull_result.stderr}")

                if pull_result.returncode != 0:
                    print(f"Error en git pull: {pull_result.stderr}")
                    return

                # Reiniciar el servicio
                print(f"Reiniciando el servicio: {service_name}")
                restart_result = subprocess.run(["sudo", "systemctl", "restart", service_name], capture_output=True, text=True)
                print(f"Service restart stdout: {restart_result.stdout}")
                print(f"Service restart stderr: {restart_result.stderr}")

                if restart_result.returncode != 0:
                    print(f"Error al reiniciar el servicio: {restart_result.stderr}")

            except Exception as e:
                print(f"Error en la operación: {e}")

        # Ejecutar las operaciones en un hilo separado para no bloquear la respuesta
        Thread(target=execute_operations).start()

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
