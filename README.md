Sistema de Reconocimiento Facial enfocado en la gestión de herramientas y recursos en un entorno institucional. Este sistema permite identificar usuarios mediante reconocimiento facial y registrar las herramientas seleccionadas por cada individuo manteniendo y creando un historial de cada estudiante

Vista estudiante: Al darle iniciar se reconoce su rostro, y crea su pedido de herramientas para que el bodeguero pueda acceder a ella y escanear las herramientas elegidas

Vista bodeguero: Ver todos los pedidos echos por estudiantes, CRUD de herramientas, ESCANEAR herramientas de los PEDIDOS, Añadir estudiantes al RECONOCIMIENTO FACIAL. El escaner cuenta con contraseña


Diagrama de flujo del TOTEM (Estudiante):
![Diagrama de flujo del totem - VISTA ESTUDIANTE](https://github.com/user-attachments/assets/fed36767-ed4b-40ad-b5c2-b4c94c45f410)

VISTA ESTUDIANTE:
![Inicio](https://github.com/user-attachments/assets/af9c6225-f0ff-4a62-bf9d-117067564b3e)
![Deteccion de rostro](https://github.com/user-attachments/assets/7cf9d818-7da9-4e59-8c6d-8c27615795db)
![herramientas](https://github.com/user-attachments/assets/c29073d3-ebdc-40f3-a637-6615d1a42aa5)
![image](https://github.com/user-attachments/assets/a1d8e10c-acea-4692-87a3-294eb18c78be)


VISTA BODEGUERO:
![Inicio Bodeguero](https://github.com/user-attachments/assets/c0299d6d-e761-49d7-b2d1-c5ed556c005a)
![image](https://github.com/user-attachments/assets/20e3ad2e-40d7-49e0-9110-ab9e7e947329)



El archivo Main del proyecto es 'sistema_panol.py'.

Carpetas
/Python310
PATH del python utilizado para el proyecto (3.10.0).
/.venv
Entorno virtual con las librerias necesarias.
/Dataset
Directorio con información de los alumnos ingresados junto a sus caras.
/codigos_de_barra
Codigos de barra de cada insumo/material del pañol.
/dll-pyzbar
Directorio con ejecutables y programas necesarios para el proyecto.
/imagenes
Directorio con las imagenes de prueba para el proyecto, y un .bat para la creación en masa
/img
Directorio con las imagenes de prueba en masa
Mejoras que hemos echo a lo largo del proyecto:
