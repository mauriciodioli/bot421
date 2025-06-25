from app import app
from utils.db import db
import schedule
import time

with app.app_context():
 db.create_all()


   