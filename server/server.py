# -*- coding: utf-8 -*-
"""
@author: Luis Fdo. Pérez

Server of the Application
"""
import config, random, string

from flask import Flask, request, render_template, redirect, session, url_for
from flask.ext import login
from flask.ext.mongoengine import MongoEngine
from flask.ext.mail import Mail, Message

from models import Usuarios, Asignaturas, Temas, Preguntas, Examenes, Opciones
from forms import GeneraExamenForm, ProfileForm

from export import exportODT, exportODT2, exportPDF

from tkFileDialog import asksaveasfilename
from tkMessageBox import showinfo, showerror


#========================================#
#    Creation of the Web Application     #
#========================================#
app=Flask(__name__)
app.config.from_object(config)

# 
db = MongoEngine()
db.init_app(app)

# Initialize the application to send mails
mail = Mail(app)

# Initialize ddbb
def init_ddbb():
    # Compruebo que no existe el usuario admin
    num = Usuarios.objects(usuario="admin").count()
    if num == 0:
        
        # Grabo al usuario admin y a un profesor y a un alumno de prueba
        admin = Usuarios(nombre="admin", apellidos="", usuario="admin", password="educaweb", email="admin@uned.es", tipo=0, activado=True)
        admin.save()
        profe = Usuarios(nombre="profe", apellidos="", usuario="profe1", password="profe1", email="profe1@uned.es", tipo=1, activado=True)
        profe.save()
        alumno = Usuarios(nombre="alumno", apellidos="", usuario="alumno1", password="alumno1", email="alumno1@uned.es", tipo=2, activado=True)
        alumno.save()

        # Registros de prueba -- BORRAR EN PRODUCCIÓN      
        asignaturas = ["Procesadores del lenguaje", "Sistemas Operativos", "Inteligencia Artificial", "Redes", "Sistemas Distribuidos"]
        
        temas = [ 
            ("Introducción", "Analisis Lexico", "Analisis sintactico"), 
            ("Fundamentos de los SO", "Sistemas Operativos multitarea"),
            ("Introducción a la IA", "Logica", "Sistemas Expertos"), 
            ("Redes LAN", "TCP/IP", "ADSL"), 
            ("Fundamentos de los S.D.", "Comunicación entre procesos" )
            ]
            
        opcion1 = Opciones(letra="A", texto="opcion A")
        opcion2 = Opciones(letra="B", texto="opcion B")

        preguntas = [
            (
                (   ("pregunta 1 procesadores - introducción", 0),
                    ("pregunta 2 procesadores - introducción", 0)
                ),
                (   ("pregunta 1 procesadores - a.lex.", 0),
                    ("pregunta 2 procesadores - a-lex.", 0),
                    ("pregunta 3 procesadores - a-lex.", 0)
                ),
                (   ("pregunta 1 procesadores - a.sint.", 0),
                    ("pregunta 2 procesadores - a.sint.", 0)
                )
            ),
            (
                (   ("pregunta 1 Sist. Op. - fundamentos", 0),
                    ("pregunta 2 Sist. Op. - fundamentos", 0)
                ),
                (   ("pregunta 1 Sist. Op. - S.O. Multitarea", 0),
                    ("pregunta 2 Sist. Op. - S.O. Multitarea", 0)
                )
            ),
            (
                (   ("pregunta 1 IA - introducción", 1, (opcion1, opcion2), "A"),
                    ("pregunta 2 IA - introducción", 1, (opcion1, opcion2), "B"),
                    ("pregunta 3 IA - introducción", 1, (opcion1, opcion2), "B")
                ),
                (   ("pregunta 1 IA - Logica", 1, (opcion1, opcion2), "B"),
                    ("pregunta 2 IA - Logica", 1, (opcion1, opcion2), "A")
                ),
                (   ("pregunta 1 IA - Sist. Ex.", 1, (opcion1, opcion2), "A"),
                    ("pregunta 2 IA - Sist. Exp.", 1, (opcion1, opcion2), "A")
                )
            ),
            (
                (   ("pregunta 1 Redes - Redes LAN", 2, True),
                    ("pregunta 2 Redes - Redes LAN", 2, False),
                ),
                (   ("pregunta 1 Redes - TCP/IP", 2, False),
                    ("pregunta 2 Redes - TCP/IP", 2, False),
                ),
                (   ("pregunta 1 Redes - ADSL", 2, True),
                    ("pregunta 2 Redes - ADSL", 2, True),
                ),
            ),
            (
                (   ("pregunta 1 Sist. Op. - fundamentos", 1, (opcion1, opcion2), "B"),
                    ("pregunta 2 Sist. Op. - fundamentos", 1, (opcion1, opcion2), "A")
                ),
                (   ("pregunta 1 Sist. Op. - S.O. Multitarea", 1, (opcion1, opcion2), "A"),
                    ("pregunta 2 Sist. Op. - S.O. Multitarea", 1, (opcion1, opcion2), "B")
                )
            )
            ]

        for i in range(len(asignaturas)):
            asignatura = Asignaturas()
            asignatura.asignatura = asignaturas[i]
            asignatura.save()
            profe.asignaturas = profe.asignaturas.append(asignatura)
            alumno.asignaturas = alumno.asignaturas.append(asignatura)
            num_pregunta = 1
            
            for j in range(len(temas[i])):
                tema = Temas()
                tema.num = j+1
                tema.descripcion = temas[i][j]
                tema.asignatura = asignatura
                tema.usuario = profe
                tema.save()                
                
                for k in range(len(preguntas[i][j])):
                    pregunta = Preguntas()
                    pregunta.num = num_pregunta
                    pregunta.texto = preguntas[i][j][k][0]
                    pregunta.tema = tema
                    pregunta.tipo = preguntas[i][j][k][1]
                    
                    if pregunta.tipo == 1:
                        for opcion in preguntas[i][j][k][2]:
                            pregunta.opciones = pregunta.opciones.append(opcion)
                        pregunta.correcta = preguntas[i][j][k][3]
                    
                    if pregunta.tipo == 2:
                        pregunta.verdadera = preguntas[i][j][k][2]
                        
                    pregunta.asignatura = asignatura
                    pregunta.usuario = profe
                    pregunta.save()
                    
                    num_pregunta = num_pregunta + 1

        
    #if num == 0:       
        #Usuarios(nombre="admin", apellidos="", usuario="admin", password="educaweb", email="admin@uned.es", tipo=0, activado=True).save()

        #procesadores = Asignaturas(asignatura="Procesadores del lenguaje")
        #procesadores.save()        

        #ss_oo = Asignaturas(asignatura="Sistemas Operativos")
        #ss_oo.save()
       
        #leng = Asignaturas(asignatura="Lenguajes de Programación")
        #leng.save()
        
        #ia = Asignaturas(asignatura="Inteligencia Artificial")
        #ia.save()
        
        #redes = Asignaturas(asignatura="Redes")
        #redes.save()
        
        #profe1 = Usuarios(nombre="profe1", usuario="profe1", password="profe1", email="profe1@uned.es", tipo=1, activado=True, asignaturas={ss_oo, redes, procesadores})
        #profe1.save()

        #luisfer = Usuarios(nombre = "Luis F.", apellidos="Pérez", usuario="luisfer", password="luisfer", email="luifito@gmail.com", tipo=1, activado=True, asignaturas={procesadores, ia, leng})
        #luisfer.save()
        
        # IA - preguntas Test
        #tema1 = Temas(num=1, descripcion="Introduccion a la IA", asignatura=ia, usuario=luisfer).save()
        #tema2 = Temas(num=2, descripcion="Logica", asignatura=ia, usuario=luisfer).save()
        #tema3 = Temas(num=3, descripcion="Sistemas expertos", asignatura=ia, usuario=luisfer).save()
        """
        opcion1 = Opciones(letra="A", texto="opcion A")
        opcion2 = Opciones(letra="B", texto="opcion B")
        Preguntas(num=1, texto="Pregunta 1 del tema 1 de IA", asignatura=ia, tema=tema1, tipo=1, opciones={opcion1, opcion2}, correcta="A", usuario=profe).save()
        Preguntas(num=2, texto="Pregunta 2 del tema 1 de IA", asignatura=ia, tema=tema1, tipo=1, opciones={opcion1, opcion2}, correcta="B", usuario=luisfer).save()
        Preguntas(num=3, texto="Pregunta 1 del tema 2 de IA", asignatura=ia, tema=tema2, tipo=1, opciones={opcion1, opcion2}, correcta="B", usuario=luisfer).save()
        Preguntas(num=4, texto="Pregunta 2 del tema 2 de IA", asignatura=ia, tema=tema2, tipo=1, opciones={opcion1, opcion2}, correcta="B", usuario=luisfer).save()
        Preguntas(num=5, texto="Pregunta 1 del tema 3 de IA", asignatura=ia, tema=tema3, tipo=1, opciones={opcion1, opcion2}, correcta="A", usuario=luisfer).save()
        Preguntas(num=6, texto="Pregunta 2 del tema 3 de IA", asignatura=ia, tema=tema3, tipo=1, opciones={opcion1, opcion2}, correcta="A", usuario=luisfer).save()
        
        # Redes - preguntas Verdadero o falso
        #tema1 = Temas(num=1, descripcion="Redes LAN", asignatura=redes, usuario=luisfer).save()
        #tema2 = Temas(num=2, descripcion="TCP/IP", asignatura=redes, usuario=luisfer).save()
        #tema3 = Temas(num=3, descripcion="ADSL", asignatura=redes, usuario=luisfer).save()
        Preguntas(num=1, texto="Pregunta 1 del tema 1 de Redes", asignatura=redes, tema=tema1, tipo=2, verdadera=True, usuario=luisfer).save()
        Preguntas(num=2, texto="Pregunta 2 del tema 1 de Redes", asignatura=redes, tema=tema1, tipo=2, usuario=luisfer).save()
        Preguntas(num=3, texto="Pregunta 1 del tema 2 de Redes", asignatura=redes, tema=tema2, tipo=2, verdadera=True, usuario=luisfer).save()
        Preguntas(num=4, texto="Pregunta 2 del tema 2 de Redes", asignatura=redes, tema=tema2, tipo=2, usuario=luisfer).save()
        Preguntas(num=5, texto="Pregunta 1 del tema 3 de Redes", asignatura=redes, tema=tema3, tipo=2, verdadera=True, usuario=luisfer).save()
        Preguntas(num=6, texto="Pregunta 2 del tema 3 de Redes", asignatura=redes, tema=tema3, tipo=2, usuario=luisfer).save()

        # Procesadores - preguntas desarrollo        
        #tema1 = Temas(num=1, descripcion="Introducción", asignatura=procesadores, usuario=luisfer)
        #tema1.save()
        #tema2 = Temas(num=2, descripcion="Analisis Lexico", asignatura=procesadores, usuario=luisfer)
        #tema2.save()
        #tema3 = Temas(num=3, descripcion="Analisis sintactico", asignatura=procesadores, usuario=luisfer)
        #tema3.save()
        Preguntas(num=1, texto="Pregunta 1 del tema 1 de Procesadores a desarrollar", asignatura=procesadores, tema=tema1, tipo=0, usuario=luisfer).save()
        Preguntas(num=2, texto="Pregunta 2 del tema 1 de Procesadores a desarrollar", asignatura=procesadores, tema=tema1, tipo=0, usuario=luisfer).save()
        Preguntas(num=3, texto="Pregunta 3 del tema 1 de Procesadores a desarrollar", asignatura=procesadores, tema=tema1, tipo=0, usuario=luisfer).save()
        Preguntas(num=4, texto="Pregunta 4 del tema 1 de Procesadores a desarrollar", asignatura=procesadores, tema=tema1, tipo=0, usuario=luisfer).save()
        Preguntas(num=5, texto="Pregunta 1 del tema 2 de Procesadores a desarrollar", asignatura=procesadores, tema=tema2, tipo=0, usuario=luisfer).save()
        Preguntas(num=6, texto="Pregunta 2 del tema 2 de Procesadores a desarrollar", asignatura=procesadores, tema=tema2, tipo=0, usuario=luisfer).save()
        Preguntas(num=7, texto="Pregunta 3 del tema 2 de Procesadores a desarrollar", asignatura=procesadores, tema=tema2, tipo=0, usuario=luisfer).save()
        Preguntas(num=8, texto="Pregunta 4 del tema 2 de Procesadores a desarrollar", asignatura=procesadores, tema=tema2, tipo=0, usuario=luisfer).save()
        Preguntas(num=9, texto="Pregunta 1 del tema 3 de Procesadores a desarrollar", asignatura=procesadores, tema=tema3, tipo=0, usuario=luisfer).save()
        Preguntas(num=10, texto="Pregunta 2 del tema 3 de Procesadores a desarrollar", asignatura=procesadores, tema=tema3, tipo=0, usuario=luisfer).save()
        Preguntas(num=11, texto="Pregunta 3 del tema 3 de Procesadores a desarrollar", asignatura=procesadores, tema=tema3, tipo=0, usuario=luisfer).save()
        Preguntas(num=12, texto="Pregunta 4 del tema 3 de Procesadores a desarrollar", asignatura=procesadores, tema=tema3, tipo=0, usuario=luisfer).save()

        Preguntas(num=1, texto="Pregunta 1 del tema 1 de Procesadores", asignatura=procesadores, tema=tema1, tipo=0, usuario=profe1).save()
        Preguntas(num=2, texto="Pregunta 2 del tema 1 de Procesadores", asignatura=procesadores, tema=tema1, tipo=0, usuario=profe1).save()
        Preguntas(num=3, texto="Pregunta 3 del tema 1 de Procesadores", asignatura=procesadores, tema=tema1, tipo=0, usuario=profe1).save()
        Preguntas(num=4, texto="Pregunta 4 del tema 1 de Procesadores", asignatura=procesadores, tema=tema1, tipo=0, usuario=profe1).save()
        Preguntas(num=5, texto="Pregunta 1 del tema 2 de Procesadores", asignatura=procesadores, tema=tema2, tipo=0, usuario=profe1).save()
        Preguntas(num=6, texto="Pregunta 2 del tema 2 de Procesadores", asignatura=procesadores, tema=tema2, tipo=0, usuario=profe1).save()
        Preguntas(num=7, texto="Pregunta 3 del tema 2 de Procesadores", asignatura=procesadores, tema=tema2, tipo=0, usuario=profe1).save()
        Preguntas(num=8, texto="Pregunta 4 del tema 2 de Procesadores", asignatura=procesadores, tema=tema2, tipo=0, usuario=profe1).save()
        Preguntas(num=9, texto="Pregunta 1 del tema 3 de Procesadores", asignatura=procesadores, tema=tema3, tipo=0, usuario=profe1).save()
        Preguntas(num=10, texto="Pregunta 2 del tema 3 de Procesadores", asignatura=procesadores, tema=tema3, tipo=0, usuario=profe1).save()
        """

