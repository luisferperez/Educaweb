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
from tkFileDialog import asksaveasfilename
from tkMessageBox import showinfo, showerror
from mongoengine import OperationError

from models import Usuarios, Asignaturas, Temas, Preguntas, Examenes, Opciones
from forms import GeneraExamenForm, ProfileForm
from export import exportODT, exportODT2, exportPDF

#========================================#
#    Creation of the Web Application     #
#========================================#
app=Flask(__name__)
app.config.from_object(config)

# Initialize the MongoDB database
db = MongoEngine()
db.init_app(app)

# Initialize the application to send mails
mail = Mail(app)

# Initialize ddbb
def init_ddbb():
    # Check that the admin user not exist
    num = Usuarios.objects(usuario="admin").count()

    if num == 0:        
        # the "admin" user is saved as a teacher and a student test
        admin = Usuarios(nombre="admin", apellidos="", usuario="admin", password="educaweb", email="admin@uned.es", tipo=0, activado=True)
        admin.save(clean=False)
        profe = Usuarios(nombre="profesor", apellidos="", usuario="profesor1", password="profe1", email="profesor1@uned.es", tipo=1, activado=True)
        profe.save(clean=False)
        alumno = Usuarios(nombre="alumno", apellidos="", usuario="alumno1", password="alumno1", email="alumno1@uned.es", tipo=2, activado=True)
        alumno.save(clean=False)

        # test records    
        asignaturas = ["Seguridad en las comunicaciones", "Procesadores del lenguaje", "Sistemas Operativos", "Inteligencia Artificial", "Redes", "Sistemas Distribuidos"]
      
        temas = [ 
            (u"El problema de la seguridad", u"La seguridad en los elementos físicos", u"Defensa básica ante ataques"),
            (u"Introducción", u"Analisis Lexico", u"Analisis sintáctico"), 
            (u"Fundamentos de los SO", u"Sistemas Operativos multitarea"),
            (u"Introducción a la IA", u"Lógica", u"Sistemas Expertos"), 
            (u"Redes LAN", "TCP/IP", "ADSL"), 
            (u"Fundamentos de los S.D.", u"Comunicación entre procesos" )
            ]
            
        opcion1 = Opciones(letra="A", texto="opcion A")
        opcion2 = Opciones(letra="B", texto="opcion B")
        op_seg1 = Opciones(letra="A", texto=u"Se debe comprar las mejores herramientas de seguridad disponibles en el mercado y formar a todo el personal en su uso")
        op_seg2 = Opciones(letra="B", texto=u"Se debe contratar al hacker de más prestigio de la comunidad informática y hacerle responsable de la seguridad")
        op_seg3 = Opciones(letra="C", texto=u"Se debe confiar en la suerte y hacer lo que pueda")
        op_seg4 = Opciones(letra="D", texto=u"No hay manera de evitarlos completamente")
        op_seg5 = Opciones(letra="A", texto=u"Debe ser completamente secreta, excepto para un grupo de élite")
        op_seg6 = Opciones(letra="B", texto=u"Debe incluir mecanismos de respuesta, frente a posibles ataques")
        op_seg7 = Opciones(letra="C", texto=u"Debe conseguir que los usuarios no tengan que conocerla")
        op_seg8 = Opciones(letra="D", texto=u"Debe cubrir solo los aspectos de sistemas operativos de la organización")
        op_seg9 = Opciones(letra="A", texto=u"Un sistema que permite, en tiempo real, detectar determinados tipos de ataques y alertar sobre ellos, a la vez que, en algunos casos, puede pararlos.")
        op_seg10 = Opciones(letra="B", texto=u"Un sistema cerrado de TV, que consigue detectar a cualquier ladrón informático que trate de penetrar en la organización.")
        op_seg11 = Opciones(letra="C", texto=u"Un sistema de localización de posibles atacantes en internet.")
        op_seg12 = Opciones(letra="D", texto=u"Un sistema que permite conocer cualquier envío no deseado de información por las redes de comunicaciones.")
        
        op_seg13 = Opciones(letra="A", texto=u"Porque implementan hasta el nivel 3 de la arquitectura OSI, y los hubs solo hasta el nivel 1.")
        op_seg14 = Opciones(letra="B", texto=u"No son necesariamente más seguros. Depende de su configuración concreta.")
        op_seg15 = Opciones(letra="C", texto=u"Tienen mecanismos físicos de seguridad adicionales.")
        op_seg16 = Opciones(letra="D", texto=u"Son más seguros los hubs, al no tener ninguna configuración especial que hacer en ellos.")
        op_seg17 = Opciones(letra="A", texto=u"Redes locales montadas en secreto, basándose en técnicas criptográficas secretas.")
        op_seg18 = Opciones(letra="B", texto=u"Grupos de ordenadores, relacionados lógicamente entre sí, por un número de grupo (o de VLAN) y configurados por el administrador de un conmutador.")
        op_seg19 = Opciones(letra="C", texto=u"Grupos de ordenadores en distintas redes IP, en distintas situaciones geográficas, dependientes de distintos encaminadores y conmutadores.")
        op_seg20 = Opciones(letra="D", texto=u"Un nuevo desarrollo de seguridad, probado únicamente como piloto, en el MIT.")
        op_seg21 = Opciones(letra="A", texto=u"Acceder a él mediante ssh o telnet, que ofrece, además, las mejores prestaciones de velocidad.")
        op_seg22 = Opciones(letra="B", texto=u"Acceder a él mediante http, al poderse usar criptografía SSL.")
        op_seg23 = Opciones(letra="C", texto=u"Depende en cada caso cómo esté configurado. No hay una solución claramente más segura que otra.")
        op_seg24 = Opciones(letra="D", texto=u"No puede accederse remotamente.")
        op_seg25 = Opciones(letra="A", texto=u"El programa que controla toda la seguridad del sistema operativo.")
        op_seg26 = Opciones(letra="B", texto=u"El nombre que recibe el centro físico del ordenador.")
        op_seg27 = Opciones(letra="C", texto=u"La parte del sistema operativo que controla la administración de recursos.")
        op_seg28 = Opciones(letra="D", texto=u"Una nueva aplicación de seguridad para Windows.")
        op_seg29 = Opciones(letra="A", texto=u"Verdadero, hoy en día cualquiera puede hacerlo.")
        op_seg30 = Opciones(letra="B", texto=u"Falso, depende de qué sistema de ficheros. Por ejemplo, FAT no puede hacerlo.")
        op_seg31 = Opciones(letra="C", texto=u"Falso, el sistema de ficheros nunca se ocupa de estos asuntos.")
        op_seg32 = Opciones(letra="D", texto=u"Verdadero, pero además, depende de la gestión de usuarios.")
        op_seg33 = Opciones(letra="A", texto=u"4 clases distintas: sólo IP, mensajes de aplicaciones con transporte TCP, de aplicaciones con transporte UDP y de protocolos del mismo nivel 3.")
        op_seg34 = Opciones(letra="B", texto=u"3 clases distintas: mensajes de aplicaciones con transporte TCP, de aplicaciones con transporte UDP y de protocolos del mismo nivel 3.")
        op_seg35 = Opciones(letra="C", texto=u"2 clases distintas: mensajes de aplicaciones con transporte TCP y de aplicaciones con transporte UDP.")
        op_seg36 = Opciones(letra="D", texto=u"Muchas clases distintas, dependiendo de la aplicación y el protocolo de encaminamiento.")

        preguntas = [
            (
                (   (u"Para evitar completamente cualquier tipo de ataque informático a los sistemas:", 1, (op_seg1, op_seg2, op_seg3, op_seg4), "D"),
                    (u"La política de seguridad de una organización debe tener alguna de las siguientes características:", 1, (op_seg5, op_seg6, op_seg7, op_seg8), "B"),
                    (u"En el contexto de seguridad de las comunicaciones, un sistema de detección de intrusiones es:", 1, (op_seg9, op_seg10, op_seg11, op_seg12), "A"),
                ),
                (   (u"Los encaminadores son máquinas más seguras que los hubs por:", 1, (op_seg13, op_seg14, op_seg15, op_seg16), "D"),
                    (u"Las VLAN (redes de área local virtuales) son:", 1, (op_seg17, op_seg18, op_seg19, op_seg20), "B"),
                    (u"Para la gestión remota de un encaminador o de un conmutador siempre es más seguro:", 1, (op_seg21, op_seg22, op_seg23, op_seg24), "C"),
                ),
                (   (u"El kernel del sistema operativo es:", 1, (op_seg25, op_seg26, op_seg27, op_seg28), "C"),
                    (u"La seguridad de los datos frente a accesos no autorizados la garantiza cualquier sistema de ficheros de cualquier sistema operativo:", 1, (op_seg29, op_seg30, op_seg31, op_seg32), "B"),
                    (u"Los mensajes IP pueden ser de:", 1, (op_seg33, op_seg34, op_seg35, op_seg36), "B"),
                )
            ),
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
                (   ("pregunta 1 Sist. Dist. - fundamentos", 1, (opcion1, opcion2), "B"),
                    ("pregunta 2 Sist. Dist. - fundamentos", 1, (opcion1, opcion2), "A")
                ),
                (   ("pregunta 1 Sist. Dist. - Com. entre procesos", 1, (opcion1, opcion2), "A"),
                    ("pregunta 2 Sist. Dist. - Com. entre procesos", 1, (opcion1, opcion2), "B")
                )
            )
            ]

        lista_asignaturas = []
        for i in range(len(asignaturas)):
            asignatura = Asignaturas()
            asignatura.asignatura = asignaturas[i]
            asignatura.save()

            lista_asignaturas.append(asignatura)

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
                            pregunta.opciones.append(opcion)
                        pregunta.correcta = preguntas[i][j][k][3]
                    
                    if pregunta.tipo == 2:
                        pregunta.verdadera = preguntas[i][j][k][2]
                        
                    pregunta.asignatura = asignatura
                    pregunta.usuario = profe
                    pregunta.save()
                    
                    num_pregunta = num_pregunta + 1

        profe.asignaturas = lista_asignaturas
        profe.save(clean=False)
        alumno.asignaturas = lista_asignaturas
        alumno.save(clean=False)
        
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

