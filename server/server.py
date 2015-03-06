# -*- coding: utf-8 -*-
"""
@author: Luis Fdo. Pérez

"""
import config, random, string

from flask import Flask, request, render_template, redirect, session, url_for
from flask.ext import login
from flask.ext.mongoengine import MongoEngine
from flask.ext.mail import Mail, Message

from models import Usuarios, Asignaturas, Temas, Preguntas, Examenes, Opciones
from forms import GeneraExamenForm, ProfileForm
#from export import creaODT

from xml.dom.minidom import parseString
import zipfile, shutil

from tkFileDialog import asksaveasfilename
from tkMessageBox import showinfo, showerror

# Importo las librerias para el reportlab (exportación a pdf)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

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
    num = Usuarios.objects(login="admin").count()
    
    #creaODT()
    
    # Compruebo que no existe el usuario admin
    if num == 0:
        Usuarios(nombre="admin", login="admin", password="educaweb", email="admin@uned.es", tipo=0, activado=True).save()    
        
        # Registros de prueba -- BORRAR EN PRODUCCIÓN      
        procesadores = Asignaturas(asignatura="Procesadores del lenguaje")
        procesadores.save()        

        ss_oo = Asignaturas(asignatura="Sistemas Operativos")
        ss_oo.save()
       
        leng = Asignaturas(asignatura="Lenguajes de Programación")
        leng.save()
        
        ia = Asignaturas(asignatura="Inteligencia Artificial")
        ia.save()
        
        redes = Asignaturas(asignatura="Redes")
        redes.save()
        
        profe1 = Usuarios(nombre="profe1", login="profe1", password="profe1", email="profe1@uned.es", tipo=1, activado=True, asignaturas={ss_oo, redes, procesadores})
        profe1.save()

        luisfer = Usuarios(nombre = "luisfer", login="luisfer", password="luisfer", email="luifito@gmail.com", tipo=1, activado=True, asignaturas={procesadores, ia, leng})
        luisfer.save()
        
        # IA - preguntas Test
        tema1 = Temas(num=1, descripcion="Introduccion a la IA", asignatura=ia, usuario=luisfer).save()
        tema2 = Temas(num=2, descripcion="Logica", asignatura=ia, usuario=luisfer).save()
        tema3 = Temas(num=3, descripcion="Sistemas expertos", asignatura=ia, usuario=luisfer).save()
        opcion1 = Opciones(letra="A", texto="opcion A")
        opcion2 = Opciones(letra="B", texto="opcion B")
        Preguntas(num=1, texto="Pregunta 1 del tema 1 de IA", asignatura=ia, tema=tema1, tipo=1, opciones={opcion1, opcion2}, correcta="A", usuario=luisfer).save()
        Preguntas(num=2, texto="Pregunta 2 del tema 1 de IA", asignatura=ia, tema=tema1, tipo=1, opciones={opcion1, opcion2}, correcta="B", usuario=luisfer).save()
        Preguntas(num=3, texto="Pregunta 1 del tema 2 de IA", asignatura=ia, tema=tema2, tipo=1, opciones={opcion1, opcion2}, correcta="B", usuario=luisfer).save()
        Preguntas(num=4, texto="Pregunta 2 del tema 2 de IA", asignatura=ia, tema=tema2, tipo=1, opciones={opcion1, opcion2}, correcta="B", usuario=luisfer).save()
        Preguntas(num=5, texto="Pregunta 1 del tema 3 de IA", asignatura=ia, tema=tema3, tipo=1, opciones={opcion1, opcion2}, correcta="A", usuario=luisfer).save()
        Preguntas(num=6, texto="Pregunta 2 del tema 3 de IA", asignatura=ia, tema=tema3, tipo=1, opciones={opcion1, opcion2}, correcta="A", usuario=luisfer).save()
        
        # Redes - preguntas Verdadero o falso
        tema1 = Temas(num=1, descripcion="Redes LAN", asignatura=redes, usuario=luisfer).save()
        tema2 = Temas(num=2, descripcion="TCP/IP", asignatura=redes, usuario=luisfer).save()
        tema3 = Temas(num=3, descripcion="ADSL", asignatura=redes, usuario=luisfer).save()
        Preguntas(num=1, texto="Pregunta 1 del tema 1 de Redes", asignatura=redes, tema=tema1, tipo=2, verdadera=True, usuario=luisfer).save()
        Preguntas(num=2, texto="Pregunta 2 del tema 1 de Redes", asignatura=redes, tema=tema1, tipo=2, usuario=luisfer).save()
        Preguntas(num=3, texto="Pregunta 1 del tema 2 de Redes", asignatura=redes, tema=tema2, tipo=2, verdadera=True, usuario=luisfer).save()
        Preguntas(num=4, texto="Pregunta 2 del tema 2 de Redes", asignatura=redes, tema=tema2, tipo=2, usuario=luisfer).save()
        Preguntas(num=5, texto="Pregunta 1 del tema 3 de Redes", asignatura=redes, tema=tema3, tipo=2, verdadera=True, usuario=luisfer).save()
        Preguntas(num=6, texto="Pregunta 2 del tema 3 de Redes", asignatura=redes, tema=tema3, tipo=2, usuario=luisfer).save()

        # Procesadores - preguntas desarrollo        
        tema1 = Temas(num=1, descripcion="Introducción", asignatura=procesadores, usuario=luisfer)
        tema1.save()
        tema2 = Temas(num=2, descripcion="Analisis Lexico", asignatura=procesadores, usuario=luisfer)
        tema2.save()
        tema3 = Temas(num=3, descripcion="Analisis sintactico", asignatura=procesadores, usuario=luisfer)
        tema3.save()
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
            user = Usuarios.objects(login=usuario).first()
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