# Initialize flask-login
def init_login(app):
    login_manager = login.LoginManager()
    login_manager.setup_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return Usuarios.objects(id=user_id).first()


@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username


@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/logout/')
def logout_view():
    login.logout_user()
    session.pop("usuario", None)
    return redirect(url_for('index'))

@app.route('/contact/')
def contact_view():
    return render_template('contact.html')

@app.route('/about/')
def about_view():
    return render_template('about.html')

#=========================================#
#    Error Handling                       #
#=========================================#
@app.errorhandler(404)
def error_not_found(error):
    return render_template('error/page_not_found.html'), 404

@app.route('/genexa', methods=('GET', 'POST'))
def genera_examen_view():
    """
    Función para la generación de exámenes de forma aleatoria
    """    
    form = GeneraExamenForm(request.form)   

    asig=login.current_user.get_asignaturas()    
    form.asignatura.choices = [(g.asignatura, g.asignatura) for g in asig]
    
    if request.method == 'POST' and form.validate():        
        asignatura = Asignaturas.objects(asignatura=form.asignatura.data).first()
        tipo = form.tipo_examen.data
        
        lista_preguntas = Preguntas.objects(asignatura= asignatura.get_id(), tipo=tipo)
        num_preguntas = form.num_preguntas.data
        nombre = form.nombre.data
        
        examen = Examenes(nombre=nombre, asignatura=asignatura, publico=form.publico.data, usuario=login.current_user.get_id())

        # Random mode    
        if form.modo.data==0:
            #modo = "aleatorio"            
            lista_preguntas = random.sample(lista_preguntas, num_preguntas)

        else:
            #modo = "preguntas por tema"
            lista = []
            lista_preguntas = []
            lista_temas = Temas.objects(asignatura = asignatura.get_id())
            num_temas = len(lista_temas)
            
            # Creo una lista de preguntas por tema
            for tema in lista_temas:
                preguntas = Preguntas.objects(asignatura= asignatura.get_id(), tipo=tipo, tema=tema)
                preguntas = random.sample(preguntas, len(preguntas))
                lista.append(preguntas)
            random.shuffle(lista)
            
            indice = 0  
            ind = 0
            while num_preguntas > 0:
                if len(lista[indice]) > 0:
                    lista_preguntas.insert(ind, lista[indice].pop())
                    ind = ind + 1

                    num_preguntas = num_preguntas -1
            
                if indice < num_temas-1:
                    indice = indice + 1
                else:
                    indice = 0
                                        
        examen.preguntas = lista_preguntas
        examen.save()

        return render_template('exams/gen_exa_ok.html', asignatura=asignatura, nombre=nombre, preguntas=lista_preguntas, tipo=tipo)
    return render_template('exams/gen_exa.html', form=form)


