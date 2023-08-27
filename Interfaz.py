import tkinter
from tkinter import *
from tkinter import filedialog
import os
import shutil
import Anonimizador



def seleccionar_archivos():
    filenames = filedialog.askopenfilenames()
    if filenames:
        for filename in filenames:
            cadena = filename.split("/")
            nombre = cadena[len(cadena) - 1]
            #Copia de la imagen en la carpeta imagenes
            shutil.copy(filename, "./Imagenes/" + nombre)
    else:
        print("No se ha seleccionado ningún archivo.")

#Función para cuando una vez finalizado el programa, o en caso de error se borre el contenido de la carpeta automaticamente
def borrar_archivos(carpeta):
    for archivo in os.listdir(carpeta):
        os.remove(carpeta + "/" + archivo)

#Función para la lectura del fichero Imagenes y posteriormente procesar las fotos y enseñarlas
def leer_archivos():
    #Obtención de los ficheros del proyecto e imagenes
    carpeta_principal = os.path.dirname(__file__)
    carpeta_imagenes = carpeta_principal + "/Imagenes"
    carpeta_destino = carpeta_principal + "/Imagenes procesadas"
    try:
        for linea in os.listdir(carpeta_imagenes):
            name = linea.split(".")
            orig = carpeta_imagenes + "/" + linea
            dest = carpeta_destino + "/" + name[0] + " procesada.png"
            img = Anonimizador.anonimizacion(orig, 0, dest, "robot standing on their feet")
            img.show()
    except:
        print("Archivo no correcto")
        #borrar_archivos(carpeta_imagenes)
        exit(1)

#Obtención de los ficheros del proyecto e imagenes
carpeta_principal = os.path.dirname(__file__)
carpeta_imagenes = os.path.join(carpeta_principal, "Imagenes")

#Generación de la ventana y sus cualidades
window = Tk()
window.title("Anonimizador de data sets")
window.minsize(width=1080, height=720)

#Botones de la ventana
btn1 = tkinter.Button(window, text="Selecciona las fotos", command=seleccionar_archivos)
btn1.place(x=200, y=500)

btn2 = tkinter.Button(window, text="Anonimizar fotos", command=leer_archivos)
btn2.place(x=400, y=500)

#La ventana no se cierra hasta que se de al boton de cerrar
window.mainloop()

#Borrado despues de finalizar la herramienta
borrar_archivos(carpeta_imagenes)