#==================================================#
#  Initialize Flask-Login to handle user sessions  #
#==================================================#
def init_login(app):
    login_manager = login.LoginManager()
    login_manager.setup_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return Usuarios.objects(id=user_id).first()

#=========================================#
#    Error Handling                       #
#=========================================#
@app.errorhandler(404)
def error_not_found(error):
    return render_template('error/page_not_found.html'), 404

@app.errorhandler(OperationError)
def error_mongo(e):
    msg_error = u'El documento no puede ser borrado por existir otros documentos relacionados.'
    return render_template('error/error_msg.html', error=msg_error)


#==========================================#
#    Web Routes                            #
#==========================================#
@app.route('/')
def index():
    """ View to show the home page. """
    return render_template('index.html')
    
@app.route('/logout/')
def logout_view():
    """ Logging out the current session. """
    login.logout_user()
    session.pop("usuario", None)
    return redirect(url_for('index'))

@app.route('/contact/')
def contact_view():
    """ View to show the contact page. """
    return render_template('contact.html')

@app.route('/about/')
def about_view():
    """ View to show the about page. """
    return render_template('about.html')

@app.route('/genexa', methods=('GET', 'POST'))
def genera_examen_view():
    """
    Function for generating random tests
    """    
    form = GeneraExamenForm(request.form)   

    asig=login.current_user.get_asignaturas()
    if not asig:
        msg_error = u"El usuario no tiene actualmente asignada ninguna asignatura, por lo que no \
        es posible generar exámenes de forma automática."
        return render_template('error/error_msg.html', error=msg_error)
    form.asignatura.choices = [(g.asignatura, g.asignatura) for g in asig]
    
    # the form  has already completed    
    if request.method == 'POST' and form.validate():        
        asignatura = Asignaturas.objects(asignatura=form.asignatura.data).first()
        tipo = form.tipo_examen.data
        
        lista_preguntas = Preguntas.objects(asignatura= asignatura.get_id(), tipo=tipo)
        num_preguntas = form.num_preguntas.data
        nombre = form.nombre.data
        
        examen = Examenes(nombre=nombre, asignatura=asignatura, publico=form.publico.data, usuario=login.current_user.get_id())

        # Random mode    
        if form.modo.data==0:
            # the necessary questions randomly selected from the list of questions            
            lista_preguntas = random.sample(lista_preguntas, num_preguntas)

        # mode = "questions by chapter"
        else:
            lista = []
            lista_preguntas = []
            lista_temas = Temas.objects(asignatura = asignatura.get_id())
            num_temas = len(lista_temas)
            
            # A list of questions is created for each chapter and randomly rearranges
            # and are included as well in another list
            for tema in lista_temas:
                preguntas = Preguntas.objects(asignatura= asignatura.get_id(), tipo=tipo, tema=tema)
                preguntas = random.sample(preguntas, len(preguntas))
                lista.append(preguntas)
            random.shuffle(lista)
            
            # Questions are selected from the random list until the total number needed
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
        examen.save(clean=False)

        return render_template('exams/gen_exa_ok.html', asignatura=asignatura, nombre=nombre, preguntas=lista_preguntas, tipo=tipo)
    
    # the form is displayed to complete
    return render_template('exams/gen_exa.html', form=form)


