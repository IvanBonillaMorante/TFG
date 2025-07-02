import numpy as np
from skimage import io
from skimage.transform import resize
import torch
from diffusers import StableDiffusionInpaintPipeline
from ultralytics import YOLO
import os


class Anonimizador:

    def __init__(self, *args):
        if len(args) == 0:
            self.segmentation = "yolov8n-seg.pt"
        elif len(args) == 1:
            self.segmentation = args[0]
        else :
            print("Numero equivocado de argumentos")

    # Función que permite el pixelado de la imagen
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
        media = (componenteB / (px_size * px_size), componenteG / (px_size * px_size),
                 componenteR / (px_size * px_size))
        return media

    # Función que permite la anonimización de las persona detectadas, dandole la ruta de origen a la imagen, una carpeta como ruta de destino y un modo para el tipo de anonimización deseado
    # El argumento prompt es la linea que se usara para sustituir la mascara por lo que se ponga en esa linea
    def anonimizacion(self, imgOrig, mode, imgDest, prompt):

        # Se escoge el modelo de YOLOv8 de segmentación para identificar las personas dentro de la imagen
        model = YOLO(self.segmentation)

        lista = list()
        paths = imgOrig.split("/")

        if (os.path.isdir(imgOrig)):

            lista = os.listdir(imgOrig)

        else:

            name = paths[len(paths) - 1]
            imgOrig = imgOrig[0 : len(imgOrig) - len(name) - 1]
            lista.append(name)

        for img in lista:

            im1 = io.imread(imgOrig + "/" + img)

            # Redimensionamos la imagen para que psoteriormente pueda ser tratada por la función de difusión estable
            im1 = resize(im1, (512, 512, 3))
            image = im1.transpose((2, 0, 1))[np.newaxis, ...]
            image = torch.from_numpy(image)
            image = image.to("cuda")

            # Obtenemos los resultados de la segmentación indicando la imagen, si se guarda la imagen, y classes indica que clases detectar
            results = model.predict(source=image, save=False, save_txt=False, classes=0)

            if(results[0].masks != None):

                # Por cada resultado (imagen obtenida) vamos a analizar todas las máscaras localizadas en el tensor flow de máscaras
                for mascara in results[0].masks.masks:


                    # Aqui se obtiene una de las máscara de la segmentación de los distintos elementos encontrados en la imagen de entrada
                    array_of_ones = np.ones((512, 512, 3), "uint8")

                    #Prueba con (1 - im2) * im1 para el modo sombreado
                    if mode != 0:
                        im2 = (mascara.cpu().numpy() * 255).astype("uint8")
                        im2 = resize(im2, (512, 512, 3))

                        #modo 1 es sombreado
                        if(mode == 1):
                            im1 = np.multiply(np.subtract(array_of_ones, im2), im1)
                        #modo 2 es pixelado
                        elif(mode == 2):
                            for x in range(len(im2)):
                                for y in range(len(im2[x])):
                                    if (im2[x, y].all() == 1):
                                        dim = im1.shape
                                        im1[x, y] = Anonimizador.pixelado(x, y, im1, 16, dim)
                        else:
                            raise Exception("Choose a mode between 0 to 2")

                    else:

                        # Creamos el pipe para realizar la sustitución de los objetos identificados por el prompt que le pongamos,
                        pipe = StableDiffusionInpaintPipeline.from_pretrained(
                            "stabilityai/stable-diffusion-2-inpainting",
                            torch_dtype=torch.float32,
                        )

                        pipe.to("cuda")

                        # Imagen procesada
                        imagenesProcesadas = pipe(prompt=prompt, image=image, mask_image=mascara)
                        imagenProcesada = imagenesProcesadas.images[0]

                        # Sustituimos en la imagen original las personas por el prompt
                        mascara = mascara.cpu().numpy()
                        mascara = mascara[..., np.newaxis]
                        mascara = np.repeat(mascara, 3, -1)

                        imagenProcesada = np.array(imagenProcesada)
                        imagenProcesada = (imagenProcesada / 255).astype(np.float64)



                        fondo = np.multiply(np.subtract(array_of_ones, mascara), im1)
                        primerPlano = np.multiply(mascara, imagenProcesada)


                        im1 = np.add(fondo, primerPlano)

            name = img[0 : len(img) - 4]

            # Guardado de la imagen procesada
            im1 = (im1 * 255).astype(np.uint8)
            io.imsave(imgDest + "/" + name + "_procesado.png", im1)


if __name__=="__main__":
    import click

    @click.command()
    @click.option('--url', required=True, type=str, help='URL of the image as a string')
    @click.option('--mode', default=0, type=int, help='Mode as an integer')
    @click.option('--saving_path', required=True, type=str, help='Saving path as a string')
    @click.option('--prompt', required=True, type=str, help='Prompt as a string')
    def main(url, mode, saving_path, prompt):
        """
        Read and process command-line arguments.

        Args:
            url (str): URL of the image.
            mode (int): Mode as an integer.
            saving_path (str): Saving path for the image.
            prompt (str): Prompt for the operation.
        """
        # Your processing logic here
        a = Anonimizador()
        a.anonimizacion(url, mode, saving_path, prompt)

    main()


