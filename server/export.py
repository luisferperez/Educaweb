# -*- coding: utf-8 -*-
"""http://es.scribd.com/doc/75861786/Python-Excel-Word-PPoint-OutLook-Interfaces#scribd
"""

import pywin32
from warnings import warn


app = 'word'
word = pywin32.gencache.EnsureDispatch('%s.application' %app)
doc = word.Documents.Add()
word.Visible = True


range.InsertAfter("Hola")
warn(app)


doc.Close(False)
word.Application.Quit()