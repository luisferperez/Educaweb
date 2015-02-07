# -*- coding: utf-8 -*-
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
from xml.dom.minidom import parseString
#import xml.etree.ElementTree
import zipfile, shutil

def creaODT(exam):
    """
    función para exportar los examenes a un fichero tipo odt    
    http://www.linuxjournal.com/article/9347?page=0,1
    """
    myfile = zipfile.ZipFile('server/static/plantilla.odt')
    listoffiles = myfile.infolist()
    for s in listoffiles:
        if s.orig_filename == 'content.xml':
            fd = open('server/static/prueba.xml','w')
            bh = myfile.read(s.orig_filename)
            fd.write(bh)
            fd.close()
    

    shutil.copy('server/static/plantilla.odt', 'server/static/plantilla2.odt')
    myfile = zipfile.ZipFile('server/static/plantilla2.odt')
    ostr = myfile.read('content.xml', 'w')
    
    doc = parseString(ostr)
    paras = doc.getElementsByTagName('text:p')
    text_in_paras = []
    for p in paras:
        for ch in p.childNodes:
            if ch.nodeType == ch.TEXT_NODE:
                text_in_paras.append(ch.data)
                if ch.data.count('Asignatura') > 0:
                    print "Encontrada asignatura"
                    ch.data = ch.data + "1"
                    nuevo_nodo = ch
                    p.appendChild(nuevo_nodo)
                print ch.data
                
    fd = open('server/static/prueba.xml','w')

    print doc.toprettyxml()
#    myfile.write('server/static/prueba.xml', 'content.xml')

    doc.writexml(fd)
    doc.unlink()
    
    fd.close()

"""
    tree = xml.etree.ElementTree.parse('server/static/prueba.xml')    
    root = tree.getroot()
    for child in root:
        print "Tag, attrib:", child.tag, child.attrib
        for ch in child:
            print "tag 1:", ch.tag
            print "at 1:", ch.attrib
            print "text 1:", ch.text
            if "text" in ch.tag:
            #if ch.attrib == "text":                
                for c in child:                
                    print "tag, at child 2:", c.tag, c.attrib
                    print "text 2:", c.text

    for text in root.iter('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}text'):
        print 'Con tree:', text.tag, text.attrib, text.text
"""
#    myfile.write('server/static/prueba.xml', 'content.xml')
#    myfile.close()


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
 
class WordDocument(object):
    """
    Some convenience methods for Word documents accessed
    through COM.
    http://dzone.com/snippets/script-word-python
    """
 
#    def __init__(self, visible=False):
#        self.app = Dispatch("Word.Application")
#        self.app.Visible = visible
 
     
    def new(self, filename=None):
        """
        Create a new Word document. If 'filename' specified,
        use the file as a template.
        """
        self.app.Documents.Add(filename)
 
    def open(self, filename):
        """
        Open an existing Word document for editing.
        """
        self.app.Documents.Open(filename)
 
    def save(self, filename=None):
        """
        Save the active document. If 'filename' is given,
        do a Save As.
        """
        if filename:
            self.app.ActiveDocument.SaveAs(filename)
        else:
            self.app.ActiveDocument.Save()
 
    def save_as(self, filename):
        return self.save(filename)
 
    def print_out(self):
        """
        Print the active document.
        """
        self.app.Application.PrintOut()
 
    def close(self):
        """
        Close the active document.
        """
        self.app.ActiveDocument.Close()
 
    def quit(self):
        """
        Quit Word.
        """
        return self.app.Quit()
 
    def find_and_replace(self, find_str, replace_str):
        """
        Find all occurances of 'find_str' and replace with 'replace_str'
        in the active document.
        """
        self.app.Selection.HomeKey(Unit=wdStory)
        find = self.app.Selection.Find
        find.Text = find_str
        while self.app.Selection.Find.Execute():
            self.app.Selection.TypeText(Text=replace_str)