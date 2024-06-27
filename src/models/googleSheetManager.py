from flask_marshmallow import Marshmallow
from flask import Blueprint, current_app
from utils.db import db
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

ma = Marshmallow()
google_sheet_manager_bp = Blueprint('googleSheetManager', __name__)

class GoogleSheetManager:
    def __init__(self, sheetId, sheet_name):
        self.sheet = self.autenticar_y_abrir_sheet(sheetId, sheet_name)

    def autenticar_y_abrir_sheet(self, sheetId, sheet_name):
        try:
            scope = ['https://spreadsheets.google.com/feeds', 
                     'https://www.googleapis.com/auth/drive']
            newPath = os.path.join(current_app.config['BASE_DIR'], 'strategies/pruebasheetpython.json')
            creds = ServiceAccountCredentials.from_json_keyfile_name(newPath, scope)
            client = gspread.authorize(creds)
            sheet = client.open_by_key(sheetId).worksheet(sheet_name)
            return sheet
        except Exception as e:
            print(f"Error al autenticar y abrir la hoja de cálculo: {e}")
            return None

    def cargar_datos(self, datos, rango):
        if self.sheet:
            try:
                self.sheet.update(rango, datos)
                print("Datos cargados exitosamente.")
            except Exception as e:
                print(f"Error al cargar datos en la hoja de cálculo: {e}")
        else:
            print("No se puede cargar datos porque la hoja no está abierta.")
