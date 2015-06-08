# -*- coding: utf-8 -*-
"""
@author: Luis Fdo. Pérez
@co-authors: Basis code obtained from the SCC Department,
             
Administration Panel
"""
from flask import request, redirect, url_for
from flask.ext import admin, login
from flask_admin.contrib.mongoengine import ModelView
#from flask.ext.admin.contrib.mongoengine import ModelView
from flask.ext.admin import Admin, expose, helpers

from models import Usuarios, Temas, Preguntas, Asignaturas, Examenes
from forms import LoginForm, RegistrationForm


from flask.ext.admin.form import rules
#==============================================================================
# Initialization
#==============================================================================
def initialize_admin_component(app):
    """ Initialize the Admin Views. """
    # Create admin
    admin = Admin(app, 'EducaWeb', index_view=MyAdminIndexView(), base_template='layout.html', template_mode='bootstrap3')
    # Add views
    admin.add_view(UserView(Usuarios))
    admin.add_view(AsignaturasView(Asignaturas))
    admin.add_view(TemasView(Temas))
    admin.add_view(PreguntasView(Preguntas))
    admin.add_view(MyView(Examenes))

#==============================================================================
# Create customized index view class
#==============================================================================
class MyAdminIndexView(admin.AdminIndexView):
    """ View that will be used as index for Admin. """
    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        #if request.method == 'POST' and form.validate():
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            if user != None:
                login.login_user(user)

        if login.current_user.is_authenticated():
            return redirect(url_for('index'))
        link = '<p>Si no dispone de cuenta de usuario <a href="' + url_for('.register_view') + '">Pulse aqu&iacute para registrarse.</a></p>'
        link2 = u'<p>Si no recuerda su contraseña <a href="' + url_for('rec_pass') + '">pulse aqu&iacute para reactivarla.</a></p>'        
        self._template_args['form'] = form
        self._template_args['legend'] = u"Entrada a la aplicación"
        self._template_args['link'] = link
        self._template_args['link2'] = link2
        return super(MyAdminIndexView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if request.method == 'POST' and form.validate():
            user = Usuarios()

            form.populate_obj(user)
            user.save()

            login.login_user(user)
            return redirect(url_for('.index'))

        link = '<p>Si ya tiene una cuenta de usuario <a href="' + url_for('.login_view') + '">Pulse aqu&iacute para iniciar sesi&oacuten.</a></p>'
        self._template_args['form'] = form
        self._template_args['legend'] = "Nuevo usuario"
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

#==============================================================================
# Base View
#==============================================================================
class MyView(ModelView):
    """ View that will be used as base for other views. """
    # the "usuario" column is not displayed
    column_exclude_list = ("usuario")
    form_excluded_columns = ("usuario")

    list_template = 'admin/list.html'
    create_template = 'admin/create.html'
    edit_template = 'admin/edit.html'
    
    # these views only be accessible by teachers
    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.is_activado() and login.current_user.is_profesor() 
        

#==============================================================================
# Views for database collections
#==============================================================================
class UserView(ModelView):
        
    # the "password" column is not displayed
    column_exclude_list = ("password")
    form_excluded_columns = ("password")
    
    column_filters = ['usuario']
    
    column_searchable_list = ('usuario', 'email')

    column_choices = {
        'tipo': [
            (0, 'Administrador'),
            (1, 'Profesor'),
            (2, 'Alumno')
        ]
    }
    """
    form_overrides = dict(tipo=SelectField)
    form_args = dict(
        # Pass the choices to the `SelectField`
        tipo=dict(
            choices=[(0, 'administrador'), (1, 'profesor'), (2, 'alumno')]
        ))
        """    
    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.is_administrador()

class AsignaturasView(MyView):

    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.is_activado() and login.current_user.is_administrador() 
"""      
    def init_actions(self):
        if login.current_user.is_profesor():
            print "Hola, profe"
            
    ""    form_ajax_refs = {
        'usuario': {
            'fields': ['login']
        }
    }
    """    

class TemasView(MyView):
    column_labels = dict(nombre='Nombre', descripcion='Descripcion')
    column_default_sort = ('asignatura', 'num')


class PreguntasView(MyView):
    #column_exclude_list = ("respuesta", "opciones")
    
    #column_default_sort = ('asignatura', 'tema', 'num')

    # Choices for the "tipo" column
    column_choices = {
        'tipo': [
            (0, 'Desarrollo'), 
            (1, 'Test'),
            (2, 'Verdadero o Falso')
            
        ]
    }

    form_subdocuments = {
        'opciones': {
            'form_subdocuments': {
                None: {
                    # Add <hr> at the end of the form
                    'form_rules': ('letra', 'texto', rules.HTML('<hr>')),
                    'form_widget_args': {
                        'name': {
                            'style': 'color: red'
                        }
                    }
                }
            }
        }
    }
