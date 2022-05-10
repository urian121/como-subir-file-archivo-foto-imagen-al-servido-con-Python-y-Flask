#Importando  flask y algunos paquetes para la session y BD
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import date
from random import sample
#from funciones import *


from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash

#Para subir archivo tipo foto al servidor
from werkzeug.utils import secure_filename 
import os

#Declarando nombre de la aplicación e inicializando
app = Flask(__name__)


# Cambiar esto a su clave secreta
app.secret_key = '97110c8ae51a4b5af397be6534caef90e4bb9b1dcb3380af008f90b23a5d1616bf319bc29098105da20fe'

# Ingrese los detalles de conexión de su base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'library_iberonex'

# Inicializar MySQL
mysql = MySQL(app)



#Redireccionando cuando la página no existe
@app.errorhandler(404)
def not_found(error):
    if 'conectado' in session:
        return redirect(url_for('cpanel'))
    else:
        return redirect(url_for('login'))

#creando una funcion y dentro de la misma una data (un diccionario)
#con valores del usuario ya logueado
def dataLoginSesion():
    inforLogin = {
        "idLogin":session['id'],
        "emailLogin":session['email_user'],
        "nombreLogin":session['nombres'],
        "univLogin":session['universidad'],
        "tipoLogin":session['tipo_user'],
        "paisLogin":session['pais'],
        "estatusLogin":session['estatus_user']
    }
    return inforLogin

def listaPaises():
    #Listando de Paises
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM paises")
    paises = cursor.fetchall()
    cursor.close()
    return paises

def listaUniversidades():
    #Listando de Universidades
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM universidades')
    universidades = cursor.fetchall()
    cursor.close()
    return universidades

def listaTipoUsuarios():
    #Listando los tipos de usuarios
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM tipo_user")
    dataUsers = cursor.fetchall()
    cursor.close()
    return dataUsers
    
def listaContenidos():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM contents_univs')
    contenidos = cursor.fetchall()
    cursor.close()
    return contenidos

def stringAleatorio():
    #Generando string aleatorio
    string_aleatorio = "0123456789abcdefghijklmnopqrstuvwxyz_"
    longitud         = 20
    secuencia       = string_aleatorio.upper()
    resultado_aleatorio  = sample(secuencia, longitud)
    string_aleatorio     = "".join(resultado_aleatorio)
    return string_aleatorio

def listaFichasUniversidades():  
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)         
    cursor.execute('SELECT funiv .*, univs .*, p .* FROM ficha_univs AS funiv INNER JOIN universidades AS univs ON funiv.univ_id = univs.id INNER JOIN paises AS p ON funiv.pais_id = p.id')
    fichaUniversidades = cursor.fetchall()
    cursor.close()
    return fichaUniversidades

def listadeUniversidadesConPaises():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT univs .*, ps .* FROM universidades AS univs INNER JOIN paises AS ps ON univs.pais_univ_id = ps.id')
    universidades = cursor.fetchall()
    cursor.close()  
    return universidades
    
def listaDeEstudiantes()      :
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE tipo_user = 3')
    estudiantes = cursor.fetchall()
    cursor.close()
    return estudiantes

def listaDeCriadores():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE tipo_user = 2')
    criadores = cursor.fetchall()
    cursor.close()
    return criadores

        
