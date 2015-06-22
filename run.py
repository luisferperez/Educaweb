# -*- coding: utf-8 -*-
"""
@author: Luis Fdo. Pérez
@co-authors: Basis code obtained from the SCC Department

Execute the application server
"""
from server.server import init_login, init_ddbb, app
from server.admin import initialize_admin_component

if __name__ == '__main__':
    
    # Initialize ddbb    
    init_ddbb()
    
    # Initialize flask-login    
    init_login(app)
    
    # Administration Panel    
    initialize_admin_component(app)

    # Start application
    app.run()