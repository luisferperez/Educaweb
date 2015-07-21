# -*- coding: utf-8 -*-
""" 
@author: Luis Fdo. Pérez

Módulo donde se definen los modelos de datos para la base de datos
de MongoDB

"""
from mongoengine import Document, EmbeddedDocument, StringField, IntField, BooleanField, \
    ReferenceField, ListField, EmbeddedDocumentField, Q, queryset_manager, signals, \
    EmailField, SortedListField, ValidationError, NULLIFY, CASCADE
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
    
    nombre = StringField(required=True, max_length=40)
    apellidos = StringField(max_length = 80)
    usuario = StringField(required=True, max_length=80, unique=True)
    email = EmailField(required=True, max_length=100)
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

    def is_alumno(self):
        return self.tipo == 2

    def is_activado(self):
        return self.activado

    def get_id(self):
        return str(self.id)
        
    def get_usuario(self):
        return str(self.usuario)

    def get_tipo(self):
        return str(self.tipo)

    def get_asignaturas(self):
        return self.asignaturas       
        
    def get_nombre_ape(self):
        if self.apellidos:        
            return self.nombre + " " + self.apellidos
        else:
            return self.nombre

    # Required for administrative interface
    def __unicode__(self):
        return self.usuario

@update_modified.apply
class Temas(Document):
    num = IntField(required=True, unique_with = ('asignatura', 'usuario'))
    descripcion = StringField(max_length=100)
    asignatura = ReferenceField(Asignaturas, reverse_delete_rule= NULLIFY)
    usuario = ReferenceField(Usuarios, reverse_delete_rule= NULLIFY)

    # Required for administrative interface
    def __unicode__(self):
        return str(self.asignatura) + "- Tema " + str(self.num) + " - " + self.descripcion

    @queryset_manager
    def objects(doc_cls, queryset):
        lista_asignaturas=login.current_user.get_asignaturas()
        if lista_asignaturas:        
            query = Q(asignatura= lista_asignaturas[0].get_id())
            for l in lista_asignaturas[1:]:
                query |= Q(asignatura=l.get_id())
            query &= Q(usuario=login.current_user.get_id())
            return queryset.filter(query)
        else:
            return queryset.filter(usuario=login.current_user.get_id().order_by('num'))

    """
    def clean(self):
        ""Make validations before save any document""
        preguntas = Preguntas.objects(tema=self.id).count()
        if preguntas > 0:
            msg = 'No se puede grabar el tema.'
            raise ValidationError(msg)
    """
       #return queryset.filter(usuario=login.current_user.get_id()).order_by('num')


class Opciones(EmbeddedDocument):
    letra = StringField(max_length=1, required=True)
    texto = StringField()

    @queryset_manager
    def objects(doc_cls, queryset):
       return queryset.order_by('-letra')

@update_modified.apply
class Preguntas(Document):
    TIPO = ((0, 'Desarrollo'), (1, 'Test'), (2, 'Verdadero o Falso'))

    num = IntField(required=True, unique_with = ('asignatura', 'usuario'))    
    texto = StringField(required=True)
    asignatura = ReferenceField(Asignaturas, reverse_delete_rule= NULLIFY)
    tema = ReferenceField(Temas, reverse_delete_rule= NULLIFY)
    tipo = IntField(choices=TIPO)
    # Solo para la opción de verdadero o falso    
    verdadera = BooleanField() 
    # Solo para la opción de test
    opciones = ListField(EmbeddedDocumentField(Opciones))
    correcta = StringField(max_length=1)

    #respuesta = StringField()
    usuario = ReferenceField(Usuarios, reverse_delete_rule= NULLIFY)

    @queryset_manager
    def objects(doc_cls, queryset):
       return queryset.filter(usuario=login.current_user.get_id())

    # Required for administrative interface
    def __unicode__(self):
        return str(self.asignatura) + " - " + str(self.num)

@update_modified.apply
class Examenes(Document):
    nombre = StringField(required=True, unique_with = ('asignatura', 'usuario'))
    asignatura = ReferenceField(Asignaturas, reverse_delete_rule= NULLIFY)
    preguntas = ListField(ReferenceField(Preguntas))
    publico = BooleanField()
    usuario = ReferenceField(Usuarios, reverse_delete_rule= CASCADE)    

    @queryset_manager
    def objects(doc_cls, queryset):
       return queryset.filter(usuario=login.current_user.get_id())

    @queryset_manager
    def public(doc_cls, queryset):
        lista_asignaturas=login.current_user.get_asignaturas()
        if lista_asignaturas:        
            query = Q(asignatura= lista_asignaturas[0].get_id())
            for l in lista_asignaturas[1:]:
                query |= Q(asignatura=l.get_id())
            query &= (Q(publico=True) | Q(usuario=login.current_user.get_id()))
            return queryset.filter(query)
        else:
            return queryset.filter(usuario=login.current_user.get_id())

    # Required for administrative interface
    def __unicode__(self):
        return str(self.nombre) + " - " + str(self.asignatura)

    def get_id(self):
        return str(self.id)