@app.route('/examenes', methods=('GET', 'POST'))
@app.route('/examenes/<asignatura>/<nombre>/<usuario>', methods=('GET', 'POST'))
def examenes_view(nombre=None, asignatura=None, usuario=None):
    exams = Examenes.public()
    
    if request.method == 'POST':
        if nombre:
            asig = Asignaturas.objects(asignatura=asignatura).first()        
            user = Usuarios.objects(usuario=usuario).first()
            exam = Examenes.public(asignatura=asig.get_id(), nombre=nombre, usuario=user).first()
            
            i = 1
            respuestas = []            
            for pregunta in exam.preguntas:
                pre = "pregunta" + str(i)
                
                if pregunta.tipo == 0:
                    respuestas.append(request.form[pre].strip())
                    pregunta.respuesta = request.form[pre].strip()
                    
                if pregunta.tipo == 1 or pregunta.tipo == 2:                  
                    if request.form.get(pre) <> None:
                        respuestas.append(request.form.get(pre))
                        pregunta.respuesta = request.form.get(pre)

                i = i + 1                   

            return render_template('exams/exam.html', exam=exam, respuestas=respuestas)
    
    if nombre:
        asig = Asignaturas.objects(asignatura=asignatura).first()        
        user = Usuarios.objects(usuario=usuario).first()
        exam = Examenes.public(asignatura=asig.get_id(), nombre=nombre, usuario=user).first()
        return render_template('exams/exam.html', exam=exam)
    else:        
        return render_template('exams/public_exam.html', exams = exams)

