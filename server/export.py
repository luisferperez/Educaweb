# -*- coding: utf-8 -*-
from xml.dom.minidom import parseString
import zipfile, shutil

# Importo las librerias para el reportlab (exportación a pdf)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

# Librerías de odfpy
from odf.opendocument import OpenDocumentText
from odf.text import P, H


def exportODT(examen, archivo):
    
    # Saco los datos del examen
    asignatura = examen.asignatura
    nombre = examen.nombre
    preguntas = examen.preguntas

    textdoc = OpenDocumentText()

    """        
    T1style = Style(name="T1", family="text")
    T1style.addElement(TextProperties(fontstyle="bold",fontstyleasian="bold", fontstylecomplex="bold"))
    textdoc.automaticstyles.addElement(T1style)
    """    
        
    h = H(outlinelevel=1, text=asignatura)
    textdoc.text.addElement(h)
    
    h = H(outlinelevel=4, text=nombre)
    textdoc.text.addElement(h)
    
    i = 1        
    for pregunta in preguntas:
        p = P(text = str(i) + ".- " + str(pregunta.texto))
        textdoc.text.addElement(p)
   
        # Para las preguntas tipo test
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



"""http://es.scribd.com/doc/75861786/Python-Excel-Word-PPoint-OutLook-Interfaces#scribd
import pywin32
from warnings import warn

def creaWord():
    app = 'word'
    word = pywin32.gencache.EnsureDispatch('%s.application' %app)
    doc = word.Documents.Add()
    word.Visible = True

    range.InsertAfter("Hola")
    warn(app)

    doc.Close(False)
    word.Application.Quit()
    
"""    



"""

#import win32com.client
from win32com.client import Dispatch

wdStory = 6

def creaWord2():
    import win32com.client
    wordapp = win32com.client.Dispatch("Word.Application") # Create new Word Object
    wordapp.Visible = 0 # Word Application should`t be visible
    worddoc = wordapp.Documents.Add() # Create new Document Object
    worddoc.PageSetup.Orientation = 1 # Make some Setup to the Document:
    worddoc.PageSetup.LeftMargin = 20
    worddoc.PageSetup.TopMargin = 20
    worddoc.PageSetup.BottomMargin = 20
    worddoc.PageSetup.RightMargin = 20
    worddoc.Content.Font.Size = 11
    worddoc.Content.Paragraphs.TabStops.Add (100)
    worddoc.Content.Text = "Hello, I am a text!"
    worddoc.Content.MoveEnd
    worddoc.Close() # Close the Word Document (a save-Dialog pops up)
    wordapp.Quit() # Close the Word Application 
   """ 
 
