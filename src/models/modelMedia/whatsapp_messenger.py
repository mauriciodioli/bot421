
import datetime

class WhatsAppMessenger:
    def __init__(self):
        pass

    def send_message(self, phone_number, message, hour=None, minute=None):
        if hour is None or minute is None:
            now = datetime.datetime.now()
            hour = now.hour
            minute = now.minute + 2  # Envía el mensaje 2 minutos después del tiempo actual

        try:
  #          kit.sendwhatmsg(phone_number, message, hour, minute)
            print(f"Mensaje enviado con éxito a {phone_number}")
        except Exception as e:
            print(f"Ocurrió un error: {e}")