@app.route('/mi_cuenta', methods=('GET', 'POST'))
def cuenta_view():
    form = ProfileForm(request.form)   
    user = Usuarios.objects(id=login.current_user.get_id()).first()

    if request.method == 'POST':
        user.usuario = form.usuario.data
        user.nombre = form.nombre.data
        user.apellidos = form.apellidos.data
        user.password = form.password.data
        user.email = form.email.data
        save = False
        
        if form.validate():
            save = True
            user.save()
        return render_template("user/profile.html", user=user, form=form, save=save)

    return render_template('user/profile.html', user=user, form=form)


@app.route('/rec_pass', methods=('GET', 'POST'))
def rec_pass():
    if request.method == 'POST':            
        login = request.form["usuario"]

        if login:
            user = Usuarios.objects(usuario=login).first()
            if user:
                email = user.email
                if email:
                    passw = gen_passwd(8)
                    user.password = passw
                    user.save()
                    send_email(email, passw)                    
                    return render_template('user/rec_pass.html', email=email)
                else:
                    error = u"No ha introducido ningún email válido en su perfil"
            else:
                error = u"El usuario introducido no es válido"

        else:
            error = u"Debe introducir un usuario"

        return render_template("user/rec_pass.html", error=error)

    return render_template('user/rec_pass.html') 
    

