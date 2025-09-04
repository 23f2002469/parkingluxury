# 🚗 SafeWheels.com – Smart 4-Wheeler Parking Web Application

**Author:** Rohit Raj  
**Roll Number:** 23f2002459  
**Institute:** IIT Madras

---

## 🧠 Project Objective

To build a responsive, data-driven web application for managing 4-wheeler parking with:

- 🎛️ Dashboards for both users and admin  
- 📍 Real-time parking spot tracking  
- 💳 Automated billing  
- 📊 Visual analytics and usage summaries

---

## 🛠️ Technologies Used

- **Frontend:** HTML, CSS  
- **Backend:** Python, Flask, Flask_SQLAlchemy  
- **Database:** SQLite  
- **Visualization:** Matplotlib, BytesIO  
- **Other Tools:** Flash (for UI alerts)

---

## 🌐 Overview

**SafeWheels.com** is a smart parking web platform for 4-wheelers that provides:

- Separate access levels for **admin** and **users**
- Real-time parking management
- Automated billing system
- Interactive analytics via graphs
- Strong data validation and integrity

Only **one admin** account exists, with full control over parking lots. Users can sign up and access personalized dashboards to manage their bookings.

---

## 🔐 Admin Features

### 🧑‍💼 Admin Role

- Predefined single admin with full control over the system

### 🏗️ Parking Lot Management

- Create parking lots with a defined number of spots and base price  
- Edit lots (spots) only if there are **no active bookings** and price **whenever desired**
- Delete lots only when **all spots are empty**  
- Auto-generate parking spots based on the lot capacity

### 📊 Monitoring and Insights

- Real-time spot status monitoring  
- Search for parking lots and currently parked users  
- View **total revenue** and **sales across all lots**  
- Graphs:
  - Parking lot statuses
  - Revenue per lot
  - Sales per lot

---

## 👥 User Features

### 🔐 Authentication

- User **sign up** and **login** with credentials

### 💼 Wallet & Booking

- Add money to in-app wallet  
- Select parking lot; spot is auto-assigned  
- Booking allowed only if balance ≥ 1-minute charge  
- Booking status updates to **occupied**  
- On release:
  - Timestamp recorded
  - Auto bill generated
  - Charges deducted based on stay duration

### ⚙️ Rules

- Only one **active booking** at a time  
- New bookings are restricted until the current one is released

### 📈 Dashboard Insights

- Track **total money spent** and **number of bookings**  
- Visuals:
  - Visits per lot
  - Amount spent per lot  
- Full booking history available

---

## 🧪 Implementation Highlights

- Modeled DB schema using **Flask_SQLAlchemy**
- Created separate interfaces for user/admin using **HTML/CSS**, **Jinja2**, and **Flask**
- Used **Matplotlib** + **BytesIO** for real-time chart generation
- Data persisted with **SQLite**
- Form validations for consistent data entry
- Session control and access management with **Flask sessions**

---

## 🗃️ Database Schema

📎 [View Database Schema (Google Drive)](https://drive.google.com/file/d/16GJzVdHRrvBbf3ftXCNeMpzmnIzGT0A3/view?usp=sharing)


## 🗃️Images

📎 [View Images
(Google Drive)](https://drive.google.com/drive/folders/1c0vQ9zixGWyBLnmaQmrOVbFBonTWS1P7?usp=sharing)

---

