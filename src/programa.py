import os
from flask import Flask, flash, request, redirect, url_for,send_from_directory, session, render_template
from werkzeug.utils import secure_filename
from main import char_list_from_file, infer
from model import DecoderType, Model

#UPLOAD_FOLDER = '../data/'

app = Flask(__name__)

app.secret_key = "secret key"

path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

unArchivo = ''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    print(path)
    print(UPLOAD_FOLDER)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            archivo = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(archivo)
            os.environ["img_file"] = archivo
            unArchivo = os.path.join(path,'uploads',filename)
            #return redirect(url_for('download_file', name=filename))
            session['filepath'] = archivo
            return redirect(url_for('infer_uploads'))
    return render_template('home.html')

@app.route('/infer', methods=['GET'])
def infer_uploads():
    #esta parte de buscar el archivo falla, hay que reparar aqui OJO
    print("un archivo")
    print(unArchivo)
    #elModel: Model
    model = Model(char_list_from_file(), DecoderType.BestPath, must_restore=True)
    #dump=args.dump
    archivo = session.get('filepath',None)
    texto = infer(model, archivo)
    return render_template('predicted.html', texto=texto)

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)