<<<<<<< HEAD
import ast
import os

def analizar_funciones(file_path):
    with open(file_path, 'r') as file:
        source_code = file.read()

    # Parsear el código fuente
    tree = ast.parse(source_code)

    # Recorrer el AST para encontrar funciones y extraer información
    funciones_info = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Información básica de la función
            funcion_info = {
                'nombre': node.name,
                'args': [arg.arg for arg in node.args.args],
                'docstring': ast.get_docstring(node),
                'linea_inicio': node.lineno,
            }
            funciones_info.append(funcion_info)
    
    return funciones_info

def mostrar_informacion_funciones(funciones_info):
    for info in funciones_info:
        print(f"Función: {info['nombre']}")
        print(f"  - Argumentos: {', '.join(info['args'])}")
        print(f"  - Docstring: {info['docstring']}")
        print(f"  - Línea de inicio: {info['linea_inicio']}")
        print()

if __name__ == "__main__":
    # Construir la ruta al archivo operacionEstrategia.py
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'panelControlBroker', 'panelControl.py'))

    # Analizar el archivo para obtener información de las funciones
    funciones_info = analizar_funciones(file_path)

    # Mostrar la información de las funciones
    mostrar_informacion_funciones(funciones_info)
=======
import ast
import os

def analizar_funciones(file_path):
    with open(file_path, 'r') as file:
        source_code = file.read()

    # Parsear el código fuente
    tree = ast.parse(source_code)

    # Recorrer el AST para encontrar funciones y extraer información
    funciones_info = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Información básica de la función
            funcion_info = {
                'nombre': node.name,
                'args': [arg.arg for arg in node.args.args],
                'docstring': ast.get_docstring(node),
                'linea_inicio': node.lineno,
            }
            funciones_info.append(funcion_info)
    
    return funciones_info

def mostrar_informacion_funciones(funciones_info):
    for info in funciones_info:
        print(f"Función: {info['nombre']}")
        print(f"  - Argumentos: {', '.join(info['args'])}")
        print(f"  - Docstring: {info['docstring']}")
        print(f"  - Línea de inicio: {info['linea_inicio']}")
        print()

if __name__ == "__main__":
    # Construir la ruta al archivo operacionEstrategia.py
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'panelControlBroker', 'panelControl.py'))

    # Analizar el archivo para obtener información de las funciones
    funciones_info = analizar_funciones(file_path)

    # Mostrar la información de las funciones
    mostrar_informacion_funciones(funciones_info)
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