#Creando un Decorador
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'conectado' in session:
        return redirect(url_for('cpanel'))
    else:
        msg = ''
        msjStatus =""
        # Compruebe si existen solicitudes POST de "nombre de usuario" y "contraseña" (formulario enviado por el usuario)
        if request.method == 'POST' and 'email_user' in request.form and 'password' in request.form:
            # Crear variables para facilitar el acceso
            email_user = request.form['email_user']
            password   = request.form['password']
            
            # Comprobar si existe una cuenta usando MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM users WHERE email_user = %s", [email_user])
            # Obtener un registro y devolver el resultado
            account = cursor.fetchone()
            cursor.close()
            
            # Si la cuenta existe en la tabla de cuentas en la base de datos, se declaran las variables de sesión
            if account:
                if check_password_hash(account['password'],password):
                    # Crear datos de sesión, podemos acceder a estos datos en otras rutas
                    session['conectado']        = True
                    session['id']               = account['id']
                    session['email_user']       = account['email_user']
                    session['nombres']          = account['nombres']
                    session['apellidos']        = account['apellidos']
                    session['universidad']      = account['universidad']
                    session['tipo_user']        = account['tipo_user']
                    session['pais']             = account['pais']
                    session['ciudad']           = account['ciudad']
                    session['telefono']         = account['telefono']
                    session['estatus_user']     = account['estatus_user']
                    
                    
                    #Redireccionar de acuerdo al nivel de usuario en cuestio.
                    if(session['tipo_user']) == 1: #Administrador
                        return render_template('public/layout.html', dataLogin = dataLoginSesion())
                        #return redirect(url_for('cpanel', dataLogin = dataLoginSesion()))
                    elif (session['tipo_user'] == 2 and session['estatus_user'] == 1): #Creador de contenido - profesor Activo
                        return render_template('public/layout.html', dataLogin = dataLoginSesion())
                    elif (session['tipo_user'] == 2 and session['estatus_user'] == 0): #Creador de contenido - profesor NO Activo
                        msjStatus ="Perfil no Activo"
                        return 'caso 3'
                        return render_template('login/login.html', msjStatus = msjStatus)
                    elif (session['tipo_user'] == 3 and session['estatus_user'] == 1): #Perfil de estudiantes
                        return 'caso 4'
                        return render_template('public/home-user.html')
                    else:
                        return render_template('login/login.html', msg=msg)
                    
            else:
                # La cuenta no existe o el nombre de usuario/contraseña es incorrecto
                msg = 'Incorrect email_user/password!'
            
    #Mostrar el formulario de inicio de sesión con el mensaje (si corresponde)
    return render_template('login/login.html', msg=msg)



# necesitamos usar solicitudes GET y POST
@app.route('/register', methods=['GET', 'POST'])
def registerUser():
    msg = ''
    if request.method == 'POST':
        nombres         = request.form['nombres']
        apellidos       = request.form['apellidos']
        universidad     = request.form['universidad']
        tipo_user       = request.form['tipo_user']
        email_user      = request.form['email_user']
        password        = request.form['password']
        pais            = request.form['pais']
        ciudad          = request.form['ciudad']
        telefono        = request.form['telefono']
        estatus_user    = 0
        
        # Comprobar si existe una cuenta usando MySQL, con respecto al email
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email_user = %s', (email_user,))
        account = cursor.fetchone()
        cursor.close()
          
        # Si la cuenta existe, muestra los controles de error y validación.
        if account:
            msg = 'la cuenta ya existe!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email_user):
            msg = 'Dirección de correo electrónico no válida!'
        elif not re.match(r'[A-Za-z0-9]+', nombres):
            msg = 'El nombre de usuario debe contener solo caracteres y números!'
        elif not email_user or not password or not nombres:
            msg = 'por favor rellena el formulario!'
        else:
            # La cuenta no existe y los datos del formulario son válidos,
            # ahora inserte una nueva cuenta en la tabla de cuentas
            
            #Fecha actual
            created_users = date.today()
            nueva_password = generate_password_hash(password, method='sha256')
            cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (nombres, apellidos, universidad, tipo_user, email_user, nueva_password, pais, ciudad, telefono, estatus_user, created_users ))
            mysql.connection.commit()
            cursor.close()
            msg = 'Se ha registrado exitosamente!'
        return render_template('login/login.html', msg=msg)
    return render_template('login/page_register.html', msg=msg)


@app.route('/register-user')
def viewRegisterUser():
    return render_template('login/page_register.html', users=listaTipoUsuarios(), dataUniversidades=listaUniversidades(), dataPaises = listaPaises()) 

 
