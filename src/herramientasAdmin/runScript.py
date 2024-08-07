from flask import Blueprint, redirect, url_for,render_template,current_app
import subprocess
import os
runScript = Blueprint('runScript',__name__)

@runScript.route('/run-script', methods=['POST'])
def run_script():
    try:
        app = current_app._get_current_object()
        # Variables de entorno o configuración para la clave privada y la IP
        private_key_path = os.getenv('SSH_PRIVATE_KEY_PATH', 'bot421dbversion2.pem')
        remote_user = 'ubuntu'
        remote_host = 'ip-172-31-19-138'
        app.logger.info("_______________FUNC_ run_script_____________0000000000")
        # Comando SSH
        ssh_command = [
            'ssh', '-i', private_key_path, f'{remote_user}@{remote_host}', 'bash -s'
        ]
        
        # Script a ejecutar en el host remoto
        script = """
        /home/ubuntu/reiniciar_contenedor.sh
        """
        
        # Ejecutar el comando SSH
        result = subprocess.run(ssh_command, input=script, text=True, capture_output=True)
        app.logger.info("_______________FUNC_ run_script_____________11111111111")
        # Imprimir resultados para depuración (considera usar logging en lugar de print en producción)
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        
        # Verifica si el comando fue exitoso
        if result.returncode != 0:
            raise Exception(f"El comando SSH falló con el código de retorno {result.returncode}")
    
    except Exception as e:
        # Manejo de errores (podrías usar logging aquí también)
        print(f"Error ejecutando el script: {e}")
    
    # Redirigir a la página principal
    return  render_template("index.html")

