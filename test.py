from datetime import datetime
import time
import random


id_historial = 0

def generador_id (id_historial):
    print("El ID actual es: ", id_historial)
    id_historial += 1
    print(id_historial)

generador_id(id_historial)