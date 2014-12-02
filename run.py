# -*- coding: utf-8 -*-
from server.server import init_login, init_ddbb, app
from server.admin import initialize_admin_component

if __name__ == '__main__':
    
    init_ddbb()
    
    init_login(app)

    # Administration Panel    
    initialize_admin_component(app)

    # Main application
    app.run()