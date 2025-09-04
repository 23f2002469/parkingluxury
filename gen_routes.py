from flask import current_app as app, render_template, request, redirect, url_for, flash, session,Response
from io import BytesIO
import matplotlib.pyplot as plt
from app import db,Admin ,User,ParkingLot,ParkingSpot,Bill
from datetime import datetime
import random

@app.route('/',methods=['GET','POST'])
def login():
   if request.method=='GET':
      return render_template('login.html')
   else:
       email=request.form.get('email')
       password=request.form.get('password')
       user=User.query.filter_by(email=email).first()
       admin=Admin.query.filter_by(email=email).first()
       
       if not user and not admin:
            flash('Email ID is not registered','error')
            return redirect(url_for('login'))
       elif user and user.password!=password:
            flash('Incorrect password','error')
            return redirect(url_for('login'))
       elif admin and admin.password!=password:
            flash('Incorrect password','error')
            return redirect(url_for('login'))


       if user and user.password==password:
         session['email']=user.email
         session['name']=user.name
         flash('Welcome to Safe Wheels','success')
         return redirect(url_for('user_home', user_id=user.user_id))

       elif admin and admin.password==password:
          session['email']=admin.email
          session['name']=admin.name
          flash(f'Welcome {admin.name}','success')
          return redirect(url_for('admin_home'))
                
@app.route("/logout/")
def logout():
   session.pop('email',None)
   flash('You have been logged out successfully','success')
   return redirect(url_for('login'))

@app.route('/signup/',methods=['GET','POST'])
def signup():
   if request.method=='GET':
      return render_template('signup.html')

   else:
      email=request.form.get('email')
      password=request.form.get('password')
      name=request.form.get('name')
      gender=request.form.get('gender')
      phone=request.form.get('phone')
      dob=request.form.get('dob')
      
      exist=User.query.filter_by(email=email).first() or Admin.query.filter_by(email=email).first()
      if exist:
         flash('Existing Credentials !!Please login','error')
         return redirect(url_for('login'))
      
      flash("Registration successfull! Welcome","success")
      flash("Login Now",'success')
      new_user=User(email=email,password=password,name=name,gender=gender,phone=phone,dob=dob)
      db.session.add(new_user)
      db.session.commit()
      return redirect(url_for('login'))
   
@app.route('/admin/home/',methods=['GET','POST'])
def admin_home():
   if session['email'] not in [admin.email for admin in Admin.query.all()]:
       flash("Please Login first",'error')
       return redirect(url_for('login'))
   
   if request.method=='GET':
      parklots=ParkingLot.query.all()
      if not (parklots):
       flash("No parking lots available",'info')
       return render_template('admin_home.html',parklots=[])

      return render_template('admin_home.html',parklots=parklots)
   
   elif request.method=='POST':
      search=request.form.get('search')
      searchlot=ParkingLot.query.filter_by(name=search).first()
      if not searchlot:
         flash("No parking lot found with that name",'info')
         return redirect(url_for('admin_home'))
      return render_template('admin_home.html',parklots=[searchlot])

@app.route('/admin/users/')
def users():
   if session['email'] not in [admin.email for admin in Admin.query.all()]:
      flash("Please Login first",'error')
      return redirect(url_for('login'))
   users=User.query.all()
   if not users:
      flash("No users registered yet",'info')
      return render_template('users.html',users=[])
   return render_template('users.html',users=users)


