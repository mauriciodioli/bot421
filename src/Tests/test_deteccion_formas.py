import numpy as np
from flask import Blueprint, current_app,make_response, Flask, request, jsonify, send_file
import cv2
from io import BytesIO
import base64
from PIL import Image
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './uploads'
PROCESSED_FOLDER = './processed'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER


# Inicializar el blueprint
test_deteccion_formas = Blueprint('test_deteccion_formas', __name__)



def traer_imagenes():
    # Obtener la ruta completa de la carpeta 'static/uploads'
    uploads_folder = os.path.join(current_app.root_path, 'static', 'uploads')

    # Obtener todas las imágenes en la carpeta 'static/uploads'
    image_files = [file for file in os.listdir(uploads_folder) if file.endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    # Crear las rutas completas de las imágenes sin codificación de caracteres
    image_paths = [os.path.join('uploads', filename).replace(os.sep, '/') for filename in image_files]
    
    return image_paths  # Cambiar a 'image_paths' para devolver las rutas completas

@test_deteccion_formas.route('/comparar-metodos')
def comparar_metodos():
    # Obtener las rutas de las imágenes
    image_paths = traer_imagenes()

    # Procesar cada imagen
    resultados = []
    for image_path in image_paths:
        # Abrir la imagen
        
        imagen = Image.open(os.path.join(current_app.root_path, 'static', image_path))
        imagen_np = np.array(imagen)
  # Definir la ruta de salida para la imagen procesada
        output_path = os.path.join(current_app.root_path, 'static', 'uploads', 'processed', os.path.basename(image_path))

        # Preprocesar la imagen y guardar la imagen procesada
        imagen_procesada1 = preprocesar_imagen(imagen_np, output_path)  # Para la red neuronal

       
        imagen_procesada2 = convertirGrises(imagen_np)     # Para el método de Sobel y Umbral
        
        # Método 1: Red Neuronal
        caracteristicas1 = analizar_forma(imagen_procesada1)
        if caracteristicas1 is None:
            resultado_red_neuronal = "No se encontró forma"
        else:
            prediccion = red_neuronal.predecir(caracteristicas1)
            forma = np.argmax(prediccion)
            
            # Imprimir el resultado
            print("La forma con la mayor probabilidad es:", forma)
            etiquetas = ["Circulo","Cuadrado","Triangulo"]
            resultado_red_neuronal = etiquetas[forma]
        
        # Método 2: Sobel y Umbral
        imagen_suavizada = aplicarFiltroGaussiano(imagen_procesada2)
        imagen_normalizada = normalizarImagen(imagen_suavizada)
        bordes = aplicarOperadorSobel(imagen_normalizada)
        umbral = establecerUmbral(bordes)
        regiones = aplicarSegmentacionThresholding(bordes, umbral)
        caracteristicas2 = calcularCaracteristicasForma(regiones)
        resultado_sobel = clasificarFormas(caracteristicas2)
        
        # Comparación de resultados
        if resultado_red_neuronal == resultado_sobel:
            mejor_resultado = resultado_red_neuronal
        else:
            mejor_resultado = "Resultados diferentes: NN -> {}, Sobel -> {}".format(
                resultado_red_neuronal, resultado_sobel
            )

        # Agregar el resultado al listado
        resultados.append({
            'path': image_path,
            'resultado_red_neuronal': resultado_red_neuronal,
            'resultado_sobel': resultado_sobel,
            'mejor_resultado': mejor_resultado
        })

    # Retornar todos los resultados procesados
    return jsonify(resultados)



# Red Neuronal Definida
class RedNeuronal:
    def __init__(self, learning_rate=0.1):
        self.learning_rate = learning_rate
        self.pesos1 = np.random.rand(5, 5)  # Ajuste de tamaño según características
        self.pesos2 = np.random.rand(5, 3)

    def entrenar(self, entradas, salidas):
        for i in range(len(entradas)):
            salida_oculta = self.sigmoid(np.dot(entradas[i], self.pesos1))
            salida = self.sigmoid(np.dot(salida_oculta, self.pesos2))
            error = salidas[i] - salida
            delta_salida = error * salida * (1 - salida)
            delta_oculta = delta_salida @ self.pesos2.T * salida_oculta * (1 - salida_oculta)
            self.pesos2 += self.learning_rate * np.outer(salida_oculta, delta_salida)
            self.pesos1 += self.learning_rate * np.outer(entradas[i], delta_oculta)

    def predecir(self, entrada):
        salida_oculta = self.sigmoid(np.dot(entrada, self.pesos1))
        return self.sigmoid(np.dot(salida_oculta, self.pesos2))

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

# Inicializamos la red neuronal y entrenamos con datos de ejemplo
red_neuronal = RedNeuronal()
entradas = np.array([
    [5, 5, 5, 15, 10.825],
    [4, 4, 6, 14, 9.237],
    [5, 78.5, 0, 0, 0],
    [10, 314.0, 0, 0, 0],
    [5, 100.0, 0, 0, 0],
    [10, 400.0, 0, 0, 0]
])
salidas = np.array([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1],
    [0, 0, 1],
    [0, 0, 1],
    [0, 0, 1]
])
red_neuronal.entrenar(entradas, salidas)

