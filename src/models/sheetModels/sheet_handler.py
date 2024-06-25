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
                    f'{self.sheet_name}!E:E',    # symbol - ticker de mercado
                    f'{self.sheet_name}!V:V',    # tipo_de_activo - cedear, arg o usa
                    f'{self.sheet_name}!Y:Y',    # precioUt - en planilla usa no trae precio
                    f'{self.sheet_name}!S:S',    # trade_en_curso - long, short o nada
                    f'{self.sheet_name}!T:T',    # ut - cantidad a operar
                    f'{self.sheet_name}!U:U',    # senial - Open o Close
                    f'{self.sheet_name}!Z:Z',    # gan_tot
                    f'{self.sheet_name}!AD:AD'   # dias_operado - Dias habiles operado
                ]

                for _ in range(3):  # Intentar hasta 3 veces
                    try:
                        data = sheet.batch_get(ranges)
                        if data:
                            symbol = data[0][0] if len(data) > 0 else []
                            tipo_de_activo = data[1][0] if len(data) > 1 else []
                            precioUt = data[2][0] if len(data) > 2 else []
                            trade_en_curso = data[3][0] if len(data) > 3 else []
                            ut = data[4][0] if len(data) > 4 else []
                            senial = data[5][0] if len(data) > 5 else []
                            gan_tot = data[6][0] if len(data) > 6 else []
                            dias_operado = data[7][0] if len(data) > 7 else []

                            union = zip(symbol, tipo_de_activo, trade_en_curso, ut, senial, gan_tot, dias_operado, precioUt)
                            return list(union)
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