@app.route('/add_parking_lot/',methods=['GET','POST'])
def add_parking_lot():
   if request.method=='GET':
      return render_template('add_parking_lot.html')
   elif request.method=='POST':
      
      name = request.form.get('name')
      pin = request.form.get('pin')
      address = request.form.get('address')
      price = float(request.form.get('price'))
      capacity = int(request.form.get('capacity'))
      available = int(request.form.get('available', random.randint(1, capacity)))
      parklot = ParkingLot.query.filter_by(name=name).first()

      if parklot:
         parklot.price=price
         db.session.commit()
         
         delete= request.form.get('delete')
         if delete:
          spots= ParkingSpot.query.filter_by(parklot_id=parklot.parklot_id).all()
          bills= Bill.query.filter_by(parklot_id=parklot.parklot_id).all()
          for bill in bills:
            db.session.delete(bill)
          for spot in spots:
            db.session.delete(spot)

          db.session.delete(parklot)
          db.session.commit()
          flash('Parking lot and all its associated data deleted successfully', 'success')
          return redirect(url_for('admin_home'))
      

         if capacity<available :
            flash("Available should be less than or equal to Capacity","error")
            return redirect(url_for('parkinglot', parklot_id=parklot.parklot_id))
         if parklot.available !=available:
            check=Bill.query.filter_by(parklot_id=parklot.parklot_id, settled=0).first()
            if check:
               flash("Cannot update parking lot while there are active bookings","error")
               return redirect(url_for('parkinglot', parklot_id=parklot.parklot_id))
            else:
               change=available-parklot.available
               if (change > 0 and ((parklot.available+change) <= capacity)):
                  flash(f"Added {change} spots to the parking lot","success")
                  parklot.available += change
                  db.session.commit()
                  for i in range(change):
                   new_spot=ParkingSpot(parklot_id=parklot.parklot_id,status=0)
                   db.session.add(new_spot)
                   db.session.commit()
                  
               

               elif change < 0:
                  flash(f"Removed {-change} spots from the parking lot","success")
                  parklot.available += change
                  db.session.commit()
                  for i in range(-change):
                     spot=ParkingSpot.query.filter_by(parklot_id=parklot.parklot_id,status=0).first()
                     existing_bills=Bill.query.filter_by(parklot_id=parklot.parklot_id, parkingspot_id=spot.parkingspot_id, settled=1).all()
                     for bill in existing_bills:
                        db.session.delete(bill)
                        db.session.commit()
                     db.session.delete(spot)
                     db.session.commit()
               return redirect(url_for('parkinglot', parklot_id=parklot.parklot_id))
         db.session.commit()
         flash("Updated","info")
         return redirect(url_for('admin_home',parklots=ParkingLot.query.all()))
      else:
         new_lot = ParkingLot(name=name, pin=pin, address=address, price=price, capacity=capacity, available=capacity)
         db.session.add(new_lot)
         db.session.commit()
         for i in range(capacity):
          new_spot=ParkingSpot(parklot_id=new_lot.parklot_id,status=0)
          db.session.add(new_spot)
         db.session.commit()
         flash('Parking lot added successfully', 'success')
         return redirect(url_for('admin_home',parklots=ParkingLot.query.all()))

    

@app.route('/parkinglot/<int:parklot_id>/', methods=['GET', 'POST'])
def parkinglot(parklot_id):
   if session['email'] not in [admin.email for admin in Admin.query.all()]:
      flash("Please Login first",'error')
      return redirect(url_for('login'))
   
   parklot = ParkingLot.query.get(parklot_id)
   if not parklot:
      flash("Parking lot not found", "error")
      return redirect(url_for('admin_home'))

   if request.method == 'POST':
      try:
         search = int(request.form.get('search'))
         searchspot = ParkingSpot.query.filter_by(parkingspot_id=search, parklot_id=parklot_id).first()
         if not searchspot:
            flash("Parking Spot Not Found", "error")
            searchspot = None
      except (ValueError, TypeError):
         flash("Invalid spot ID", "error")
         searchspot = None
   else:
      searchspot = None

   spotsa = ParkingSpot.query.filter_by(parklot_id=parklot_id, status=0).all()
   spotsb = ParkingSpot.query.filter_by(parklot_id=parklot_id, status=1).all()

   return render_template('parkinglot.html', 
                        parklot=parklot, 
                        spotsa=spotsa, 
                        spotsb=spotsb, 
                        spot=searchspot, 
                        Bill=Bill)


@app.route('/users/home/<int:user_id>/',methods=['GET','POST'])
def user_home(user_id):
   if session['email'] not in [user.email for user in User.query.all()]:
      flash("Please Login first as User","error")
      return redirect(url_for('login'))
   user=User.query.get(user_id)
   bills_h=Bill.query.filter_by(user_id=user_id,settled=1).all()
   bills_c=Bill.query.filter_by(user_id=user_id,settled=0).all()
   parklots=ParkingLot.query.all()
   if request.method=='GET':
      return render_template('user_home.html',user=user,bills_h=bills_h,bills_c=bills_c,parklots=parklots)
   elif request.method=='POST':
      money=float((request.form.get('money')))
      if money<0:
         flash("Money cannot be negative","warning")
         return redirect(url_for('user_home', user_id=user_id))
      user.money+=round(money,2)
      db.session.commit()
      flash("Money added successfully","success")
      return redirect(url_for('user_home', user_id=user_id))
   

