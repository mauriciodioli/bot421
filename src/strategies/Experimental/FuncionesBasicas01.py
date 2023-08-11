# calculo del mep AL30 con websoket
def MepAl30WS(message):
     
     
  #  resultado = instrument_by_symbol_para_CalculoMep(message)    
  #  resultado2 = instrument_by_symbol_para_CalculoMep(message) 
    
    
    #if isinstance(message["marketData"]["OF"][0]["price"],float):
    #precio = message["marketData"]["OF"][0]["price"]
    #if isinstance(message["marketData"]["OF"][0]["size"],int):
    #Liquidez_ahora_cedear = message["marketData"]["OF"][0]["size"]


    #if len( message['marketData']['OF']) == 0:
    if not isinstance(message["marketData"]["OF"][0]["size"],int):# entra si el offer esta vacio
        # entra si el offer esta vacio
        print(" FUN calcularMepAl30WS: La clave 'OF' está vacía.")
    else:

        al30_ci = message['marketData']['OF'][0]['price'] #vendedora OF
        al30D_ci =message['marketData']['BI'][0]['price'] #compradora BI
        #print("__________al30_ci____________",al30_ci)
        #print("__________al30D_ci____________",al30D_ci)
        
        # simulo compra de bono      
        #print("____simulo compra de bono ")  
        # al30ci_unitaria = al30_ci/100
        #cantidad_al30ci=int(10000/al30ci_unitaria)
        #print("__________cantidad_al30ci_________",cantidad_al30ci)
        
        # ahora simulo la venta de los bonos D
        #print("ahora simulo la venta de los bonos D")
        #al30D_ci_unitaria = al30D_ci/100
        #dolaresmep = al30D_ci_unitaria * cantidad_al30ci
        #mep = 10000 / dolaresmep
    mep = 380
    #print(" FUN calcularMepAl30WS: .")
    return mep
