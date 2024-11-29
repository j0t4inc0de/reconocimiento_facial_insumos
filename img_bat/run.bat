@echo off
setlocal enabledelayedexpansion

:: Ruta de la imagen original (cambia esto)
set "imagen=imagen1.png"

:: Carpeta de destino (cambia esto)
set "destino=copias"

:: Crear la carpeta de destino si no existe
if not exist "%destino%" md "%destino%"

:: Bucle para crear las copias
for /L %%i in (1,1,20) do (
    copy "%imagen%" "%destino%\imagen_%%i.png"
)

pause