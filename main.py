from flask import Blueprint
from . import create_app
#/from gevent.pywsgi import WSGIServer

app= create_app()

main = Blueprint('main', __name__)
if __name__ == '__main__':
    app.run(debug=True)    
    # pip install gevent #/para produção/desenvolvimento
    #/ http_server = WSGIServer(('', 5000), app)
    #/ http_server.serve_forever()


