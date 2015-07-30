# -*- coding: utf-8 -*-
"""
@author: Luis Fdo. Pérez
@co-authors: Basis code obtained from the SCC Department

Forms to render HTML inputs & validate request data
"""
# Define login and registration forms (for flask-login)
from wtforms import form, fields, validators

from models import Usuarios, Preguntas, Asignaturas, Examenes

class LoginForm(form.Form):
    """ 
    Form used to log the user in the application. 
    """
    usuario = fields.TextField(validators=[validators.required(u'Debe introducir el nombre de usuario.')])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_password(self, field):
        """ Function to validate the password """        
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('El usuario no es valido')

        if user.password != self.password.data:
            raise validators.ValidationError('El password no es correcto')

    def get_user(self):
        return Usuarios.objects(usuario=self.usuario.data).first()


class RegistrationForm(form.Form):
    """    
    Form used to perform user registration in the application.
    """
    nombre = fields.TextField(validators=[validators.required(u'El nombre no puede estar vacío.')])
    apellidos = fields.TextField()
    usuario = fields.TextField(validators=[validators.required(u'Debe introducir un nombre de usuario.')])
    email = fields.TextField(validators=[validators.required(u'El campo email es obligatorio'), validators.Email(u'El email insertado no es válido.')])
    password = fields.PasswordField(validators=[validators.DataRequired(u'El campo de la contraseña no puede estar vacío'), validators.EqualTo('confirm', message=u'Las contraseñas deben coincidir')])
    confirm = fields.PasswordField('Repeat Password')

    def validate_usuario(self, field):
        """ Function to validate the user """        
        if Usuarios.objects(usuario=self.usuario.data):
            raise validators.ValidationError('El nombre de usuario ya existe en el sistema.')

class GeneraExamenForm(form.Form):
    """    
    Form used for entering data for automatically generating tests.
    """
    TIPO = ((0, 'Desarrollo'), (1, 'Test'),(2, 'Verdadero o Falso'))
    MODO = ((0, 'Aleatorio'), (1, 'Preguntas por tema'))

    nombre = fields.StringField('Nombre', [validators.required(u'Es necesario escribir un nombre para el examen')])
    asignatura = fields.SelectField('Asignatura:', [validators.required(u'Es necesario introducir la asignatura del examen.')])
    tipo_examen = fields.SelectField('Tipo de Examen:', coerce=int, choices=TIPO)
    num_preguntas = fields.IntegerField(u'Número de preguntas:', [validators.required(u'Debe especificar el número de preguntas que tendrá el examen')])
    modo = fields.SelectField('Modo de examen:', coerce=int, choices=MODO)
    publico = fields.BooleanField(u'¿Desea hacer público el examen?')
    
    def validate_nombre(self, field):
        """ Function to validate that the name of the exam has not been used for the same subject """
        asignatura = Asignaturas.objects(asignatura=self.asignatura.data).first()        
        if Examenes.objects(nombre=self.nombre.data, asignatura=asignatura):
            raise validators.ValidationError(u'El nombre del examen ya ha sido usado')

    def validate_num_preguntas(self, field):
        """ Function to verify that there are enough questions of the subject and type given to generate the exam """
        asignatura = Asignaturas.objects(asignatura=self.asignatura.data).first()
        tipo = self.tipo_examen.data
        num_preguntas = self.num_preguntas.data
        preguntas = Preguntas.objects(asignatura=asignatura.get_id(), tipo=tipo).count()
        if preguntas < num_preguntas:
            raise validators.ValidationError(u'No existen suficientes preguntas de la asignatura para el tipo indicado.')

    def get_tipo(self):
        return self.TIPO[self.tipo_examen.data][1:1]

class ProfileForm(form.Form):
    """    
    Form used for the modification of user profile
    """
    nombre = fields.StringField([validators.required(u'El campo nombre es obligatorio')])
    apellidos = fields.StringField()
    usuario = fields.StringField([validators.required(u'Es necesario introducir el campo usuario')])
    email = fields.StringField("email", [validators.required(message=u'El email no puede estar vacío')])
    password = fields.PasswordField(validators=[validators.DataRequired(u'El campo de la contraseña no puede estar vacío'), validators.EqualTo('confirm', message=u'Las contraseñas deben coincidir')])
    confirm = fields.PasswordField('Repeat Password')
