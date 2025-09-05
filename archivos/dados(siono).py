import random

while True:
    resultado = random.randint(0,1)
    
    if resultado == 0:
    	print("El dado giro y obtuvo:  No  ", resultado)
    else:
    	print("El dado giro y obtuvo: Si", resultado)
    input("Presiona cualquier tecla para lanzar nuevamente.")