@app.route('/examenes', methods=('GET', 'POST'))
@app.route('/examenes/<export>', methods=('GET', 'POST'))
@app.route('/examenes/<asignatura>/<nombre>/<usuario>', methods=('GET', 'POST'))
def examenes_view(nombre=None, asignatura=None, usuario=None, export=None):
    """
    the list of exams is shown for both the export menu and the menu to perform exams    
    """
    exams = Examenes.public()
    
    if request.method == 'POST':
        # the corrected exam is displayed        
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
            
    # if we pass to the function an exam name, displays the full exam
    if nombre:
        asig = Asignaturas.objects(asignatura=asignatura).first()        
        user = Usuarios.objects(usuario=usuario).first()
        exam = Examenes.public(asignatura=asig.get_id(), nombre=nombre, usuario=user).first()
        return render_template('exams/exam.html', exam=exam)
    # the complete list of exams are shown    
    else:        
        return render_template('exams/public_exam.html', exams=exams, export=export)

@app.route('/mi_cuenta', methods=('GET', 'POST'))
def cuenta_view():
    """
    Function to display the form that allows to query and modify the user profile
    """        
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
            user.save(clean=False)
        return render_template("user/profile.html", user=user, form=form, save=save)

    return render_template('user/profile.html', user=user, form=form)