# Función para preprocesar la imagen
def preprocesar_imagen(imagen, output_path=None): 
    # Convertir a escala de grises
    imagen_grises = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

      # Convertir a blanco y negro usando un umbral sin inversión
    _, imagen_bn = cv2.threshold(imagen_grises, 127, 255, cv2.THRESH_BINARY)  # Usa THRESH_BINARY para no invertir los colores

    # Aplicar el desenfoque gaussiano
    imagen = cv2.GaussianBlur(imagen_bn, (5, 5), 0)

    
    # Guardar la imagen procesada en formato PNG si se proporciona un output_path
    if output_path is not None:
       # Convertir la imagen de nuevo a formato PIL
        imagen_procesada = Image.fromarray(imagen)

        # Definir el nuevo path para guardar la imagen procesada
        new_path = os.path.join(current_app.root_path, 'static', 'uploads', output_path)
        
        # Guardar la imagen procesada en formato PNG
        imagen_procesada.save(new_path)  # Aquí se utiliza el método save de PIL

    
    return imagen


# Función para analizar la forma y extraer características
def analizar_forma(imagen):
    """
    Analiza la forma en la imagen y extrae características.

    Args:
        imagen (numpy array): Imagen en escala de grises.

    Returns:
        list: Características de la forma, si se encuentra una.
              [perímetro, área, ...]
        None: Si no se encuentra una forma.
    """
    # Umbralizar la imagen para obtener bordes
    _, bordes = cv2.threshold(imagen, 128, 255, cv2.THRESH_BINARY)

    # Encontrar contornos en la imagen, capturando contornos interiores y exteriores
    contornos, _ = cv2.findContours(bordes, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Si no se encuentran contornos, retornar None
    if not contornos:
        return None

    # Seleccionar el contorno más grande
    contorno = max(contornos, key=cv2.contourArea)

    # Calcular características del contorno
    area = cv2.contourArea(contorno)
    perimetro = cv2.arcLength(contorno, True)

    # Características: [perímetro, área]
    return [perimetro, area, 0, 0, 0]  # Ejemplo para demo


@test_deteccion_formas.route('/procesar-imagen', methods=['POST'])
def procesar_imagen():
    data = request.json['imagen']
    imagen_str = data.split(',')[1]
    imagen = Image.open(BytesIO(base64.b64decode(imagen_str)))
    imagen_np = np.array(imagen)

    # Preprocesamos la imagen
    imagen_procesada = preprocesar_imagen(imagen_np)

    # Extraemos las características de la forma
    caracteristicas = analizar_forma(imagen_procesada)

    if caracteristicas is None:
        return jsonify({"resultado": "No se encontró forma"})

    # Clasificamos usando la red neuronal
    prediccion = red_neuronal.predecir(caracteristicas)

    # Determinamos la forma
    forma = np.argmax(prediccion)
    etiquetas = ["Triángulo", "Círculo", "Cuadrado"]
    resultado = etiquetas[forma]

    return jsonify({"resultado": resultado})



# Preprocesamiento
def cargarImagen(image_path):
    return cv2.imread(image_path)

def convertirGrises(imagen):
    return cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

def aplicarFiltroGaussiano(imagenGrises):
    return cv2.GaussianBlur(imagenGrises, (5, 5), 0)

def normalizarImagen(imagen):
    return cv2.normalize(imagen, None, 0, 255, cv2.NORM_MINMAX)

# Detección de bordes
def aplicarOperadorSobel(imagenNormalizada):
    sobelx = cv2.Sobel(imagenNormalizada, cv2.CV_64F, 1, 0, ksize=5)
    sobely = cv2.Sobel(imagenNormalizada, cv2.CV_64F, 0, 1, ksize=5)
    return cv2.magnitude(sobelx, sobely)

def establecerUmbral(bordes):    
    umbral = 100  # Valor fijo
    return umbral  # Devuelve el valor del umbral

    #_, umbral = cv2.threshold(bordes, 100, 255, cv2.THRESH_BINARY)
    return umbral

# Segmentación
def aplicarSegmentacionThresholding(bordes, umbral):
    _, regiones = cv2.threshold(bordes, 
                                umbral, 
                                255, 
                                cv2.THRESH_BINARY)
    return regiones

# Análisis de forma
def calcularCaracteristicasForma(regiones):
    # Calcular momentos de Hu como ejemplo de características
    momentos = cv2.moments(regiones)
    huMoments = cv2.HuMoments(momentos).flatten()
    return huMoments

# Clasificación
def clasificarFormas(caracteristicas): 
    area = caracteristicas[1]  # Supongamos que el área es la segunda característica
    print("Área detectada:", area)  # Imprime el área para depuración
    if area > 500:  # Un umbral de área arbitrario para determinar forma
        return "Cuadrado"
    elif area < 200:
        return "  Circulo" 
    else:
        return "Triángulo"


# Postprocesamiento
def refinarResultados(etiquetas):
    # Aquí se podrían aplicar más filtros o técnicas de refinamiento
    return etiquetas



