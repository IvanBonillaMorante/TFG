from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from Anonimizador import Anonimizador


app = Flask(__name__)

@app.before_request
def before_request():
    print("Antes de la peticion")

@app.after_request
def after_request(response):
    print("Despues de la peticion")
    return response

@app.route('/')
def index():
    # return "<h1>¡Hola mundo!</h1>"
    cursos = ['PHP', 'Pyhton', 'Java', 'Kotlin', 'Dart', 'JavaScript']
    data = {
        'titulo': 'Index',
        'bienvenida': '¡Saludos!',
        'cursos': cursos,
        'num_cursos': len(cursos)
    }
    return render_template('index.html', data=data)

@app.route('/contactos/<nombre>/<int:edad>')
def contacto(nombre, edad):
    data = {
        'titulo': 'Contacto',
        'nombre': nombre,
        'edad': edad
    }
    return render_template('contacto.html', data=data)


def query_string():
    print(request)
    print(request.args)
    print(request.args.get('param1'))
    print(request.args.get('param2'))
    return "ok"

def pagina_no_encontrada(error):
    #return render_template('404.html'), 404
    return redirect(url_for('index'))

@app.route('/prueba')
def prueba():
    data = {
        'titulo': 'Prueba',
    }

    return render_template('prueba.html', data=data)

@app.route('/prueba2')
def prueba2():
    data = {
        'titulo': 'Prueba',
    }

    return render_template('prueba2.html', data=data)

@app.route('/imagenes', methods=['POST'])
def imagenes():
    imagenes = request.files.getlist('lista')
    for imagen in imagenes:
        nombre_archivo = imagen.filename
        path = "/home/ivan/TFG/prueba_unitaria"

        upload_path = os.path.join(path, nombre_archivo)
        imagen.save(upload_path)

    anonimizador = Anonimizador()
    anonimizador.anonimizacion("/home/ivan/TFG/prueba_unitaria", 0, "/home/ivan/TFG/prueba_unitaria_procesada", "a person standing on his feet")

@app.route('/descarga')
def descarga():
    data = {
        'titulo': 'Descarga',
    }
    return render_template('descarga.html', data=data)

if __name__ == '__main__':
    app.add_url_rule('/query_string', view_func=query_string)
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(debug=True, port=6008, host="0.0.0.0")
