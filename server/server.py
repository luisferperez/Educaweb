# -*- coding: utf-8 -*-
import config, random

from flask import Flask, request, render_template, redirect, session, url_for
from flask.ext import login
from flask.ext.mongoengine import MongoEngine

from models import Usuarios, Asignaturas, Temas, Preguntas, Examenes
from forms import GeneraExamenForm

#========================================#
#    Creation of the Web Application     #
#========================================#
app=Flask(__name__)
app.config.from_object(config)

db = MongoEngine()
db.init_app(app)

# Initialize ddbb
def init_ddbb():
    num = Usuarios.objects(login="admin").count()
    
    if num == 0:
        Usuarios(login="admin", password="educaweb", tipo=0, activado=True).save()    
        
        # Registros de prueba -- BORRAR EN PRODUCCIÓN
        #luisfer.save()        
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
        
        profe1 = Usuarios(login="profe1", password="profe1", tipo=1, activado=True, asignaturas={ss_oo, redes})
        profe1.save()

        luisfer = Usuarios(login="luisfer", password="luisfer", tipo=1, activado=True, asignaturas={procesadores, ia, leng})
        luisfer.save()
        
        Temas(num=1, descripcion="Introduccion a la IA", asignatura=ia, usuario=luisfer).save()
        
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

        return render_template('examen.html', asignatura=asignatura, nombre=nombre, preguntas=lista_preguntas, tipo=tipo)
    return render_template('gen_exa.html', form=form)


@app.route('/examenes', methods=('GET', 'POST'))
@app.route('/examenes/<nombre>', methods=('GET', 'POST'))
def examenes_view(nombre=None):
    exams = Examenes.public()
    
    if request.method == 'POST':
        if nombre:
            exam = Examenes.objects(nombre=nombre).first()
            return render_template('exams/exam.html', exam=exam)
        else:
            return render_template('examen.html')
    return render_template('public_exam.html', exams = exams)
