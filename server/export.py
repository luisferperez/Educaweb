# -*- coding: utf-8 -*-
"""
@author: Luis Fdo. Pérez
@co-authors: 

Functions to export data from exams to ODT or PDF files
"""

from xml.dom.minidom import parseString
import zipfile, shutil

# Imports from reportlab library for export to PDF files
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

# Imports from odpf library for export to ODT files
from odf.opendocument import OpenDocumentText
from odf.text import P, H


def exportODT(examen, archivo):
    """ 
    Function to export the data exam to a odt file.
    The input data is the exam and the ODT file to write.
    """
    
    # Extract data from exam    
    asignatura = examen.asignatura
    nombre = examen.nombre
    preguntas = examen.preguntas

    textdoc = OpenDocumentText()
      
    h = H(outlinelevel=1, text=asignatura)
    textdoc.text.addElement(h)
    
    h = H(outlinelevel=4, text=nombre)
    textdoc.text.addElement(h)
    
    i = 1        
    for pregunta in preguntas:
        p = P(text = str(i) + ".- " + str(pregunta.texto))
        textdoc.text.addElement(p)
   
        # For test questions
        if pregunta.tipo == 1:
            for opcion in pregunta.opciones:                              
                texto = opcion.letra + "). " + opcion.texto
                p = P(text = texto)
                textdoc.text.addElement(p)
                                        
        # Para las preguntas tipo verdadero o falso
        elif pregunta.tipo == 2:
            texto = "A).- Verdadero"
            p = P(text = texto)
            textdoc.text.addElement(p)
            
            texto = "B).- Falso"
            p = P(text = texto)
            textdoc.text.addElement(p)
            
        p = P()
        textdoc.text.addElement(p)
        p = P()
        textdoc.text.addElement(p)

        i = i + 1
        
    textdoc.save(archivo)
        
    return examen


def exportODT2(examen, archivo):
    
    # Saco los datos del examen
    asignatura = examen.asignatura
    nombre = examen.nombre
    preguntas = examen.preguntas

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
                    
    myfile.writestr('content.xml', doc.toprettyxml(encoding='utf-8')) # Hay que hacer el "encoding" para que no se produzcan errores con las ñ y otros carecteres
    myfile.close()                
         
    return examen

def exportPDF(examen, filePDF):
    
    # Saco los datos del examen
    asignatura = examen.asignatura
    nombre = examen.nombre
    preguntas = examen.preguntas

    story = []
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Cabecera', alignment=TA_CENTER, fontSize=16))
    styles.add(ParagraphStyle(name='Titulo', fontSize=12))
    
    doc=SimpleDocTemplate(filePDF)

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

    return examen