@app.route('/crear-contenido-creador', methods=['GET', 'POST'])
def viewRegisterContent():
    if 'conectado' in session:
        return render_template('public/Modulo_creadores_contenidos/create_contenido.html', dataLogin = dataLoginSesion())
           
    return redirect(url_for('login'))


@app.route('/contenidos', methods=['GET', 'POST'])
def viewContents():
    if 'conectado' in session:
        return render_template('public/Modulo_creadores_contenidos/list_contents.html', dataContents=listaContenidos(), dataLogin = dataLoginSesion())
           
    return redirect(url_for('login'))


# Cerrar session del usuario
@app.route('/logout')
def logout():
    msgClose = ''
    # Eliminar datos de sesión, esto cerrará la sesión del usuario
    session.pop('conectado', None)
    session.pop('id', None)
    session.pop('email_user', None)
    #return render_template('login/login.html', msgClose=msgClose)
    return redirect(url_for('login',msgClose = msgClose))


@app.route('/cpanel')
def cpanel():
    # Compruebe si el usuario está conectado
    if 'conectado' in session:
        return render_template('public/layout.html', dataLogin = dataLoginSesion())
    # El usuario no ha iniciado sesión redirigido a la página de inicio de sesión
    return redirect(url_for('login'))


@app.route('/perfil')
def perfil():
    if 'conectado' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.close()
        # Mostrar la página de perfil con información de la cuenta
        return render_template('public/Modulo_perfil/perfil.html', dataPerfil=account, dataLogin = dataLoginSesion())
    return redirect(url_for('login'))


@app.route('/criadores')
def criadores():
    if 'conectado' in session:
        if(session['tipo_user']==1):
            return render_template('public/Modulo_creadores_contenidos/list_creadores.html', dataCriadores=listaDeCriadores(), dataLogin = dataLoginSesion())
        else:
            return redirect(url_for('cpanel'))
    return redirect(url_for('login'))


@app.route('/estudiantes')
def estudiantes():
    if 'conectado' in session:
        if(session['tipo_user']==1):
            return render_template('public/Modulo_students/list_students.html', dataEstudiantes=listaDeEstudiantes(), dataLogin = dataLoginSesion())
        else:
            return redirect(url_for('cpanel'))
    return redirect(url_for('login'))


@app.route('/registrar-ficha-de-la-universidad')
def universidad():
    if 'conectado' in session:
        return render_template('public/Modulo_ficha_univ/nueva_universidad.html', dataUniversidades=listaUniversidades(), dataPaises = listaPaises(), dataLogin = dataLoginSesion()) 
    else:
        return redirect(url_for('login'))


@app.route('/register-universidad', methods=['GET', 'POST'])
def registerUniv():
    if 'conectado' in session:
        msg = ''
        if request.method == 'POST':
            univ_id             = request.form['univ_id']
            pais_id             = request.form['pais_id']
            campus              = request.form['campus']
            number_alumnos      = request.form['number_alumnos']
            rector_univ         = request.form['rector_univ']
            email_rector        = request.form['email_rector']
            pag_web             = request.form['pag_web']
            year_creacion       = request.form['year_creacion']
            description_univ    = request.form['description_univ']
            
            #Script para subir foto
            f = request.files['logo_univ']
            basepath = os.path.dirname (__file__) # La ruta donde se encuentra el archivo actual
            filename = secure_filename(f.filename) #Nombre original de la foto
            
            #https://gist.github.com/LuisAlejandroSalcedo/7d9de1c8d50b2c05bfffbc9092da11e0
            #Generador_de_Contraseñas.py
            #capturando extension del archivo ejemplo: .png, .jpg, .pdf ...etc
            extension           = os.path.splitext(filename)[1]
            nuevoNombreFile     = stringAleatorio() + extension
     
            upload_path = os.path.join (basepath, 'static/logos_univ', nuevoNombreFile) #Nota: Si no hay una carpeta, debe crearla primero, de lo contrario se le preguntará que no existe tal ruta
            f.save(upload_path)
            
            #Fecha actual
            data_created_ficha_univ = date.today()
            
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO ficha_univs (univ_id, pais_id, campus, number_alumnos, rector_univ, email_rector, pag_web, year_creacion, description_univ, logo_univ, data_created_ficha_univ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (univ_id, pais_id, campus, number_alumnos, rector_univ, email_rector, pag_web, year_creacion, description_univ, nuevoNombreFile, data_created_ficha_univ))
            mysql.connection.commit()
            cursor.close()
            msg = 'Se ha registrado exitosamente!'
            return redirect(url_for('cpanel'))
    
    return render_template('login/page_register.html', msg=msg, dataLogin = dataLoginSesion())