@app.route('/export1', methods=('GET', 'POST'))
@app.route('/export1/<exam>', methods=('GET', 'POST'))
def export_odt(exam=None):
    
    # compruebo que se han pasado los datos del examen
    if not exam:
        showerror('Error', 'Datos insuficientes.')
        return None
    
    # Busco el objeto examen
    examen = Examenes.objects(id=exam).first()

    # Cuadro de dialogo para guardar el archivo
    archivo = asksaveasfilename(filetypes = [("Archivos ODT",".odt")])
    if not archivo:
        showinfo('Proceso cancelado', 'El proceso ha sido cancelado por el usuario.')
        return render_template('exams/exam.html', exam=examen)

    if request.method == 'POST':        
        exportODT(examen, archivo)
                
    showinfo('Archivo generado', 'El archivo ' + archivo + ' se ha generado correctamente.')
    return render_template('exams/exam.html', exam=examen)
    

@app.route('/export2/<exam>', methods=('GET', 'POST'))
def export_odt2(exam=None):
    
    # compruebo que se han pasado los datos del examen
    if not exam:
        showerror('Error', 'Datos insuficientes.')
        return None
    
    # Saco los datos del examen
    examen = Examenes.objects(id=exam).first()

    # Cuadro de dialogo para guardar el archivo
    file_odt = asksaveasfilename(filetypes = [("Archivos ODT",".odt")])
    if not file_odt:
        showinfo('Proceso cancelado', 'El proceso ha sido cancelado por el usuario.')
        return render_template('exams/exam.html', exam=examen)
        
        
    if request.method == 'POST':
        exportODT2(examen, file_odt)
                                   
        showinfo('Archivo generado', 'El archivo se ha generado correctamente.')
    
    return render_template('exams/exam.html', exam=examen)


