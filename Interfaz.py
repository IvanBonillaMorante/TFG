import tkinter
from tkinter import *
from tkinter import filedialog
import os
import torch
from ultralytics import YOLO
from PIL import Image
import cv2
from diffusers import StableDiffusionInpaintPipeline
import shutil

#Función que permite el pixelado de la imagen
def pixelado(x, y, img, px_size):
    #Creamos las variables componentes RGB para realizar la media de los tres canales
    componenteR = 0
    componenteB = 0
    componenteG = 0
    #Dentro del bucle recogemos los valores de los 3 canales para cada componente de todos los pixeles del kernel indicado (px_size)
    for i in range(x-(px_size//2), x+(px_size//2)):
        for j in range(y-(px_size//2), y+(px_size//2)):
            if((i >= 0 or j >= 0) and (i < 1080 , j < 720)):
                componenteB += img[j, i][0]
                componenteG += img[j, i][1]
                componenteR += img[j, i][2]

    #Se establece media para asociar ese componente RGB al pixel de la imagen
    media = [componenteB // (px_size*px_size), componenteG // (px_size*px_size), componenteR // (px_size*px_size)]
    return media

#Función que permite la anonimización de las persona detectadas
def anonimizacion(img):
    # Se escoge el modelo de YOLOv8 de segmentación para identificar las personas dentro de la imagen
    model = YOLO("yolov8n-seg.pt")

    # Abrimos la imagen que queremos segmentar
    im1 = Image.open("Imagenes/"+img)

    # Extraemos una dupla con las dimensiones de la imagen original
    #dim = im1.size

    # Redimensionamos la imagen para que psoteriormente pueda ser tratada por la función de difusión estable
    im1 = im1.resize((512, 512))

    # Obtenemos los resultados de la segmentación
    results = model.predict(source=im1, save=False, save_txt=False)

    #obtenemos solo el nombre de la imagen
    cadena = img.split(".")
    name = cadena[0]

    # Por cada resultado (imagen obtenida) vamos a analizar todas las máscaras localizadas en el tensor flow de máscaras
    for resultado in results:
        for mascara in resultado.masks.masks:
            # Aqui se obtiene una de las máscara de la segmentación de los distintos elementos encontrados en la imagen de entrada
            im2 = (mascara.numpy() * 255).astype("uint8")
            im2 = cv2.resize(im2, (512, 512), interpolation=cv2.INTER_AREA)
            # Este bucle for para realizar el pixelado y el sombreado de las personas
            # for y in range(len(im2)):
            # for x in range(len(im2[y])):
            # if(im2[y, x] == 255):
            # im1[y, x] = 0 figuras en negro

            # im1[y, x] = pixelado(x, y, im1, 16) pixelar

            # Guardamos la mascara para luego abrirla con PIL
            cv2.imwrite("mascara.jpg", im2)

            # Creamos el pipe para realizar la sustitución de los objetos identificados por el prompt que le pongamos,
            pipe = StableDiffusionInpaintPipeline.from_pretrained(
                "stabilityai/stable-diffusion-2-inpainting",
                torch_dtype=torch.float32,
            )

            # Abrimos la mascara con PIL
            mask = Image.open("mascara.jpg")

            # Prompt de lo que queremos obtener en la imagen procesada
            prompt = "Robot standing on his feet"

            # Reescalado de la mascara
            #mask = mask.resize((512, 512))

            # Imagen procesada
            imagenProcesada = pipe(prompt=prompt, image=im1, mask_image=mask).images[0]

            # Sustituimos en la imagen original las personas por el prompt
            pixels = im1.load()
            pixelsMask = mask.load()
            pixelsImagenP = imagenProcesada.load()
            for y in range(512):
                for x in range(512):
                    if pixelsMask[x, y] != 0:
                        pixels[x, y] = pixelsImagenP[x, y]
            #Se guarda la imagen con una persona cambiada, esto se hace debido a poder depurar la herramienta debido al tiempo que tarda en generar una imagen totalmente anonimizada
            im1.save("Imagenes procesadas/" + name + " procesada.png")

    # Guardado de la imagen procesada
    im1.save("Imagenes procesadas/" + name + " procesada.png")
    # Devolvemos la imagen
    return im1

#Función para poder seleccionar las fotografias a anonimizar
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
    carpeta_imagenes = os.path.join(carpeta_principal, "Imagenes")
    try:
        for linea in os.listdir(carpeta_imagenes):
            img = anonimizacion(linea)
            img.show()
    except:
        print("Archivo no correcto")
        borrar_archivos(carpeta_imagenes)
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
