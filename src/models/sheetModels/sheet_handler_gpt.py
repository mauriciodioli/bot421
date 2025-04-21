import time
import gspread

class Sheet_handler_gpt:
    def __init__(self, sheet_manager, sheetId, sheet_name):
        self.sheet_manager = sheet_manager
        self.sheetId = sheetId
        self.sheet_name = sheet_name

    def leerSheet(self):
        try:
            sheet = self.sheet_manager.abrir_sheet(self.sheetId, self.sheet_name)
            if sheet:
                # Definimos los rangos correctos
                ranges = [
                    'A:A',    #0 numero
                    'B:B',    #1 pais
                    'C:C',    #2 producto
                    'D:D',    #3 amazon
                    'F:F',    #4 ebay
                    'G:G',    #5 aliexpress
                    'DDZ',    #6 fecha                   
                ]

                for _ in range(3):  # Intentar hasta 3 veces
                    try:
                        data = sheet.batch_get(ranges)
                        if data:
                            # Procesar cada columna de datos
                            numero = [str(item[0]).strip("['").strip("']") for item in data[0][1:]] if len(data) > 0 and len(data[0]) > 1 else []
                            pais = [str(item).strip("['").strip("']") for item in data[1][1:]] if len(data) > 1 and len(data[1]) > 1 else []
                            producto = [str(item).strip("['").strip("']") for item in data[2][1:]] if len(data) > 2 and len(data[2]) > 1 else []
                            amazon = [str(item).strip("['").strip("']") for item in data[3][1:]] if len(data) > 3 and len(data[3]) > 1 else []
                            ebay = [str(item).strip("['").strip("']") for item in data[4][1:]] if len(data) > 4 and len(data[4]) > 1 else []
                            aliexpress = [str(item).strip("['").strip("']") for item in data[5][1:]] if len(data) > 5 and len(data[5]) > 1 else []
                            fecha = [str(item).strip("['").strip("']") for item in data[6][1:]] if len(data) > 6 and len(data[6]) > 1 else []
                          
                            # Combinar columnas en un solo resultado
                            union = zip(
                                numero, pais, producto, amazon, ebay, aliexpress, fecha
                            )
                            #for linea in union:
                                #print(linea)
                            return union
                    except gspread.exceptions.APIError as e:
                        print(f"Error al leer la hoja: {e}")
                        if e.response.status_code == 500:
                            time.sleep(2)  # Esperar 2 segundos antes de reintentar
                        else:
                            break
                return None
            else:
                print("No se pudo abrir la hoja")
                return None
        except Exception as e:
            print(f"Error en el proceso de lectura: {e}")
            return None
