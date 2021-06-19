from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail

from .models.ModeloLibro import ModeloLibro
from .models.ModeloUsuario import ModeloUsuario
from .models.ModeloCompra import ModeloCompra
from .consts import *
from .emails import confirmacion_compra

from .models.entities.Usuario import Usuario
from .models.entities.Compra import Compra
from .models.entities.Libro import Libro

app = Flask(__name__)

csrf=CSRFProtect()
db=MySQL(app)
login_manager_app = LoginManager(app)
mail=Mail()

# Es un callback para recargar el usuario pasando el id almacenado en la sesión
@login_manager_app.user_loader
def load_user(id):
    return ModeloUsuario.obtener_por_id(db, id)

@app.route('/login', methods =["GET", "POST"])
def login():
    #CSRF=Cross-site request Forgery = solicitud de falsificación entre sitios
    #Vamos a meter una seguridad para que nadie pueda hacer peticiones a nuestro sitio
    if request.method=="POST":
        # print(request.form["usuario"])
        # print(request.form["password"])
        usuario = Usuario(None, request.form["usuario"], request.form["password"], None)
        usuario_logeado = ModeloUsuario.login(db,usuario)
        if usuario_logeado != None :
            #una vez autentificado te logeas con la función login_user
            login_user(usuario_logeado)
            flash(MSG_BIENVENIDA, "success")
            return redirect(url_for('index'))
        else:
            flash(LOGIN_INCORRECTO, "warning")
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')

@app.route('/logout')
def logout():
    logout_user();
    flash(LOGOUT, 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    if current_user.is_authenticated:
        if current_user.tipousuario.id == 1:
            try:
                libros_vendidos = ModeloLibro.listar_libros_vendidos(db)
                data ={
                    'titulo': "Libros vendidos",
                    'libros_vendidos': libros_vendidos
                }
                return render_template('index.html', data=data)
            except Exception as ex:
                return render_template('errores/error.html', mensaje=format(ex))
        else:
            try:
                compras=ModeloCompra.listar_compras_usuario(db, current_user)
                data={
                    'titulo': "Mis compras",
                    'compras': compras
                }
                return render_template('index.html', data=data)
            except Exception as ex:
                return render_template('errores/error.html', mensaje=format(ex))

    else:
        return redirect(url_for('login'))

@app.route('/libros')
@login_required
def listar_libros():
    try:
        libros = ModeloLibro.listar_libros(db)
        data = {
            'titulo': "Listado de libros",
            'libros': libros
        }
        return render_template('listado_libros.html', data=data)
        # return "conexión ok con libros. Número de libros: {0}".format(len(data))
    except Exception as ex:
        return render_template('errores/error.html', mensaje=format(ex))

@app.route('/comprarLibro', methods=['POST'])
@login_required
def comprar_libro():
    data_request = request.get_json()
    data = {}
    #print(data_request)
    try:
        #libro=Libro(data_request['isbn'],None,None,None,None)
        libro = ModeloLibro.leer_libro(db, data_request['isbn'])
        compra = Compra(None, libro, current_user)
        data['exito']= ModeloCompra.registrar_compra(db, compra )
        #confirmacion_compra_sincrona(mail, current_user, libro) #Envio síncrono
        confirmacion_compra(app, mail, current_user, libro)     # Envío asíncrono
    except Exception as ex:
        data['mensaje']= format(ex)
        data['exito']= False
    return jsonify(data)  #pasamos el diccinario a formato json

def paginaNoEncontrada(error):
    return render_template("errores/error404.html"), 404

def paginaNoAutorizada(error):
    return redirect(url_for('login'))

def inicializar_app(config):
    app.config.from_object(config)
    csrf.init_app(app)
    mail.init_app(app)
    app.register_error_handler(404, paginaNoEncontrada)
    app.register_error_handler(401, paginaNoAutorizada)
    return app