@app.route('/summary/')
def summary():
   if session['email'] in [admin.email for admin in Admin.query.all()]:
     users=User.query.all()
     bills=Bill.query.filter_by(settled=1).all()
     lots=ParkingLot.query.all()
 
     revenueperuser={}
     for user in users:
        revenueperuser[user.name]=0
        for bill in bills:
           if user.user_id==bill.user_id:
              revenueperuser[user.name]+=bill.amount


     salesperlot={}
     
     for lot in lots:
        salesperlot[lot]=len(Bill.query.filter_by(settled=1,parklot_id=lot.parklot_id).all())
   

 
     totalrevenue=sum(revenueperuser.values())

     totalsales=sum(salesperlot.values())

     return render_template('summaryadmin.html',revenueperuser=revenueperuser,salesperlot=salesperlot,totalrevenue=totalrevenue,totalsales=totalsales)

   elif session['email'] in [user.email for user in User.query.all()]:
     user_id=(User.query.filter_by(email=session['email']).first()).user_id
     user=User.query.get(user_id)
  
     lots=ParkingLot.query.all()
     visitperlot={}
     spentperlot={}
     for lot in lots:
        bills=Bill.query.filter_by(settled=1,user_id=user_id,parklot_id=lot.parklot_id).all()
        visitperlot[lot]=len(bills)
        spentperlot[lot]=sum([bill.amount for bill in bills])

     totalbookings=len(Bill.query.filter_by(user_id=user_id,settled=1).all())
     totalspent=sum(spentperlot.values())
     return render_template("summaryuser.html",visitperlot=visitperlot,spentperlot=spentperlot,user=user,totalbookings=totalbookings,totalspent=totalspent)

   else:
      flash("Please Login to view summary","error")
      return redirect(url_for("login"))




   


@app.route('/edit/<int:user_id>/',methods=['GET','POST'])
def edit(user_id):
   if session['email'] not in [user.email for user in User.query.all()]:
      flash("Please Login first","error")
      return redirect(url_for('login'))
   user=User.query.get(user_id)
   if request.method=='GET':
      return render_template('edit.html',user=user)
   elif request.method=='POST':
      user.name=request.form.get('name')
      user.gender=request.form.get('gender')
      if user.email!=request.form.get('email'):
         flash("Email cannot be changed","error")
         return redirect(url_for('edit',user_id=user_id))
      user.phone=request.form.get('phone')
      user.dob=request.form.get('dob')
      db.session.commit()
      flash("Profile updated successfully","success")
      return redirect(url_for('user_home',user_id=user_id))


@app.route('/bill/<int:bill_id>/',methods=['GET','POST'])
def bill(bill_id):
   if request.method=='POST':
      if session['email'] not in [user.email for user in User.query.all()]:
         flash("Please Login first","error")
         return redirect(url_for('login'))
      bill=Bill.query.get(bill_id)
      user_id=bill.user_id
      user=User.query.get(user_id)
      bill.settled=int(request.form.get('settled'))
      bill.end=datetime.now()
      diff=((bill.end-bill.start)).total_seconds()
      bill.amount=round(bill.lot.price*diff, 2)
      bill.spot.status=0
      user.money-=bill.amount
      bill.lot.available+=1
      db.session.commit()
      flash("Bill Settled successfully","success")
      return render_template('bill.html',bill=bill)

@app.route('/book/<int:parklot_id>/<int:user_id>/',methods=['GET','POST'])
def book(parklot_id,user_id):
   if session['email'] not in [user.email for user in User.query.all()]:
      flash("Please Login to make Bookings",'error')
      return redirect(url_for('login'))

   user=User.query.get(user_id)
   parklot=ParkingLot.query.get(parklot_id)
   if request.method=="GET":
      if user.money<(parklot.price*60):
         flash("Not enough balance ..Add money first","warning")
         flash("Min one minute parking is required","error")
         return redirect(url_for('user_home',user_id=user_id))
      return render_template('book.html',parklot=parklot,user=user)


   elif request.method=="POST":
      vehicle_number=request.form.get("vehicle_number")
      available_spots=ParkingSpot.query.filter_by(parklot_id=parklot.parklot_id,status=0).all()
      user_occupied=random.choice(available_spots)
      parklot.available-=1
      user_occupied.status=1
      start=datetime.now()
      bill=Bill(parklot_id=parklot_id,user_id=user_id,vehicle_number=vehicle_number,parkingspot_id=user_occupied.parkingspot_id,start=start,date=str(datetime.now()).split(" ")[0],settled=False)
      db.session.add(bill)
      db.session.commit()
      flash("Spot Occupied, the timer has started at "+str(start),"info")
      flash("Your wheels are safe with us","success")
      return redirect(url_for('user_home',user_id=user_id))
   
@app.route('/Revenuevsuser.png/')

