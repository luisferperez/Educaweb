# -*- coding: utf-8 -*-
"""
@author: Luis Fdo. Pérez
@co-authors: Basis code obtained from the SCC Department,
             
Administration Panel
"""
from flask import request, redirect, url_for
from flask.ext import admin, login
from flask_admin.contrib.mongoengine import ModelView, filters
from flask.ext.admin import Admin, expose, helpers
from flask.ext.admin.form import rules

from models import Usuarios, Temas, Preguntas, Asignaturas, Examenes
from forms import LoginForm, RegistrationForm

#==============================================================#
# Initialization                                               #         
#==============================================================#
def initialize_admin_component(app):
    """ 
    Initialize the Admin Views. 
    """
    # Create admin interface
    admin = Admin(app, 'EducaWeb', index_view=MyAdminIndexView(), base_template='layout.html', template_mode='bootstrap3')
    # Add views
    admin.add_view(UserView(Usuarios))
    admin.add_view(AsignaturasView(Asignaturas))
    admin.add_view(TemasView(Temas))
    admin.add_view(PreguntasView(Preguntas))
    admin.add_view(MyView(Examenes))

#==============================================================#
# Create customized index view class                           #
#==============================================================#
class MyAdminIndexView(admin.AdminIndexView):
    """ 
    View that will be used as index for Admin. 
    """
    
    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        """ handle user login """
        
        # User login is performed through the form "LoginForm"        
        form = LoginForm(request.form)

        # if the form is validated, the login is done with the validated user
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            if user != None:
                login.login_user(user)

        # if the user login is correct, is redirected to the home page
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
        """ handle user register  """
        
        # User registration is performed through the form "RegistrationForm"
        form = RegistrationForm(request.form)

        # when the response is received and validated the form
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

#==============================================================#
# Base View                                                    #
#==============================================================#
class MyView(ModelView):
    """ 
    View that will be used as base for other views. 
    """
    # the "usuario" column is not displayed
    column_exclude_list = ("usuario")
    form_excluded_columns = ("usuario")

    # custom templates    
    list_template = 'admin/list.html'
    create_template = 'admin/create.html'
    edit_template = 'admin/edit.html'
    
    # these views only be accessible by teachers
    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.is_activado() and login.current_user.is_profesor() 
        

#==============================================================#
# Views for database collections                               #
#==============================================================#
class UserView(ModelView):
    """
    Users View. Entry view which lets us manage the users in the system.
    """
    # the "password" column is not displayed
    column_exclude_list = ("password")
    form_excluded_columns = ("password")
    
    # users can only be created by registration    
    can_create = False
    
    # custom templates
    list_template = 'admin/list.html'
    edit_template = 'admin/edit.html'
    
    # columns which can perform search filter
    column_filters = ['usuario', 'nombre']
    
    # fields in which the search is performed    
    column_searchable_list = ('nombre', 'usuario', 'email')

    # Choices for the column of the user type
    column_choices = {
        'tipo': [
            (0, 'Administrador'),
            (1, 'Profesor'),
            (2, 'Alumno')
        ]
    }

    # help text for some columns    
    column_descriptions = dict(
        usuario=u'Nombre de entrada a la aplicación',
        tipo=u'Administrador, profesor o alumno',
        activado=u'El usuario debe ser activado por el administrador para acceder a la aplicación')
    
    # this view is only accessible by administrators
    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.is_administrador()
        

class AsignaturasView(MyView):
    """
    Subjects View. Entry view which lets administrators manage the subjects in the system.
    """
    # columns which can perform search filter    
    column_filters = ['asignatura']
    
    # this view is only accessible by administrators
    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.is_activado() and login.current_user.is_administrador() 


class TemasView(MyView):
    """
    Chapters View. Entry view which lets teachers manage the chapters in the system.
    """
    # Custom labels for some columns
    column_labels = dict(num=u'Número', descripcion=u'Descripción')
    
    # default order for the records list
    column_default_sort = ('asignatura', 'num')

    # columns which can perform search filter    
    #column_filters = (filters.FilterLike(Asignaturas.asignatura, 'asignatura',), 'descripcion')
    
    #filters.FilterConverter()

class PreguntasView(MyView):
    """
    Questions View. Entry view which lets teachers manage the questions in the system.
    """
    column_exclude_list = ('usuario', 'verdadera', 'correcta')
    
    # default order for the records list        
    column_default_sort = ('asignatura', 'num')

    # help text for some columns
    column_descriptions = dict(
        asignatura='Asignatura a la que corresponde la pregunta',
        tipo='Preguntas a desarrollar, test o preguntas de tipo verdadero o falso')
    
    # fields in which the search is performed    
    column_searchable_list = ('texto',)

    # choices for the column of the question type
    column_choices = {
        'tipo': [
            (0, 'Desarrollo'), 
            (1, 'Test'),
            (2, 'Verdadero o Falso')
        ]
    }

    # options to show the subdocuments for column "opciones"
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