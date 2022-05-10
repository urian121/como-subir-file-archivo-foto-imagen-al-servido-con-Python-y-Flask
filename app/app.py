from flask import Flask, render_template, request
from datetime import date
from random import sample

#Para subir archivo tipo foto al servidor
from werkzeug.utils import secure_filename 
import os


#Declarando nombre de la aplicación e inicializando
app = Flask(__name__)


#Redireccionando cuando la página no existe
@app.errorhandler(404)
def not_found(error):
    return 'Ruta no encontrada'


def stringAleatorio():
    #Generando string aleatorio
    string_aleatorio = "0123456789abcdefghijklmnopqrstuvwxyz_"
    longitud         = 20
    secuencia       = string_aleatorio.upper()
    resultado_aleatorio  = sample(secuencia, longitud)
    string_aleatorio     = "".join(resultado_aleatorio)
    return string_aleatorio
     
#Creando un Decorador
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route('/registrar-archivo', methods=['GET', 'POST'])
def registarArchivo():
        if request.method == 'POST':
            #estudiante          = request.form['estudiante']
            #data_created_ficha_univ = date.today()
             
            #Script para subir foto
            f = request.files['archivo']
            basepath = os.path.dirname (__file__) # La ruta donde se encuentra el archivo actual
            filename = secure_filename(f.filename) #Nombre original del archivo
            
            #capturando extension del archivo ejemplo: .png, .jpg, .pdf ...etc
            extension           = os.path.splitext(filename)[1]
            nuevoNombreFile     = stringAleatorio() + extension
     
            upload_path = os.path.join (basepath, 'static/archivos', nuevoNombreFile) #Nota: Si no hay una carpeta, debe crearla primero, de lo contrario se le preguntará que no existe tal ruta
            f.save(upload_path)
            
            return 'El Registro fue un Exito &#x270c;&#xfe0f;'
        return render_template('index.html')
    

if __name__ == '__main__':
    app.run(debug=True, port=5000)