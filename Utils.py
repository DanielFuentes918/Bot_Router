from flask import request, jsonify
import subprocess
from threading import Thread
import os
from dotenv import load_dotenv


def pull(repo_path, service):
    try:
        os.chdir(repo_path)

        # Ejecutar git pull
        pull_result = subprocess.run(["git", "pull"], capture_output=True, text=True)
        print(f"Git pull stdout: {pull_result.stdout}")
        print(f"Git pull stderr: {pull_result.stderr}")

        # Verificar si git pull tuvo éxito
        if pull_result.returncode != 0:
            print(f"Error al ejecutar git pull: {pull_result.stderr}")

        # Reiniciar el servicio
        restart_result = subprocess.run(["sudo", "systemctl", "restart", service], capture_output=True, text=True)
        print(f"Service restart stdout: {restart_result.stdout}")
        print(f"Service restart stderr: {restart_result.stderr}")

        if restart_result.returncode != 0:
            print(f"Error al reiniciar el servicio: {restart_result.stderr}")

    except Exception as e:
        print(f"Excepción al ejecutar operaciones: {e}")

# Ejecutar las operaciones en un hilo separado para no bloquear la respuesta
Thread(target=pull).start()