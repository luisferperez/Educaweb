# -*- coding: utf-8 -*-

# Define login and registration forms (for flask-login)
from wtforms import form, fields, validators
from models import Usuarios, Preguntas, Asignaturas, Examenes

class LoginForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('El usuario no es valido')

        if user.password != self.password.data:
            raise validators.ValidationError('El password no es correcto')

    def get_user(self):
        return Usuarios.objects(login=self.login.data).first()


class RegistrationForm(form.Form):
    nombre = fields.TextField(validators=[validators.required()])
    apellidos = fields.TextField(validators=[validators.required()])
    login = fields.TextField(validators=[validators.required()])
    email = fields.TextField()
    password = fields.PasswordField(validators=[validators.DataRequired(), validators.EqualTo('confirm', message='Passwords must match')])
    confirm = fields.PasswordField('Repeat Password')

    def validate_login(self, field):
        if Usuarios.objects(login=self.login.data):
            raise validators.ValidationError('Nombre de usuario duplicado')

class GeneraExamenForm(form.Form):
    TIPO = ((0, 'Desarrollo'), (1, 'Test'),(2, 'Verdadero o Falso'))
    MODO = ((0, 'Aleatorio'), (1, 'Preguntas por tema'))

    nombre = fields.StringField('Nombre', [validators.required()])
    asignatura = fields.SelectField('Asignatura:', [validators.required()])
    tipo_examen = fields.SelectField('Tipo de Examen:', coerce=int, choices=TIPO)
    num_preguntas = fields.IntegerField(u'Número de preguntas:', [validators.required()])
    modo = fields.SelectField('Modo de examen:', coerce=int, choices=MODO)
    publico = fields.BooleanField(u'¿Desea hacer público el examen?')
    
    def validate_nombre(self, field):
        if Examenes.objects(nombre=self.nombre.data):
            raise validators.ValidationError(u'El nombre del examen ya ha sido usado')

    def validate_num_preguntas(self, field):
        asignatura = Asignaturas.objects(asignatura=self.asignatura.data).first()
        tipo = self.tipo_examen.data
        num_preguntas = self.num_preguntas.data
        preguntas = Preguntas.objects(asignatura=asignatura.get_id(), tipo=tipo).count()
        if preguntas < num_preguntas:
            raise validators.ValidationError(u'No existen suficientes preguntas de la asignatura para el tipo indicado.')            
            #raise validators.ValidationError(u'No existen suficientes preguntas de la asignatura ' + str(asignatura)+ u' para el tipo indicado.')