@app.route('/update-estatus-user', methods=['GET', 'POST'])
def updateStatusUser():
    if 'conectado' in session:
        if(session['tipo_user']==1):
            if request.method=='POST':
                idUser        = request.form['id']
                estatus_user  = request.form['estatus']
                
                cur = mysql.connection.cursor()
                cur.execute("""
                    UPDATE users
                    SET estatus_user=%s
                    WHERE id=%s
                    """, (estatus_user, idUser))
                mysql.connection.commit()
                cur.close()
                return estatus_user
        else:
            return redirect(url_for('cpanel'))
    return redirect(url_for('cpanel'))


@app.route('/update-estatus-student', methods=['GET', 'POST'])
def updateStatuStudents():
    if 'conectado' in session:
        if(session['tipo_user']==1):
            if request.method=='POST':
                idUser        = request.form['id']
                estatus_user  = request.form['estatus']
                
                cur = mysql.connection.cursor()
                cur.execute("""
                    UPDATE users
                    SET estatus_user=%s
                    WHERE id=%s
                    """, (estatus_user, idUser))
                mysql.connection.commit()
                cur.close()
                return estatus_user
        else:
            return redirect(url_for('cpanel'))
    return redirect(url_for('login'))



@app.route('/register-content', methods=['GET', 'POST'])
def registerContent():
    if 'conectado' in session:
        msg = ''
        msg_insert = ''
        if request.method == 'POST':
            tipo_content            = request.form['tipo_content']
            title_content           = request.form['title_content']
            autor_content           = request.form['autor_content']
            fuente_content          = request.form['fuente_content']
            idioma_content          = request.form['idioma_content']
            tematica_content        = request.form['tematica_content']
            date_creacion_content   = request.form['date_creacion_content']
            univ_id                 = request.form['univ_id']
            facultad_content        = request.form['facultad_content']
            
            url_content             = request.form['url_content']
            resumen_content         = request.form['resumen_content']
            contenido_content       = request.form['contenido_content']
            acceso_contenido        = request.form['acceso_contenido']
            
            dateCreate_content      = date.today()
            estatus_content         = 0
            content_user_id         = 9
            
            #Script para subir foto
            f = request.files['imagen_content']
            basepath = os.path.dirname (__file__) # La ruta donde se encuentra el archivo actual
            imagen_content = secure_filename(f.filename)
            
            extensionFoto           = os.path.splitext(imagen_content)[1]
            nuevoNombreFoto     = stringAleatorio() + extensionFoto
            
            upload_path = os.path.join (basepath, 'static/contents', nuevoNombreFoto) #Nota: Si no hay una carpeta, debe crearla primero, de lo contrario se le preguntará que no existe tal ruta
            f.save(upload_path)
            
            
            #script subir archivo pdf
            fpdf = request.files['archivo_pdf_content']
            basepath_pdf        = os.path.dirname (__file__) # La ruta donde se encuentra el archivo actual
            archivo_pdf_content = secure_filename(fpdf.filename)
            
            extensionFile       = os.path.splitext(archivo_pdf_content)[1]
            nuevoNombreFile     = stringAleatorio() + extensionFile
            
            upload_path_pdf = os.path.join (basepath_pdf, 'static/contents', nuevoNombreFile) 
            f.save(upload_path_pdf)
            
            
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO contents_univs (tipo_content, title_content, autor_content, fuente_content, idioma_content, tematica_content, date_creacion_content, univ_id, facultad_content, imagen_content, archivo_pdf_content, url_content, resumen_content, contenido_content, dateCreate_content, estatus_content, acceso_contenido, content_user_id ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (tipo_content, title_content, autor_content, fuente_content, idioma_content, tematica_content, date_creacion_content, univ_id, facultad_content, nuevoNombreFoto, nuevoNombreFile, url_content, resumen_content, contenido_content, dateCreate_content, estatus_content, acceso_contenido, content_user_id))
            mysql.connection.commit()
            cursor.close()
            msg_insert = 'Se ha registrado exitosamente!'
            
            return render_template('public/list_contents.html', dataContents=listaContenidos(), msg_insert=msg_insert, dataLogin = dataLoginSesion())
    return render_template('login/page_register.html', msg=msg)


