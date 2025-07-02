from flask import Flask, render_template, request, redirect, url_for, send_file
import zipfile
import os
from Anonimizador import Anonimizador


app = Flask(__name__)


@app.route('/')
def inicio():
    data = {
        'titulo': 'Inicio',
    }
    return render_template('inicio.html', data=data)

@app.route('/imagenes', methods=['POST'])
def imagenes():
    imagenes = request.files.getlist('lista')
    modo = int(request.values.get('modo'))
    prompt = request.values.getlist('prompt')
    path = "/home/ivan/TFG/prueba_unitaria"
    for imagen in imagenes:
        nombre_archivo = imagen.filename

        upload_path = os.path.join(path, nombre_archivo)
        imagen.save(upload_path)

    anonimizador = Anonimizador()
    anonimizador.anonimizacion(path, modo, "/home/ivan/TFG/prueba_unitaria_procesada", prompt)
    for file in os.listdir(path):
        archivo = os.path.join(path, file)
        os.remove(archivo)
    return redirect(url_for('descarga'))

@app.route('/descarga')
def descarga():
    data = {
        'titulo': 'Descarga',
    }
    return render_template('descarga.html', data=data)

@app.route('/download')
def download():
    archivoZip = zipfile.ZipFile('descarga.zip', 'w')
    path = "/home/ivan/TFG/prueba_unitaria_procesada"
    for file in os.listdir(path):
        archivo = os.path.join(path,file)
        archivoZip.write(archivo, compress_type=zipfile.ZIP_DEFLATED)
        os.remove(archivo)
    archivoZip.close()
    return send_file('/home/ivan/TFG/descarga.zip', as_attachment=True)

def query_string():
    print(request)
    print(request.args)
    print(request.args.get('param1'))
    print(request.args.get('param2'))
    return "ok"

def pagina_no_encontrada(error):
    return redirect(url_for('inicio'))

if __name__ == '__main__':
    app.add_url_rule('/query_string', view_func=query_string)
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(debug=True, port=6008, host="0.0.0.0")