@app.route('/export_pdf/<exam>', methods=('GET', 'POST'))
def export_pdf(exam=None):
    
    # compruebo que se han pasado los datos del examen
    if not exam:
        showerror('Error', 'Datos insuficientes.')
        return None

    # Saco los datos del examen
    examen = Examenes.objects(id=exam).first()

    # Cuadro de dialogo para guardar el archivo
    filePDF = asksaveasfilename(filetypes = [("Archivos PDF",".pdf")])
    if not filePDF:
        showinfo('Proceso cancelado', 'El proceso ha sido cancelado por el usuario.')
        return render_template('exams/exam.html', exam=examen)
        
    if request.method == 'POST':
        exportPDF(examen, filePDF)

    showinfo('Archivo generado', 'El archivo se ha generado correctamente.')
    return render_template('exams/exam.html', exam=examen)


def gen_passwd(n):
    """ 
    Generador de passwords 
    Usando choice para seleccionar una, la fuente de datos lo da string.letters
    Para usar tambien numeros, string.digits
    Extraido de: http://miguelangelnieto.net/?action=view&url=receta-generar-contrase%C3%B1as-aleatorias-en-python
    """
    return ''.join([random.choice(string.letters + string.digits) for i in range(n)])
    
def send_email(email, passw):
    msg = Message(
      'Contraseña cambiada correctamente',
       sender='educaweb.uned@gmail.com',
       recipients=[email])
    msg.body = u"Se ha creado una nueva contraseña de Educaweb para tu cuenta. La nueva contraseña es " + passw
    mail.send(msg)