@app.route('/nueva-universidad')
def viewRegisterUniv():
    if 'conectado' in session:
        if(session['tipo_user']==1):
            return render_template('public/Modulo_univ/nueva_universidad.html', dataPaises = listaPaises(), dataLogin = dataLoginSesion())  
        else:
            return redirect(url_for('cpanel'))
    else:
        return redirect(url_for('login'))
  

@app.route('/registar-nueva-universidad', methods=['GET', 'POST'])
def registerNuevaUniversidad():
    if 'conectado' in session:
        if(session['tipo_user']==1):
            msg = ''
            if request.method == 'POST':
                name_univ         = request.form['name_univ']
                pais_univ_id      = request.form['pais_univ_id']
                
                cursor = mysql.connection.cursor()
                cursor.execute('INSERT INTO universidades (name_univ, pais_univ_id) VALUES (%s, %s)', (name_univ, pais_univ_id))
                mysql.connection.commit()
                cursor.close()
                msg = 'Se ha registrado exitosamente!'
                return redirect(url_for('universidades'))
        else:
            return redirect(url_for('cpanel'))
    return render_template('login/page_register.html', msg=msg, dataLogin = dataLoginSesion())



@app.route('/universidades')
def universidades():
    if 'conectado' in session:
            if(session['tipo_user']==1):
                return render_template('public/Modulo_univ/list_universidades.html', dataUniversidades=listadeUniversidadesConPaises(), dataLogin = dataLoginSesion())
            else:
                return redirect(url_for('cpanel'))
    else:
        return redirect(url_for('login'))


@app.route('/fichas-de-universidades', methods=['GET', 'POST'])
def viewFichasUnivs():
    if 'conectado' in session:
        return render_template('public/Modulo_ficha_univ/list_fichas_universidades.html', dataFichaUnivs=listaFichasUniversidades(), dataLogin = dataLoginSesion())
    else:
        return redirect(url_for('login'))


@app.route('/view-edit-univ/<id>', methods = ['POST','GET'])
def viewEditarUniv(id):
    if 'conectado' in session:
        if(session['tipo_user']==1):
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT * FROM universidades WHERE id = %d " % int(id))
            dataUni = cur.fetchall()
            """
            cantidadRegistros = cur.rowcount
            if(cantidadRegistros):
                return 'hay'
            else:
                return 'no hay'
            """
            cur.close()
            return render_template('public/Modulo_univ/update_universidad.html', univ = dataUni[0], dataPaises = listaPaises(), dataLogin = dataLoginSesion())
        else:
            return redirect(url_for('cpanel'))
            
@app.route('/update/<id>', methods=['POST'])
def updateUniv(id):
    if 'conectado' in session:
        if request.method == 'POST':
            name_univ     = request.form['name_univ']
            pais_univ_id  = request.form['pais_univ_id']
            
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("UPDATE universidades SET name_univ = %s, pais_univ_id = %s WHERE id = %s", (name_univ, pais_univ_id, id))
            mysql.connection.commit()
            cur.close()
            #flash('Contact Updated Successfully')
            
            return render_template('public/Modulo_univ/list_universidades.html', dataUniversidades=listadeUniversidadesConPaises(), dataLogin = dataLoginSesion())



if __name__ == '__main__':
    app.run(debug=True, port=5000)