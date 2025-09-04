from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safe_wheels.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)

app.app_context().push()

class Admin(db.Model):
    
    admin_id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,nullable=False)
    email=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    
class User(db.Model):
    
    user_id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    name=db.Column(db.String,nullable=False)
    phone=db.Column(db.Integer,nullable=False)
    money=db.Column(db.Float,nullable=False,default=0.0)
    gender=db.Column(db.String(1),nullable=False)
    dob=db.Column(db.String,nullable=False)

    

class ParkingLot(db.Model):
    parklot_id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,unique=True,nullable=False)
    address=db.Column(db.String,nullable=False)
    pin=db.Column(db.Integer,nullable=False)
    price=db.Column(db.Float,nullable=False)
    capacity=db.Column(db.Integer,nullable=False)
    available=db.Column(db.Integer,nullable=False)


class ParkingSpot(db.Model):
    parkingspot_id=db.Column(db.Integer,primary_key=True)
    parklot_id=db.Column(db.Integer,db.ForeignKey('parking_lot.parklot_id'))
    status=db.Column(db.Integer,nullable=False,default=0)
    lot = db.relationship('ParkingLot', backref='spots')
    


class Bill(db.Model):
    bill_id=db.Column(db.Integer,primary_key=True)
    parklot_id=db.Column(db.Integer,db.ForeignKey('parking_lot.parklot_id'),nullable=False)
    parkingspot_id=db.Column(db.Integer,db.ForeignKey('parking_spot.parkingspot_id'),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey( 'user.user_id'),nullable=False)
    start=db.Column(db.DateTime,nullable=False)
    end=db.Column(db.DateTime,nullable=True)
    date=db.Column(db.String,nullable=False)
    amount=db.Column(db.Float,nullable=True)
    vehicle_number = db.Column(db.String,nullable=False)
    settled=db.Column(db.Integer,nullable=False)
    user=db.relationship('User',backref='bills')
    spot=db.relationship('ParkingSpot',backref='bills')
    lot=db.relationship('ParkingLot',backref='bills')
    
    


def create_tables():
    with app.app_context():
        db.create_all()
        admin=Admin.query.filter_by(admin_id=1).first()
        if not admin:
         admin=Admin(admin_id=1,name='Admin',email='Admin@g.com',password='@')
         db.session.add(admin)
         db.session.commit()


from controllers.gen_routes import *


    
          

        

if __name__=="__main__":
    create_tables()
    app.run(debug=True,port=5000)