#            examen_resuelto = Examenes_Resueltos(nombre = exam.nombre, asignatura= exam.asignatura, preguntas = exam.preguntas)            
#            examen_resuelto.save()
            
            return render_template('exams/exam.html', exam=exam, respuestas=respuestas)
    
    if nombre:
        asig = Asignaturas.objects(asignatura=asignatura).first()        
        user = Usuarios.objects(login=usuario).first()
        exam = Examenes.public(asignatura=asig.get_id(), nombre=nombre, usuario=user).first()
        return render_template('exams/exam.html', exam=exam)
    else:        
        return render_template('exams/public_exam.html', exams = exams)

@app.route('/mi_cuenta', methods=('GET', 'POST'))
def cuenta_view():
    form = ProfileForm(request.form)   
    user = Usuarios.objects(id=login.current_user.get_id()).first()

    if request.method == 'POST':
        user.login = form.login.data
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
        login = request.form["login"]

        if login:
            user = Usuarios.objects(login=login).first()
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
    
    # Cuadro de dialogo para guardar el archivo
    archivo = asksaveasfilename(filetypes = [("Archivos ODT",".odt")])    
    #print archivo
    
    if request.method == 'POST':
        shutil.copy('server/static/plantilla.odt', archivo)
        myfile = zipfile.ZipFile(archivo, 'a')
        ostr = myfile.read('content.xml', 'w')
    
        # Saco los datos del examen
        if exam:
            examen = Examenes.objects(id=exam).first()
            asignatura = examen.asignatura
            nombre = examen.nombre
            preguntas = examen.preguntas
    
        doc = parseString(ostr)
        paras = doc.getElementsByTagName('text:p')
        text_in_paras = []
        for p in paras:
            print "p.data:" +  str(p.nodeName)
            for ch in p.childNodes:
                if ch.nodeType == ch.TEXT_NODE:
                    text_in_paras.append(ch.data)
                    if ch.data.count('Asignatura') > 0:
                        print "Encontrada asignatura"
                        ch.data = ch.data + " " + str(asignatura)
                        nuevo_nodo = ch
                        p.appendChild(nuevo_nodo)
                    elif ch.data.count('Examen') > 0:
                        ch.data = ch.data + " " + str(nombre)
                        nuevo_nodo = ch
                        p.appendChild(nuevo_nodo)
                    elif ch.data.count('Preguntas') > 0:
                        i = 1                        
                        for pregunta in preguntas:                                     
                            """
                            nodo = doc.createTextNode(str(pregunta.texto))                        
                            p.appendChild(nodo)
                            #p.insertBefore(nodo, None)
                            
                            ch.data = str(pregunta.texto)
                            nuevo_nodo = ch
                            p.appendChild(nuevo_nodo)
                            """  
                                                        
                            x = doc.createElement("text:p")  
                            txt = doc.createTextNode(str(i) + ".- " + str(pregunta.texto))  
                            x.appendChild(txt)  # results in <foo>hello, world!</foo>
                            doc.childNodes[0].childNodes[3].childNodes[0].appendChild(x)
                            i = i + 1

                            x = doc.createElement("text:p")
                            doc.childNodes[0].childNodes[3].childNodes[0].appendChild(x)
                            
                            

        myfile.writestr('content.xml', doc.toprettyxml())
        myfile.close()
        
        #prueba para crear un xml
        fd = open('content.xml','w')
        doc.writexml(fd)
        doc.unlink()
        fd.close()
       
                        
    showinfo('Archivo generado', 'El archivo se ha generado correctamente.')
    return render_template('exams/exam.html', exam=examen)


