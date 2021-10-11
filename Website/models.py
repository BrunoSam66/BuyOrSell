from sqlalchemy.sql.expression import false, true
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Float

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000),nullable=False, unique=True)
    foto_name= db.Column(db.String(100),nullable=False, unique=False, default='guest_user.jpg')
    market_products= db.Column(db.String(10000),nullable=True, unique=False,default='')
    logo_user= db.Column(db.String(100),nullable=True, unique=False)
    description = db.Column(db.String(10000), nullable=True, unique=False)
    products= db.relationship('Produto')# coleção de produtos daquele utilizador
    users_follow_me=db.Column(db.String(10000),nullable=True, unique=False, default='')
    notification= db.Column(db.Integer, default=0)

class Produto(db.Model):
    __tablename__ = 'produto'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90))
    description = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())   
    category = db.Column(db.String(255))    
    money = db.Column(Float, nullable=False)
    userOwners = db.Column(db.String(255)) 
    userOwnersid = db.Column(db.Integer, db.ForeignKey("user.id")) # referencia a que user pertence este produto
    type = db.Column(db.String(50),nullable=False)
    picture =  db.relationship('Img') #coleção das imagens do produto
    user_likedIt= db.Column(db.String(10000),nullable=True, unique=False, default='')
    auctiondate= db.Column(db.DateTime(timezone=True),nullable=True)
    users_enjoy_it=db.Column(db.String(10000),nullable=True, unique=False, default='')

class Img(db.Model):
    __tablename__ = 'img'
    id = db.Column(db.Integer, primary_key=True)
    #/img = db.Column(db.Text, unique=False, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    produtoid = db.Column(db.Integer, db.ForeignKey("produto.id"), unique=False) # referencia o produto a que a imagem pertence
    width = db.Column(db.Integer, nullable=False,unique=False)
    height = db.Column(db.Integer, nullable=False, unique=False)