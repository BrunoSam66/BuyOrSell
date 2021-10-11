from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail, Message

UPLOAD_FOLDER ="./Website/static"
NAME='/BuyOrSell'
MAIL_PASSWORD='qweQWE123???__'
MAIL_USERNAME='buy0rs3ll@gmail.com'
db = SQLAlchemy()
mail= Mail()

def create_app():
    app = Flask(__name__)
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')   
    app.config["UPLOAD_FOLDER"]=UPLOAD_FOLDER
    app.config['SECRET_KEY'] = 'asfshmyildrg1343546578!"#$%&/(55785447845'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] =MAIL_USERNAME 
    app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False 
    mail.init_app(app)  
    db.init_app(app)
    with app.app_context():
        db.create_all()
    
    # blueprint for auth routes in our app
    from .auth import auth 
    from .models import User, Produto,Img
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    app.register_blueprint(auth, url_prefix=NAME)

    # blueprint for non-auth parts of app
    from .views import views 
    app.register_blueprint(views,url_prefix=NAME)

    #/ if app.config["DEBUG"]:
    #     @app.after_request
    #     def after_request(response):
    #         response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    #         response.headers["Expires"] = 0
    #         response.headers["Pragma"] = "no-cache"
    #         return response
    
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))
    return app



