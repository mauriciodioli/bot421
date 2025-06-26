<<<<<<< HEAD
import aiohttp
import asyncio

class TelegramNotifier:
     #https://api.telegram.org/bot7264333617:AAFlrcw9yObB8ksp6k1P--zW6D6uk0gCgqc/getupdates  direccion para conseguir el id del grupo
   
    token = "7264333617:AAFlrcw9yObB8ksp6k1P--zW6D6uk0gCgqc"
    base_url = f"https://api.telegram.org/bot{token}/sendMessage"

    async def enviar_mensaje_async(self, chat_id, ticker, ut1, signal):
        chat_id = chat_id.strip()  # Eliminar espacios en blanco
        message = f"Ticker: {ticker}\nUT1: {ut1}\nSignal: {signal}"
        payload = {'chat_id': chat_id, 'text': message}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.base_url, data=payload) as response:
                    data = await response.json()
                    print(data)
            except Exception as e:
                print(f"Error al enviar mensaje: {e}")
    
    async def enviar_mensaje_grupo(self, chat_id,mensaj):
        chat_id = chat_id.strip()  # Eliminar espacios en blanco
        message = f"{mensaj}"
        payload = {'chat_id': chat_id, 'text': message}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.base_url, data=payload) as response:
                    data = await response.json()
                    print(data)
            except Exception as e:
=======
import aiohttp
import asyncio

class TelegramNotifier:
     #https://api.telegram.org/bot7264333617:AAFlrcw9yObB8ksp6k1P--zW6D6uk0gCgqc/getupdates  direccion para conseguir el id del grupo
   
    token = "7264333617:AAFlrcw9yObB8ksp6k1P--zW6D6uk0gCgqc"
    base_url = f"https://api.telegram.org/bot{token}/sendMessage"

    async def enviar_mensaje_async(self, chat_id, ticker, ut1, signal):
        chat_id = chat_id.strip()  # Eliminar espacios en blanco
        message = f"Ticker: {ticker}\nUT1: {ut1}\nSignal: {signal}"
        payload = {'chat_id': chat_id, 'text': message}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.base_url, data=payload) as response:
                    data = await response.json()
                    print(data)
            except Exception as e:
                print(f"Error al enviar mensaje: {e}")
    
    async def enviar_mensaje_grupo(self, chat_id,mensaj):
        chat_id = chat_id.strip()  # Eliminar espacios en blanco
        message = f"{mensaj}"
        payload = {'chat_id': chat_id, 'text': message}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.base_url, data=payload) as response:
                    data = await response.json()
                    print(data)
            except Exception as e:
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
                print(f"Error al enviar mensaje: {e}")