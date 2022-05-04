from datetime import datetime
from playstorescrapperapp import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    isSuperAdmin = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"



class App(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appstoreid = db.Column(db.String(20), unique=True, nullable=False)
    json = db.Column(db.Text, nullable=True)
    valid = db.Column(db.Boolean, nullable=False)
    lastChecked = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"App('{self.appstoreid}')"



class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoryName = db.Column(db.String(20), unique=True, nullable=False)



class CategoryMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appId = db.Column(db.Integer, db.ForeignKey('app.id'), nullable=False)
    categoryId = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)