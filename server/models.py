# -*- coding: utf-8 -*-
from mongoengine import Document, EmbeddedDocument, StringField, IntField, BooleanField, \
    ReferenceField, ListField, EmbeddedDocumentField, Q, queryset_manager, signals
from flask.ext import login

def handler(event):
    """Signal decorator to allow use of callback functions as class decorators."""
    def decorator(fn):
        def apply(cls):
            event.connect(fn, sender=cls)
            return cls
        fn.apply = apply
        return fn
    return decorator

@handler(signals.pre_save)
def update_modified(sender, document):
    if login.current_user:    
        document.usuario = login.current_user.to_dbref()    

class Asignaturas(Document):
    asignatura = StringField(max_length=100, unique=True)

    def get_id(self):
        return str(self.id)

    # Required for administrative interface
    def __unicode__(self):
        return self.asignatura


    @queryset_manager
    def objects(doc_cls, queryset):
       if login.current_user.is_administrador():
           return queryset
       else:
           lista_asignaturas=login.current_user.get_asignaturas()
           query = Q(asignatura= str(lista_asignaturas[0]))
           for l in lista_asignaturas[1:]:
               query |= Q(asignatura=str(l))
           return queryset.filter(query)
           

class Usuarios(Document):
    TIPO = ((0, 'Administrador'), (1, 'Profesor'),(2, 'Alumno'))    
    
    nombre = StringField(max_length=40)
    apellidos = StringField(max_length = 80)
    login = StringField(required=True, max_length=80, unique=True)
    email = StringField(required=True, max_length=100)
    password = StringField(required=True, max_length=64)
    tipo = IntField(choices=TIPO)
    activado = BooleanField(default=False)
    asignaturas = ListField(ReferenceField(Asignaturas))
    
    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_profesor(self):
        return self.tipo == 1
        
    def is_administrador(self):
        return self.tipo == 0

    def is_activado(self):
        return self.activado

    def get_id(self):
        return str(self.id)
        
    def get_login(self):
        return str(self.login)

    def get_tipo(self):
        return str(self.tipo)

    def get_asignaturas(self):
        return self.asignaturas       
        
    def get_nombre_ape(self):
        return self.nombre + " " + self.apellidos       

    # Required for administrative interface
    def __unicode__(self):
        return self.login

@update_modified.apply
class Temas(Document):
    num = IntField(required=True, unique_with = ('asignatura', 'usuario'))
    descripcion = StringField(max_length=100)
    asignatura = ReferenceField(Asignaturas, reverse_delete_rule= 'NULLIFY')
    usuario = ReferenceField(Usuarios, reverse_delete_rule= 'NULLIFY')

    # Required for administrative interface
    def __unicode__(self):
        return str(self.asignatura) + "- Tema " + str(self.num) + " - " + self.descripcion

    @queryset_manager
    def objects(doc_cls, queryset):
       return queryset#.filter(usuario=login.current_user.get_id())


class Opciones(EmbeddedDocument):
    letra = StringField(max_length=1)
    texto = StringField()

class Respuestas(Document):
    #letra = StringField(max_length=1)
    texto = StringField()

@update_modified.apply
class Preguntas(Document):
    TIPO = ((0, 'Desarrollo'), (1, 'Test'), (2, 'Verdadero o Falso'))

    num = IntField(required=True, unique_with = ('asignatura', 'usuario'))    
    texto = StringField(required=True)
    asignatura = ReferenceField(Asignaturas, reverse_delete_rule= 'NULLIFY')
    tema = ReferenceField(Temas)
    tipo = IntField(choices=TIPO)
    # Solo para la opción de verdadero o falso    
    verdadera = BooleanField() 
    # Solo para la opción de test
    opciones = ListField(EmbeddedDocumentField(Opciones))
    correcta = StringField(max_length=1)

    respuestas = ReferenceField(Respuestas)
    usuario = ReferenceField(Usuarios, reverse_delete_rule= 'NULLIFY')

    @queryset_manager
    def objects(doc_cls, queryset):
       return queryset#.filter(usuario=login.current_user.get_id())

    # Required for administrative interface
    def __unicode__(self):
        return str(self.asignatura) + " - " + str(self.num)

@update_modified.apply
class Examenes(Document):
    nombre = StringField(required=True, unique_with = ('asignatura', 'usuario'))
    asignatura = ReferenceField(Asignaturas, reverse_delete_rule= 'NULLIFY')
    preguntas = ListField(ReferenceField(Preguntas))
    publico = BooleanField()
    usuario = ReferenceField(Usuarios, reverse_delete_rule= 'NULLIFY')    

    @queryset_manager
    def objects(doc_cls, queryset):
       return queryset.filter(usuario=login.current_user.get_id())

    @queryset_manager
    def public(doc_cls, queryset):
        lista_asignaturas=login.current_user.get_asignaturas()
        query = Q(asignatura= lista_asignaturas[0].get_id())
        for l in lista_asignaturas[1:]:
            query |= Q(asignatura=l.get_id())
        query &= Q(publico=True)
        return queryset.filter(query)

    # Required for administrative interface
    def __unicode__(self):
        return str(self.nombre) + " - " + str(self.asignatura)

    def get_id(self):
        return str(self.id)

@update_modified.apply
class Examenes_Resueltos(Document):
    examen = ReferenceField(Examenes)
    usuario = ReferenceField(Usuarios, reverse_delete_rule= 'NULLIFY')    