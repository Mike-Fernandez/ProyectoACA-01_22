# Archivo de control de la página principal del proyecto
#Librerias usadas, para el working directory, flask, para pasar el nombre del archivo subido, y los otros archivos del proyecto utilizados
import os
from flask import Flask, flash, request, redirect, url_for,send_from_directory, session, render_template
from werkzeug.utils import secure_filename
from main import char_list_from_file, infer
from model import DecoderType, Model


app = Flask(__name__)

app.secret_key = "secret key"

#Working directory
path = os.getcwd()
#Ruta para folder con imagenes subidas por usuario
UPLOAD_FOLDER = os.path.join(path, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Limite de tipo de archivos permitidos por la aplicación
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

#Método para revisar el formato del archivo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Método para manejar requests GET y POST en página principal
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    #Instrucciones cuando se realiza POST en home
    if request.method == 'POST':
        #Si no se encuentra el file
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        #Si el usuario no selecciona un archivo se crea un nuevo archivo vacío con nombre vacío
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        #Caso cuando se ha subido un archivo a la página principal
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #Creación de ruta del nuevo archivo
            archivo = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            #Se guarda el archivo
            file.save(archivo)
            os.environ["img_file"] = archivo
            #Se establece la ruta dentro de la sesión para que lo pueda recibir la siguiente página
            session['filepath'] = archivo
            #Redirect a la página de infer
            return redirect(url_for('infer_uploads'))
    #Se renderiza la página principal correspondiente a home.html
    return render_template('home.html')

#Función infer que maneja el método GET para la página de resultados
@app.route('/infer', methods=['GET'])
def infer_uploads():
    #Se instancia el modelo que leerá la imagen
    model = Model(char_list_from_file(), DecoderType.BestPath, must_restore=True)
    #Se obtiene la ruta del archivo de la sesión
    archivo = session.get('filepath',None)
    #Se realiza el reconocimiento de texto y se guarda la palabra resultante en la variable texto
    texto = infer(model, archivo)
    #Renderiza la template de resultado pasando la variable obtenida del modelo
    return render_template('predicted.html', texto=texto)

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)

#Se corre la aplicación en esta línea
#Aqui se definen los detalles de la dirección IP y el puerto donde se corre
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)