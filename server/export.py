# -*- coding: utf-8 -*-
"""
@author: Luis Fdo. Pérez
@co-authors: 

Functions to export data from exams to ODT or PDF files
"""

import zipfile, shutil

# Imports from reportlab library for export to PDF files
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

# Imports for export to ODT files
from odf.opendocument import OpenDocumentText
from odf.text import P, H
from xml.dom.minidom import parseString


def exportODT(examen, archivo):
    """ 
    Function to export the data exam to a odt file.
    The input data is the exam and the ODT file to write.
    This function uses odfpy library
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

    # an element is added to the object "textdoc" for each question    
    for pregunta in preguntas:
        texto = str(i) + ".- " + str(pregunta.texto.encode('utf-8'))  
        p = P(text = texto)
        textdoc.text.addElement(p)
   
        # For test questions
        if pregunta.tipo == 1:
            for opcion in pregunta.opciones:                              
                texto = opcion.letra + "). " + opcion.texto.encode('utf-8')
                p = P(text = texto.encode('utf-8'))
                textdoc.text.addElement(p)
                                        
        # For true or false questions
        elif pregunta.tipo == 2:
            texto = "A).- Verdadero"
            p = P(text = texto.encode('utf-8'))
            textdoc.text.addElement(p)
            
            texto = "B).- Falso"
            p = P(text = texto)
            textdoc.text.addElement(p)
            
        p = P()
        textdoc.text.addElement(p)
        p = P()
        textdoc.text.addElement(p)

        i = i + 1
        
    # Save complete file
    textdoc.save(archivo)
        
    return examen


def exportODT2(examen, archivo):
    """
    Another way to export to a odt file.
    In this case we use the zipfile and dom libraries 
    to extract and parse the files from the odt file
    that we use as model
    """
    
    # Extract data from exam
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
                    txt = doc.createTextNode(str(i) + ".- " + pregunta.texto)
                    x.appendChild(txt)
                    p.appendChild(x)
                    
                    # For test quiestions
                    if pregunta.tipo == 1:
                        for opcion in pregunta.opciones:
                            x = doc.createElement("text:p")
                            
                            texto = opcion.letra + "). " + opcion.texto
                            txt = doc.createTextNode(texto)
                            x.appendChild(txt)
                            p.appendChild(x)
                                        
                    # For true or false questions
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
                    
    # You need to make the "encoding" to avoid errors with the ñ and other characters
    myfile.writestr('content.xml', doc.toprettyxml(encoding='utf-8'))
    myfile.close()                
         
    return examen

def exportPDF(examen, filePDF):
    """ 
    Function to export the data exam to a pdf file.
    The input data is the exam and the PDF file to write.
    This function uses reportlab library
    """
    
    # Extract data from exam
    asignatura = examen.asignatura
    nombre = examen.nombre
    preguntas = examen.preguntas

    story = []
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Cabecera', alignment=TA_CENTER, fontSize=16))
    styles.add(ParagraphStyle(name='Titulo', fontSize=12))
    
    doc=SimpleDocTemplate(filePDF)

    # Put the name of the subject
    para = Paragraph("<u><b>"+str(asignatura)+"</b></u>", styles['Cabecera'])
    story.append(para)
    story.append(Spacer(0,20))
    
    # Put the name of the exam
    para = Paragraph("<u>"+str(nombre)+"</u>", styles['Titulo'])
    story.append(para)
    story.append(Spacer(0,20))

    # Put the exam questions
    i = 1         
    for pregunta in preguntas:
        texto = str(i) + ".- " + str(pregunta.texto.encode('utf-8'))
        story.append(Paragraph(texto, styles["Normal"]))
        
        i = i + 1
        
        # For test questions
        if pregunta.tipo == 1:
            story.append(Spacer(0,7))
            for opcion in pregunta.opciones:
                texto = opcion.letra + ").- " + opcion.texto.encode('utf-8')
                story.append(Paragraph(texto, styles["Normal"]))
                story.append(Spacer(0,7))
        
        # For true or false questions
        elif pregunta.tipo == 2:
            texto = "A).- Verdadero"
            story.append(Paragraph(texto, styles["Normal"]))
            texto = "B).- Falso"
            story.append(Paragraph(texto, styles["Normal"]))

        story.append(Spacer(0,40))

    doc.build(story)

    return examen