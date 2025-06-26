<<<<<<< HEAD
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
            if not sheet:
                print("No se pudo abrir la hoja")
                return None

            # Rango exacto con las 13 columnas del prompt extendido
            ranges = [
                'A:A',  # 0 numero
                'B:B',  # 1 pais
                'C:C',  # 2 producto
                'D:D',  # 3 categoria
                'E:E',  # 4 descripcion
                'F:F',  # 5 precio_amazon
                'G:G',  # 6 precio_ebay
                'H:H',  # 7 precio_aliexpress
                'I:I',  # 8 proveedor_mas_barato
                'J:J',  # 9 link_proveedor
                'K:K',  # 10 precio_reventa_sugerido
                'L:L',  # 11 margen_estimado
                'M:M',  # 12 imagen
            ]

            for _ in range(3):  # Intentar hasta 3 veces
                try:
                    data = sheet.batch_get(ranges)
                    if not data:
                        return None

                    # Procesar cada columna con protección
                    columnas = []
                    for i in range(13):
                        col = data[i][1:] if len(data[i]) > 1 else []
                        columnas.append([str(item).strip("['").strip("']") for item in col])

                    # Combinar columnas por fila
                    union = zip(*columnas)
                    return list(union)

                except gspread.exceptions.APIError as e:
                    print(f"Error al leer la hoja: {e}")
                    if e.response.status_code == 500:
                        time.sleep(2)
                    else:
                        break
            return None

        except Exception as e:
            print(f"Error en el proceso de lectura: {e}")
            return None
=======
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
            if not sheet:
                print("No se pudo abrir la hoja")
                return None

            # Rango exacto con las 13 columnas del prompt extendido
            ranges = [
                'A:A',  # 0 numero
                'B:B',  # 1 pais
                'C:C',  # 2 producto
                'D:D',  # 3 categoria
                'E:E',  # 4 descripcion
                'F:F',  # 5 precio_amazon
                'G:G',  # 6 precio_ebay
                'H:H',  # 7 precio_aliexpress
                'I:I',  # 8 proveedor_mas_barato
                'J:J',  # 9 link_proveedor
                'K:K',  # 10 precio_reventa_sugerido
                'L:L',  # 11 margen_estimado
                'M:M',  # 12 imagen
            ]

            for _ in range(3):  # Intentar hasta 3 veces
                try:
                    data = sheet.batch_get(ranges)
                    if not data:
                        return None

                    # Procesar cada columna con protección
                    columnas = []
                    for i in range(13):
                        col = data[i][1:] if len(data[i]) > 1 else []
                        columnas.append([str(item).strip("['").strip("']") for item in col])

                    # Combinar columnas por fila
                    union = zip(*columnas)
                    return list(union)

                except gspread.exceptions.APIError as e:
                    print(f"Error al leer la hoja: {e}")
                    if e.response.status_code == 500:
                        time.sleep(2)
                    else:
                        break
            return None

        except Exception as e:
            print(f"Error en el proceso de lectura: {e}")
            return None
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