@app.route('/export2/<exam>', methods=('GET', 'POST'))
def export_odt2(exam=None):
    
    # compruebo que se han pasado los datos del examen
    if not exam:
        showerror('Error', 'Datos insuficientes.')
        return None
    
    # Saco los datos del examen
    examen = Examenes.objects(id=exam).first()
    asignatura = examen.asignatura
    nombre = examen.nombre
    preguntas = examen.preguntas

    # Cuadro de dialogo para guardar el archivo
    archivo = asksaveasfilename(filetypes = [("Archivos ODT",".odt")])
    if not archivo:
        showinfo('Proceso cancelado', 'El proceso ha sido cancelado por el usuario.')
        return render_template('exams/exam.html', exam=examen)
        
        
    if request.method == 'POST':
        shutil.copy('server/static/formatos.odt', archivo)
        myfile = zipfile.ZipFile(archivo, 'a')
        ostr = myfile.read('content.xml', 'w')
    
        doc = parseString(ostr)
        paras = doc.getElementsByTagName('office:text')

        encontrado = False        
        
        for p in paras:
            for ch in p.childNodes:
                if ch.nodeName == "text:p" and encontrado == False: 
                    x = doc.createElement("text:p")
                    txt = doc.createTextNode(str(asignatura))
                    x.appendChild(txt)
                    x.setAttribute("text:style-name", "P1")
                    p.appendChild(x)
                    
                    x = doc.createElement("text:p")
                    p.appendChild(x)

                    x = doc.createElement("text:p")
                    txt = doc.createTextNode(str(nombre))
                    x.appendChild(txt)
                    x.setAttribute("text:style-name", "P2")
                    p.appendChild(x)

                    x = doc.createElement("text:p")
                    p.appendChild(x)

                    i = 1                        
                    for pregunta in preguntas:                      
                        x = doc.createElement("text:p")
                        txt = doc.createTextNode(str(i) + ".- " + str(pregunta.texto))  
                        x.appendChild(txt)
                        p.appendChild(x)
                        
                        # Para las preguntas tipo test
                        if pregunta.tipo == 1:
                            for opcion in pregunta.opciones:
                                x = doc.createElement("text:p")
                                
                                texto = opcion.letra + "). " + opcion.texto
                                txt = doc.createTextNode(texto)
                                x.appendChild(txt)
                                p.appendChild(x)
                                            
                        # Para las preguntas tipo verdadero o falso
                        elif pregunta.tipo == 2:
                            x = doc.createElement("text:p")
                            txt = doc.createTextNode("A).- Verdadero")
                            x.appendChild(txt)
                            p.appendChild(x)

                            x = doc.createElement("text:p")
                            txt = doc.createTextNode("B).- Falso")
                            x.appendChild(txt)
                            p.appendChild(x)

                        x = doc.createElement("text:p")
                        p.appendChild(x)
                        x = doc.createElement("text:p")
                        p.appendChild(x)

                        i = i + 1
                        
                    encontrado = True
                    
        """
        #prueba para crear un xml
        fd = open('content.xml','w')
        doc.writexml(fd, encoding='latin1')
        doc.unlink()
        fd.close()
        """
        
        myfile.writestr('content.xml', doc.toprettyxml(encoding='utf-8'))
        myfile.close()                
        
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
    asignatura = examen.asignatura
    nombre = examen.nombre
    preguntas = examen.preguntas

    # Cuadro de dialogo para guardar el archivo
    archivo = asksaveasfilename(filetypes = [("Archivos PDF",".pdf")])
    if not archivo:
        showinfo('Proceso cancelado', 'El proceso ha sido cancelado por el usuario.')
        return render_template('exams/exam.html', exam=examen)
        
    if request.method == 'POST':
        story = []
        styles=getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Cabecera', alignment=TA_CENTER, fontSize=16))
        styles.add(ParagraphStyle(name='Titulo', fontSize=12))
        
        doc=SimpleDocTemplate(archivo)

        # Introduzco el nombre de la asignatura
        para = Paragraph("<u><b>"+str(asignatura)+"</b></u>", styles['Cabecera'])
        story.append(para)
        story.append(Spacer(0,20))
        
        # Introduzco el nombre del examen
        para = Paragraph("<u>"+str(nombre)+"</u>", styles['Titulo'])
        story.append(para)
        story.append(Spacer(0,20))

        # Introduzco las preguntas del examen  
        i = 1         
        for pregunta in preguntas:
            texto = str(i) + ".- " + str(pregunta.texto)
            story.append(Paragraph(texto, styles["Normal"]))
            
            i = i + 1
            
            # Para las preguntas tipo test
            if pregunta.tipo == 1:
                story.append(Spacer(0,7))
                for opcion in pregunta.opciones:
                    texto = opcion.letra + ").- " + opcion.texto
                    story.append(Paragraph(texto, styles["Normal"]))
                    story.append(Spacer(0,7))
            
            # Para las preguntas tipo verdadero o falso
            elif pregunta.tipo == 2:
                texto = "A).- Verdadero"
                story.append(Paragraph(texto, styles["Normal"]))
                texto = "B).- Falso"
                story.append(Paragraph(texto, styles["Normal"]))

            
            story.append(Spacer(0,40))
        doc.build(story)


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