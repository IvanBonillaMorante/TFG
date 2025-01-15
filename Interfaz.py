import tkinter
from tkinter import *
from tkinter import filedialog
import os
from Anonimizador import Anonimizador



def seleccionar_archivos():
    carpeta_imagenes = filedialog.askopenfilenames()
    if carpeta_imagenes.len() == 0:
        print("No se ha seleccionado ningún archivo.")

def seleccionar_destino():
    directorio = filedialog.askopenfilenames()
    if os.path.isdir(directorio):
        destino = directorio + "/results"
        carpeta_destino = os.mkdir(destino)
    else:
        print("Directorio no válido.")

#Función para cuando una vez finalizado el programa, o en caso de error se borre el contenido de la carpeta automaticamente
def borrar_archivos(carpeta):
    for archivo in os.listdir(carpeta):
        os.remove(carpeta + "/" + archivo)

#Función para la lectura del fichero Imagenes y posteriormente procesar las fotos y enseñarlas
def leer_archivos():
    try:
        anonimizador = Anonimizador()
        prompt = btn3.get()
        mode = btn4.get()
        anonimizador.anonimizacion(carpeta_imagenes,mode,carpeta_destino,prompt)
    except:
        print("Archivo no correcto")
        exit(1)

os.environ["DISPLAY"] = ":0.0"

#Obtención de los ficheros del proyecto e imagenes
carpeta_imagenes = ""
carpeta_destino = ""
prompt = ""
mode = 3

#Generación de la ventana y sus cualidades
window = Tk()
window.title("Anonimizador de data sets")
window.minsize(width=1080, height=720)

#Botones de la ventana
btn1 = tkinter.Button(window, text="Selecciona las fotos", command=seleccionar_archivos)
btn1.place(x=200, y=500)

btn2 = tkinter.Button(window, text="Anonimizar fotos", command=seleccionar_destino)
btn2.place(x=400, y=500)

btn3 = tkinter.Text(window, width=60, height=20, font=("Helvetic", 16))
btn3.place(x=200, y=600)

btn4 = tkinter.Listbox(window)
btn4.insert(END, "0")
btn4.insert(END, "1")
btn4.insert(END, "2")
btn4.place(x=400, y=600)


btn5 = tkinter.Button(window, text="Anonimizar fotos", command=leer_archivos)
btn2.place(x=300, y=600)

#La ventana no se cierra hasta que se de al boton de cerrar
window.mainloop()

