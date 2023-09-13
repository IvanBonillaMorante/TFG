import cv2
import torch
from PIL import Image
from diffusers import StableDiffusionInpaintPipeline
from ultralytics import YOLO




class Anonimizador:

    # Función que permite el pixelado de la imagen
    @staticmethod
    def pixelado(x, y, img, px_size, img_size):
        # Creamos las variables componentes RGB para realizar la media de los tres canales
        componenteR = 0
        componenteB = 0
        componenteG = 0

        # Dentro del bucle recogemos los valores de los 3 canales para cada componente de todos los pixeles del kernel indicado (px_size)
        for i in range(x - (px_size // 2), x + (px_size // 2)):
            for j in range(y - (px_size // 2), y + (px_size // 2)):
                if ((i >= 0 and j >= 0) and (i < img_size[0] and j < img_size[1])):
                    componenteB += img[i, j][0]
                    componenteG += img[i, j][1]
                    componenteR += img[i, j][2]

        # Se establece media para asociar ese componente RGB al pixel de la imagen
        media = (componenteB // (px_size * px_size), componenteG // (px_size * px_size),
                 componenteR // (px_size * px_size))
        return media

    # Función que permite la anonimización de las persona detectadas, dandole la ruta de origen a la imagen, una ruta de destino y un modo para el tipo de anonimización deseado
    # El argumento prompt es la linea que se usara para sustituir la mascara por lo que se ponga en esa linea
    @staticmethod
    def anonimizacion(imgOrig, mode, imgDest, prompt):
        # Se escoge el modelo de YOLOv8 de segmentación para identificar las personas dentro de la imagen
        model = YOLO("yolov8n-seg.pt")

        # Abrimos la imagen que queremos segmentar
        im1 = Image.open(imgOrig)

        # Redimensionamos la imagen para que psoteriormente pueda ser tratada por la función de difusión estable
        im1 = im1.resize((512, 512))

        # Obtenemos los resultados de la segmentación indicando la imagen, si se guarda la imagen, y classes indica que clases detectar
        results = model.predict(source=im1, save=False, save_txt=False, classes=0)

        #Si no detecta una persona saltará un mensaje en la consola de mandos de que no hay elementos humanos en la imagen
        try:
            # Por cada resultado (imagen obtenida) vamos a analizar todas las máscaras localizadas en el tensor flow de máscaras
            for mascara in results[0].masks.masks:
                # Aqui se obtiene una de las máscara de la segmentación de los distintos elementos encontrados en la imagen de entrada
                im2 = (mascara.numpy() * 255).astype("uint8")
                im2 = cv2.resize(im2, (512, 512), interpolation=cv2.INTER_AREA)
                #Cargamos los pixeles de la img1
                pixels = im1.load()
                if mode != 0:
                    # Este bucle for para realizar el pixelado y el sombreado de las personas
                    for y in range(len(im2)):
                        for x in range(len(im2[y])):
                            if(im2[y, x] == 255):
                                #modo 1 es sombreado
                                if(mode == 1):
                                    pixels[x, y] = 0
                                #modo 2 es pixelado
                                elif(mode == 2):
                                    # Extraemos una dupla con las dimensiones de la imagen original
                                    dim = im1.size
                                    pixels[x, y] = Anonimizador.pixelado(x, y, pixels, 16, dim)
                                else:
                                    raise Exception("Choose a mode between 0 to 2")

                else:
                    # Guardamos la mascara para luego abrirla con PIL
                    cv2.imwrite("mascara.jpg", im2)

                    # Creamos el pipe para realizar la sustitución de los objetos identificados por el prompt que le pongamos,
                    pipe = StableDiffusionInpaintPipeline.from_pretrained(
                        "stabilityai/stable-diffusion-2-inpainting",
                        torch_dtype=torch.float32,
                    )

                    # Abrimos la mascara con PIL
                    mask = Image.open("mascara.jpg")


                    # Imagen procesada
                    imagenProcesada = pipe(prompt=prompt, image=im1, mask_image=mask).images[0]

                    # Sustituimos en la imagen original las personas por el prompt
                    #Cargamos los pixeles tanto de la mascar como de la imagen obtenida
                    pixelsMask = mask.load()
                    pixelsImagenP = imagenProcesada.load()
                    for y in range(512):
                        for x in range(512):
                            if pixelsMask[x, y] != 0:
                                pixels[x, y] = pixelsImagenP[x, y]
                    # Se guarda la imagen con una persona cambiada, esto se hace debido a poder depurar la herramienta debido al tiempo que tarda en generar una imagen totalmente anonimizada
                    im1.save(imgDest)

                # Guardado de la imagen procesada
                im1.save(imgDest)

        except:
            print("No hay elementos humanos")

        # Devolvemos la imagen
        return im1