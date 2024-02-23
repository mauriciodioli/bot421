from celery import Celery
from celery.schedules import crontab

from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify



tasks = Blueprint('tasks', __name__)

# Configurar Celery con el mismo nombre de aplicación que en tasks.py
celery_app = Celery('tareas', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')


# Definir la tarea Celery para tarea_programada
@celery_app.task
def tarea_programada():
    print("La tarea programada se ejecutó en task000000000000000000.")

# Definir la tarea Celery para otra_tarea
@celery_app.task
def otra_tarea():
    print("¡Esta es otra tarea!")

# Configurar la programación periódica de la tarea tarea_programada usando Celery Beat
celery_app.conf.beat_schedule = {
    'tarea-ejecucion-diaria': {
        'task': 'tasks.tarea_programada',
        'schedule': crontab(hour=10, minute=30),  # Ejecutar todos los días a las 10:30 a.m.
    },
}

# Configurar la programación periódica de la tarea otra_tarea usando Celery Beat
celery_app.conf.beat_schedule['otra-tarea-ejecucion-diaria'] = {
    'task': 'tasks.otra_tarea',
    'schedule': crontab(hour=11, minute=30),  # Ejecutar todos los días a las 11:30 a.m.
}