def plota1():
   users=User.query.all()
   bills=Bill.query.filter_by(settled=1).all()
   
   revenueperuser={}
   for user in users:
    revenueperuser[user.name]=0
    for bill in bills:
      if user.user_id==bill.user_id:
         revenueperuser[user.name]+=bill.amount

   fig,ax=plt.subplots(figsize=(10,5))

   ax.bar(list(revenueperuser.keys()),list(revenueperuser.values()))
   ax.set_xlabel('Users')
   ax.set_ylabel('Revenue')
   ax.set_title("Revenue vs\nUser")

   
   buffer=BytesIO()
   fig.savefig(buffer,format='png')
   buffer.seek(0)
   return Response(buffer.getvalue(),mimetype='image/png')



@app.route('/Revenuevslot.png/')
def plota2():
   
   bills=Bill.query.filter_by(settled=1).all()
   lots=ParkingLot.query.all()
   revenueperlot={}
   for lot in lots:
      revenueperlot[lot.name]=0
      for bill in bills:
         if lot.parklot_id==bill.parklot_id:
            revenueperlot[lot.name]+=bill.amount
    
   fig,ax=plt.subplots(figsize=(10,3))

   ax.bar(list(revenueperlot.keys()),list(revenueperlot.values()))
   ax.set_xlabel('Parklots')
   
   ax.set_ylabel('Revenue')
   ax.set_title("Revenue vs\nParklots")
   ax.tick_params(axis='x', rotation=20,labelsize=8)
   buffer=BytesIO()
   fig.savefig(buffer,format='png')
   buffer.seek(0)
   return Response(buffer.getvalue(),mimetype='image/png')

@app.route('/Salesperlot.png/')
def plota3():
   
   lots=ParkingLot.query.all()
   salesperlot={}
     
   for lot in lots:
    salesperlot[lot.name]=len(Bill.query.filter_by(settled=1,parklot_id=lot.parklot_id).all())
   
   
   fig, ax = plt.subplots(figsize=(8, 6.8), subplot_kw=dict(aspect="equal"))

   lots = list(salesperlot.keys())
   sales = list(salesperlot.values())

   def func(pct, sales):
    absolute = int(round(pct/100.*sum(sales)))
    return f"{pct:.1f}%\n({absolute:d} sales)"


   wedges, texts, autotexts = ax.pie(sales, autopct=lambda pct: func(pct, sales),
                                  textprops=dict(color="w"))

   ax.legend(wedges, lots,
          title="Parking Lots",
          loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1))

   plt.setp(autotexts, size=8, weight="bold")

   ax.set_title("Sales per Parking Lot")
   buffer=BytesIO()
   fig.savefig(buffer,format='png')
   buffer.seek(0)
   return Response(buffer.getvalue(),mimetype='image/png')



@app.route('/spentperlot.png/')
def plotu1():
   user_id=(User.query.filter_by(email=session['email']).first()).user_id
   user=User.query.get(user_id)
   lots=ParkingLot.query.all()
   spentperlot={}
     
   for lot in lots:
       spentperlot[lot.name]=0
       for bill in Bill.query.filter_by(settled=1,parklot_id=lot.parklot_id,user_id=user.user_id).all():
           spentperlot[lot.name]+=bill.amount

   fig, ax = plt.subplots(figsize=(10, 5), subplot_kw=dict(aspect="equal"))

   lots = list(spentperlot.keys())
   spent = list(spentperlot.values())

   def func(pct, spent):
       absolute = int(round(pct/100.*sum(spent)))
       return f"{pct:.1f}%"
   wedges, texts, autotexts = ax.pie(spent, autopct=lambda pct: func(pct, spent),
                                  textprops=dict(color="w"))

   ax.legend(wedges, lots,
          title="Parking Lots",
          loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1))

   plt.setp(autotexts, size=8, weight="bold")
   ax.set_title("Spent per Parking Lot")
   buffer=BytesIO()
   fig.savefig(buffer,format='png')
   buffer.seek(0)
   return Response(buffer.getvalue(),mimetype='image/png')



@app.route('/visitperlot.png/')
def plotu2():
   user_id=(User.query.filter_by(email=session['email']).first()).user_id
   user=User.query.get(user_id)
   bills=Bill.query.filter_by(settled=1,user_id=user.user_id).all()
   visitperlot={}
   for bill in bills:
      visitperlot[bill.lot.name]=visitperlot.get(bill.lot.name,0)+1

   fig,ax=plt.subplots(figsize=(8,6.8))

   ax.bar(list(visitperlot.keys()),list(visitperlot.values()))
   ax.set_xlabel('Parklots')

   ax.set_ylabel('Visits')
   ax.set_title("Visits vs\nParklots")
   ax.tick_params(axis='x', rotation=20,labelsize=8)
   buffer=BytesIO()
   fig.savefig(buffer,format='png')
   buffer.seek(0)
   return Response(buffer.getvalue(),mimetype='image/png')





   



   




















