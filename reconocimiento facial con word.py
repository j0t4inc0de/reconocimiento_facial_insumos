import cv2
import face_recognition
import os
from datetime import datetime, timedelta
import numpy as np
from colorama import Fore
import pyttsx3
from pyzbar.pyzbar import decode

directorioDeAlumnos = "Dataset"
archivoDeRegistro = "registro_alumnos.txt"

alumnosRegistrados = set()
codigosDeBarrasRegistrados = set()
intervaloEntreRegistros = timedelta(minutes=5)
horaDelUltimoRegistro = None
codificacionesDeAlumnos = {}

sintetizadorDeVoz = pyttsx3.init()

def reproducirTexto(texto):
    sintetizadorDeVoz.say(texto)
    sintetizadorDeVoz.runAndWait()

def registrarAlumno(nombre):
    global horaDelUltimoRegistro
    horaActual = datetime.now()
    horaDelUltimoRegistro = horaActual
    registro = f"{horaActual.strftime('%Y-%m-%d  %H:%M:%S')} - {nombre}\n"
    reproducirTexto(f"{nombre} fue registrado")
    print(Fore.BLUE + "Nombre:", nombre)
    print(Fore.MAGENTA + "Fecha:", horaActual.strftime('%Y-%m-%d  %H:%M:%S'))
    with open(archivoDeRegistro, "a") as file:
        file.write(registro)
    return f"{nombre} fue registrado"

def cargarImagenesDeAlumnos():
    for nombreAlumno in os.listdir(directorioDeAlumnos):
        alumnoDir = os.path.join(directorioDeAlumnos, nombreAlumno)
        if os.path.isdir(alumnoDir):
            codificacionesAlumno = []
            for imagenFile in os.listdir(alumnoDir):
                imagenPath = os.path.join(alumnoDir, imagenFile)
                if imagenPath.lower().endswith(('.jpg', '.jpeg', '.png')):
                    imagen = cv2.imread(imagenPath)
                    imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
                    codificaciones = face_recognition.face_encodings(imagen)
                    if len(codificaciones) > 0:
                        codificacion = codificaciones[0]
                        codificacionesAlumno.append(codificacion)
            if len(codificacionesAlumno) > 0:
                codificacionPromedio = np.array(codificacionesAlumno).mean(axis=0)
                codificacionesDeAlumnos[nombreAlumno] = codificacionPromedio

def iniciarReconocimiento():
    cargarImagenesDeAlumnos()
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)

        # Decodificar los códigos de barras en el frame
        codigosDeBarras = decode(frame)

        for codigoDeBarra in codigosDeBarras:
            (x, y, w, h) = codigoDeBarra.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            datosCodigoDeBarra = codigoDeBarra.data.decode('utf-8')
            tipoCodigoDeBarra = codigoDeBarra.type

            texto = f'{tipoCodigoDeBarra}: {datosCodigoDeBarra}'
            cv2.putText(frame, texto, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            if datosCodigoDeBarra not in codigosDeBarrasRegistrados:
                print(f'Detectado {tipoCodigoDeBarra}: {datosCodigoDeBarra}')
                codigosDeBarrasRegistrados.add(datosCodigoDeBarra)

                # Registrar el código de barras en el archivo
                with open(archivoDeRegistro, "a") as file:
                    file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Código de barras: {datosCodigoDeBarra}\n")

        ubicacionesRostros = face_recognition.face_locations(frame)
        codificacionesRostros = face_recognition.face_encodings(frame, ubicacionesRostros)

        for (top, right, bottom, left), codificacionRostro in zip(ubicacionesRostros, codificacionesRostros):
            nombre = "Persona Desconocida"

            for nombreAlumno, codificacionRef in codificacionesDeAlumnos.items():
                coincidencia = face_recognition.compare_faces([codificacionRef], codificacionRostro)[0]
                if coincidencia:
                    nombre = nombreAlumno
                    if nombre not in alumnosRegistrados:
                        mensajeRegistro = registrarAlumno(nombre)
                        alumnosRegistrados.add(nombre)
                    break

            grosorLinea = 4

            # Dibujo alrededor del rostro
            cv2.line(frame, (left, top), (left + 20, top), (204, 204, 51), grosorLinea)
            cv2.line(frame, (left, top), (left, top + 20), (204, 204, 51), grosorLinea)
            cv2.line(frame, (right, top), (right - 20, top), (204, 204, 51), grosorLinea)
            cv2.line(frame, (right, top), (right, top + 20), (204, 204, 51), grosorLinea)
            cv2.line(frame, (left, bottom), (left + 60, bottom), (204, 204, 51), grosorLinea)
            cv2.line(frame, (left, bottom), (left, bottom - 20), (204, 204, 51), grosorLinea)
            cv2.line(frame, (right, bottom), (right - 20, bottom), (204, 204, 51), grosorLinea)
            cv2.line(frame, (right, bottom), (right, bottom - 20), (204, 204, 51), grosorLinea)

            fuente = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, nombre, (left + 6, bottom - 6), fuente, 0.5,
                        (255, 191, 0), 1)

            mensajeRegistro = f"{nombre} registrado" if nombre in alumnosRegistrados else "Esperando registro"
            cv2.putText(frame,mensajeRegistro,(10 ,30 ),fuente ,0.5,(0 ,255 ,0 ),1)

            totalRegistros = len(alumnosRegistrados)
            ultimoRegistroTexto = f"Último registro: {horaDelUltimoRegistro.strftime('%Y-%m-%d %H:%M:%S')}" if horaDelUltimoRegistro else "Sin registros"
            cv2.putText(frame,f"Total registrados: {totalRegistros}",(10 ,60 ),fuente ,0.5,(0 ,255 ,0 ),1)
            cv2.putText(frame ,ultimoRegistroTexto,(10 ,90 ),fuente ,0.5,(0 ,255 ,0 ),1)

        cv2.imshow("Reconocimiento Facial y Escaneo de Codigos de Barras", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    sintetizadorDeVoz.stop()

if __name__ == '__main__':
    iniciarReconocimiento()