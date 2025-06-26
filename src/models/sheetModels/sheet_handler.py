import time
import gspread

class SheetHandler:
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
                    'E:E',    #0 symbol - ticker de mercado
                    'V:V',    #1 tipo_de_activo - cedear, arg o usa
                    'Y:Y',    #2 precioUt - en planilla usa no trae precio
                    'S:S',    #3 trade_en_curso - long, short o nada
                    'T:T',    #4 ut - cantidad a operar
                    'U:U',    #5 senial - Open o Close
                    'Z:Z',    #6 gan_tot
                    'AD:AD',  #7 dias_operado - Dias habiles operado
                    'R:R'     #8 factorUt - negativo o positivo o 0
                ]

                for _ in range(3):  # Intentar hasta 3 veces
                    try:
                        data = sheet.batch_get(ranges)
                        if data:
                            # Procesar cada columna de datos
                            symbol = [str(item[0]).strip("['").strip("']") for item in data[0][1:]] if len(data) > 0 and len(data[0]) > 1 else []
                            tipo_de_activo = [str(item).strip("['").strip("']") for item in data[1][1:]] if len(data) > 1 and len(data[1]) > 1 else []
                            precioUt = [str(item).strip("['").strip("']") for item in data[2][1:]] if len(data) > 2 and len(data[2]) > 1 else []
                            trade_en_curso = [str(item).strip("['").strip("']") for item in data[3][1:]] if len(data) > 3 and len(data[3]) > 1 else []
                            ut = [str(item).strip("['").strip("']") for item in data[4][1:]] if len(data) > 4 and len(data[4]) > 1 else []
                            senial = [str(item).strip("['").strip("']") for item in data[5][1:]] if len(data) > 5 and len(data[5]) > 1 else []
                            gan_tot = [str(item).strip("['").strip("']") for item in data[6][1:]] if len(data) > 6 and len(data[6]) > 1 else []
                            dias_operado = [str(item).strip("['").strip("']") for item in data[7][1:]] if len(data) > 7 and len(data[7]) > 1 else []
                            factorUt = [str(item).strip("['").strip("']") for item in data[8][1:]] if len(data) > 8 and len(data[8]) > 1 else []

                            # Eliminar los encabezados si están presentes
                            symbol = symbol[1:] if len(symbol) > 1 else []
                            tipo_de_activo = tipo_de_activo[1:] if len(tipo_de_activo) > 1 else []
                            precioUt = precioUt[1:] if len(precioUt) > 1 else []
                            trade_en_curso = trade_en_curso[1:] if len(trade_en_curso) > 1 else []
                            ut = ut[1:] if len(ut) > 1 else []
                            senial = senial[1:] if len(senial) > 1 else []
                            gan_tot = gan_tot[1:] if len(gan_tot) > 1 else []
                            dias_operado = dias_operado[1:] if len(dias_operado) > 1 else []
                            factorUt = factorUt[1:] if len(factorUt) > 1 else []

                            # Combinar columnas en un solo resultado
                            union = zip(
                                symbol, tipo_de_activo, trade_en_curso, ut, 
                                senial, gan_tot, dias_operado, precioUt, factorUt
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
