from flask import Blueprint, redirect, url_for, render_template, current_app
import subprocess
import os

runScript = Blueprint('runScript', __name__)

@runScript.route('/run-script')
def run_script():
    try:
        # Obtener el objeto de la aplicación actual
        app = current_app._get_current_object()

        # Variables de entorno o configuración para la clave privada y la IP
        private_key_path = os.getenv('SSH_PRIVATE_KEY_PATH', 'bot421dbversion2.pem')
        remote_user = 'ubuntu'
        ###remote_host = '18.207.114.83' #PRUEBA
        remote_host = '44.223.20.210' #PRODUCCION
        #remote_host = 'ip-172-31-19-138'
        
        # Registro de eventos
        app.logger.info("Inicio de la ejecución del script.")
        # Comando SSH
        ssh_command = [
                'ssh', '-o', 'StrictHostKeyChecking=no', '-i', private_key_path, f'{remote_user}@{remote_host}', 'bash -s'
            ]
        
        # Script a ejecutar en el host remoto
        script = """
        /home/ubuntu/reiniciar_contenedor.sh
        """
        
        # Ejecutar el comando SSH
        result = subprocess.run(ssh_command, input=script, text=True, capture_output=True)

        # Registro de resultados
        app.logger.info("Ejecución del script exitosa.")  
        # Verifica si el comando fue exitoso
        if result.returncode != 0:
            raise Exception(f"El comando SSH falló con el código de retorno {result.returncode}")
    
    except Exception as e:
        # Manejo de errores
        app.logger.error("Error ejecutando el script: %s", e)
    
    # Redirigir a la página principal
    return render_template('index.html')


