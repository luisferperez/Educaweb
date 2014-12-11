# -*- coding: utf-8 -*-
from flask import request, redirect, url_for
from flask.ext import admin, login
from flask.ext.admin.contrib.mongoengine import ModelView
from flask.ext.admin import Admin, expose, helpers

from models import Usuarios, Temas, Preguntas, Asignaturas, Examenes, Examenes_Resueltos
from forms import LoginForm, RegistrationForm


def initialize_admin_component(app):
    # Create admin
    admin = Admin(app, 'EducaWeb', index_view=MyAdminIndexView(), base_template='admin.html')
    # Add view
    admin.add_view(UserView(Usuarios))
    admin.add_view(AsignaturasView(Asignaturas))
    admin.add_view(TemasView(Temas))
    admin.add_view(PreguntasView(Preguntas))
    admin.add_view(MyView(Examenes))
#    admin.add_view(Exa_RView(Examenes_Resueltos))

# Create customized index view class
class MyAdminIndexView(admin.AdminIndexView):
    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated():
            return redirect(url_for('.index'))
        link = '<p>Si no dispone de cuenta de usuario <a href="' + url_for('.register_view') + '">Pulse aqu&iacute para registrarse.</a></p>'
        link = '<p>Si no recuerda su contraseña <a href="' + url_for('.register_view') + '">pulse aqu&iacute para reactivarla.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
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
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

class MyView(ModelView):   
    column_exclude_list = ("usuario")
    form_excluded_columns = ("usuario")

    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.is_activado() and login.current_user.is_profesor() 
        
class UserView(ModelView):
    column_exclude_list = ("password")
    form_excluded_columns = ("password")
    
    column_filters = ['login']
    
    column_searchable_list = ('login', 'email')

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
#    column_filters = (scaffold_filters(asignatura))
    column_labels = dict(nombre='Nombre', descripcion='Descripcion')
    column_default_sort = ('asignatura', 'num')


#    action_disallowed_list = ['delete']

class PreguntasView(MyView):
    
    column_default_sort =  ('asignatura', 'tema', 'num')

    column_choices = {
        'tipo': [
            (0, 'Desarrollo'), 
            (1, 'Test'),
            (2, 'Verdadero o Falso')
            
        ]
    }

class Exa_RView(ModelView):   
    column_exclude_list = ("usuario")
    form_excluded_columns = ("usuario")

    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.is_activado()
