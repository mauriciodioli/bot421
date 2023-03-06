from flask import Blueprint,render_template

import gspread
from oauth2client.service_account import ServiceAccountCredentials
#import drive
#drive.mount('/content/gdrive')



datoSheet = Blueprint('datoSheet',__name__)



@datoSheet.route('/datosDesdeSheet/')
def datosDesdeSheet():     
 return render_template('/estrategias.html')
    