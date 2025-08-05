# Webhook Proxy y Automatizador de Despliegue

Este microservicio Flask actúa como un orquestador y reenviador de eventos entre plataformas. Fue desarrollado para facilitar la integración entre bots de mensajería (como WhatsApp Business API) y servicios internos de backend.

## Características principales

- Reenvía solicitudes webhook entrantes (producción o desarrollo) a los endpoints correspondientes.
- Permite ejecución remota de `git pull` + reinicio de servicios a través de `/pull`, útil para despliegue continuo con GitHub.
- Redirecciona endpoints internos como `send_notification`, `all_truck_details` y `activar_gps` al servicio local correspondiente.
- Verificación de tokens seguros para validación de webhooks entrantes.

## 📁 Estructura de archivos

```
app.py             # Lógica principal y rutas
Config.py          # Manejo de variables de entorno
Utils.py           # Lógica de despliegue remoto
requirements.txt   # Dependencias del proyecto
```

## ⚙️ Requisitos

- Python 3.8+
- Flask
- requests
- dotenv

**Instalación de dependencias:**
```bash
pip install -r requirements.txt
```

## Endpoints disponibles

| Ruta                 | Método    | Descripción                                           |
|----------------------|-----------|-------------------------------------------------------|
| `/webhook`           | GET/POST  | Verificación y reenvío de eventos webhook             |
| `/pull`              | POST      | Ejecuta git pull y reinicia servicio basado en la rama|
| `/send_notification` | POST      | Redirige notificaciones a servicio interno            |
| `/all_truck_details` | GET       | Redirige consulta de detalles de camiones             |
| `/activar_gps`       | POST      | Redirige activación de GPS al servicio backend        |
