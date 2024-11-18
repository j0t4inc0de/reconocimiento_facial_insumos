import cv2
import face_recognition
import os
from datetime import datetime, timedelta # type: ignore
import numpy as np
from colorama import Fore
import pyttsx3
from pyzbar.pyzbar import decode

class SistemaDeRegistro:
    def __init__(self, directorio_alumnos="Dataset", archivo_registro="registro_alumnos.txt"):
        self.directorio_alumnos = directorio_alumnos
        self.archivo_registro = archivo_registro
        self.alumnos_registrados = set()
        self.codigos_barras_registrados = set()
        self.intervalo_registro = timedelta(minutes=5)
        self.hora_ultimo_registro = None
        self.codificaciones_alumnos = {}
        self.sintetizador_voz = pyttsx3.init()
        self.tiempos_ultimo_registro = {}  # Diccionario para controlar el tiempo de registro por alumno
        self.cargar_imagenes_alumnos()

    def reproducir_texto(self, texto):
        self.sintetizador_voz.say(texto)
        self.sintetizador_voz.runAndWait()

    def registrar_alumno(self, nombre):
        self.hora_ultimo_registro = datetime.now() # type: ignore
        registro = f"{self.hora_ultimo_registro.strftime('%Y-%m-%d %H:%M:%S')} - {nombre}\n"
        self.reproducir_texto(f"{nombre} fue registrado")
        print(Fore.BLUE + "Nombre:", nombre)
        print(Fore.MAGENTA + "Fecha:", self.hora_ultimo_registro.strftime('%Y-%m-%d %H:%M:%S'))
        
        with open(self.archivo_registro, "a") as file:
            file.write(registro)
        
        self.alumnos_registrados.add(nombre)
        self.tiempos_ultimo_registro[nombre] = self.hora_ultimo_registro  # Actualizar el tiempo de registro
        return f"{nombre} fue registrado"

    def cargar_imagenes_alumnos(self):
        for nombre_alumno in os.listdir(self.directorio_alumnos):
            alumno_dir = os.path.join(self.directorio_alumnos, nombre_alumno)
            if os.path.isdir(alumno_dir):
                codificaciones = []
                for imagen_file in os.listdir(alumno_dir):
                    imagen_path = os.path.join(alumno_dir, imagen_file)
                    if imagen_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                        imagen = cv2.imread(imagen_path)
                        imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
                        codificacion = face_recognition.face_encodings(imagen)
                        if codificacion:
                            codificaciones.append(codificacion[0])
                
                if codificaciones:
                    self.codificaciones_alumnos[nombre_alumno] = np.array(codificaciones).mean(axis=0)

    def procesar_codigos_barras(self, frame):
        codigos_barras = decode(frame)
        for codigo in codigos_barras:
            (x, y, w, h) = codigo.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            datos = codigo.data.decode('utf-8')
            tipo = codigo.type
            texto = f'{tipo}: {datos}'
            cv2.putText(frame, texto, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            if datos not in self.codigos_barras_registrados:
                print(f'Detectado {tipo}: {datos}')
                self.codigos_barras_registrados.add(datos)
                with open(self.archivo_registro, "a") as file:
                    file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Código de barras: {datos}\n") # type: ignore

    def procesar_reconocimiento_facial(self, frame):
        # Definir la región de interés (ROI) como una porción central del cuadro
        alto, ancho, _ = frame.shape
        margen_alto = int(alto * 0.25)  # 25% superior e inferior se excluyen
        margen_ancho = int(ancho * 0.25)  # 25% izquierdo y derecho se excluyen
        
        # Extraer ROI y convertir a RGB
        frame_roi = frame[margen_alto:alto - margen_alto, margen_ancho:ancho - margen_ancho]
        frame_roi_rgb = cv2.cvtColor(frame_roi, cv2.COLOR_BGR2RGB)

        # Detectar caras y obtener codificaciones en la ROI
        ubicaciones = face_recognition.face_locations(frame_roi_rgb)
        codificaciones = face_recognition.face_encodings(frame_roi_rgb, ubicaciones)

        # Ajustar las ubicaciones para que correspondan al cuadro completo
        ubicaciones_ajustadas = [
            (top + margen_alto, right + margen_ancho, bottom + margen_alto, left + margen_ancho)
            for top, right, bottom, left in ubicaciones
        ]

        for (top, right, bottom, left), codificacion in zip(ubicaciones_ajustadas, codificaciones):
            nombre = "Persona Desconocida"
            for nombre_alumno, codificacion_ref in self.codificaciones_alumnos.items():
                if face_recognition.compare_faces([codificacion_ref], codificacion)[0]:
                    nombre = nombre_alumno
                    # Comprobar si el registro es reciente
                    tiempo_actual = datetime.now()  # type: ignore
                    if (nombre not in self.tiempos_ultimo_registro or 
                        tiempo_actual - self.tiempos_ultimo_registro[nombre] > self.intervalo_registro):
                        self.registrar_alumno(nombre)
                    else:
                        print(f"{nombre} fue detectado, pero no se registrará nuevamente todavía.")
                    break
            
            # Dibujar rectángulo y mostrar el nombre en el cuadro original
            self.dibujar_rectangulo(frame, top, right, bottom, left, nombre)

    def dibujar_rectangulo(self, frame, top, right, bottom, left, nombre):
        grosor_linea = 4
        # Dibuja el marco alrededor de la cara
        cv2.line(frame, (left, top), (left + 20, top), (204, 204, 51), grosor_linea)
        cv2.line(frame, (left, top), (left, top + 20), (204, 204, 51), grosor_linea)
        cv2.line(frame, (right, top), (right - 20, top), (204, 204, 51), grosor_linea)
        cv2.line(frame, (right, top), (right, top + 20), (204, 204, 51), grosor_linea)
        cv2.line(frame, (left, bottom), (left + 60, bottom), (204, 204, 51), grosor_linea)
        cv2.line(frame, (left, bottom), (left, bottom - 20), (204, 204, 51), grosor_linea)
        cv2.line(frame, (right, bottom), (right - 20, bottom), (204, 204, 51), grosor_linea)
        cv2.line(frame, (right, bottom), (right, bottom - 20), (204, 204, 51), grosor_linea)
        
        cv2.putText(frame, nombre, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 191, 0), 1)
        
        mensaje_registro = f"{nombre} registrado" if nombre in self.alumnos_registrados else "Esperando registro"
        total_registros = len(self.alumnos_registrados)
        ultimo_registro_texto = (f"Último registro: {self.hora_ultimo_registro.strftime('%Y-%m-%d %H:%M:%S')}"if self.hora_ultimo_registro else "Sin registros")
        
        cv2.putText(frame, mensaje_registro, (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"Total registrados: {total_registros}", (10, 60), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, ultimo_registro_texto, (10, 90), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1)

    def iniciar_reconocimiento(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            self.procesar_codigos_barras(frame)
            self.procesar_reconocimiento_facial(frame)
            cv2.imshow("Reconocimiento Facial y Escaneo de Codigos de Barras", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        self.sintetizador_voz.stop()

if __name__ == '__main__':
    sistema = SistemaDeRegistro()
    sistema.iniciar_reconocimiento()