@app.route('/rec_pass', methods=('GET', 'POST'))
def rec_pass():
    """
    Function which displays the form to retrieve the user's password.
    """            
    if request.method == 'POST':            
        login = request.form["usuario"]

        if login:
            user = Usuarios.objects(usuario=login).first()
            if user:
                email = user.email
                if email:
                    passw = gen_passwd(8)
                    user.password = passw
                    user.save(clean=False)
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
    
@app.route('/export_odt/<modo>/<exam>', methods=('GET', 'POST'))
@app.route('/export_odt/<modo>/<template>/<exam>', methods=('GET', 'POST'))
def export_odt(exam=None, template=None, modo=None):
    """
    Function which allows to export an exam to a odt file.
    """
    # it checks that have passed the exam data
    if not exam:
        showerror('Error', 'Datos insuficientes.')
        return None
    
    # seeking the exam object
    examen = Examenes.objects(id=exam).first()

    # the dialog box is shown to save the file
    archivo = asksaveasfilename(filetypes = [("Archivos ODT",".odt")])
    if archivo:
        if modo == '1':
            exportODT(examen, archivo)
        else:
            exportODT2(examen, archivo)
        showinfo('Archivo generado', 'El archivo ' + archivo + ' se ha generado correctamente.')
    else:
        showinfo('Proceso cancelado', 'El proceso ha sido cancelado por el usuario.')

    if template:
        exams = Examenes.public()
        return render_template('exams/public_exam.html', exams=exams, export='export')
    else:    
        return render_template('exams/exam.html', exam=examen)


@app.route('/export_pdf/<exam>', methods=('GET', 'POST'))
@app.route('/export_pdf/<template>/<exam>', methods=('GET', 'POST'))
def export_pdf(exam=None, template=None):
    """
    Function which allows to export an exam to a pdf file.
    """
    # it checks that have passed the exam data
    if not exam:
        showerror('Error', 'Datos insuficientes.')
        return None

    # extract exam data
    examen = Examenes.objects(id=exam).first()

    # the dialog box is shown to save the file
    filePDF = asksaveasfilename(filetypes = [("Archivos PDF",".pdf")])
    if filePDF:
        exportPDF(examen, filePDF)
        showinfo('Archivo generado', 'El archivo se ha generado correctamente.')
    else:
        showinfo('Proceso cancelado', 'El proceso ha sido cancelado por el usuario.')
        
    if template:
        exams = Examenes.public()
        return render_template('exams/public_exam.html', exams=exams, export='export')
    else:    
        return render_template('exams/exam.html', exam=examen)

def gen_passwd(n):
    """ 
    Password generator extracted from:
    http://miguelangelnieto.net/?action=view&url=receta-generar-contrase%C3%B1as-aleatorias-en-python
    """
    return ''.join([random.choice(string.letters + string.digits) for i in range(n)])
    
def send_email(email, passw):
    """
    Function to send an email to reset the password.
    """
    msg = Message(
      'Contraseña cambiada correctamente',
       sender='educaweb.uned@gmail.com',
       recipients=[email])
    msg.body = u"Se ha creado una nueva contraseña de Educaweb para tu cuenta. La nueva contraseña es " + passw
    mail.send(msg)