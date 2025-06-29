# 🚚 Delivery-Bot Backend – Django-based Logistics Platform

> 📍 Real-world delivery engine for **Bukhara**

---

## 🔎 Overview

**Delivery-Bot Backend** is a powerful Django-based backend system that manages a real-time delivery ecosystem. It facilitates seamless interaction between:

- 👤 **Customers** – place delivery orders
- 🧑‍💼 **Order Managers** – verify and dispatch tasks
- 🛵 **Couriers** – receive orders and follow optimal routes

The system includes **map-based routing**, distance/time calculation, live order tracking, and a comprehensive admin panel.

---

## 🚀 Key Features

- 📦 Full **Order Lifecycle**:
  - New → Confirmed → Assigned → Delivered
- 🧭 **Optimal Routing** for couriers:
  - Map view with direction, distance (km), and estimated time (min)
- 🛵 **Courier Dashboard**:
  - See route from store to destination
  - Update delivery status in real time
- 🔔 **Status Notifications** to customers and couriers
- 🧑‍💼 **Admin Panel** (Django):
  - Create & assign orders
  - Manage clients & couriers
  - Monitor delivery progress
- 🌍 **Geo-coordinates support** for accurate routing

---

## 📍 Use Case: Bukhara City

This project is currently deployed and operating in **Bukhara**, providing real-time courier dispatching and tracking, tailored for urban delivery logistics.

---

## 🧰 Tech Stack

| Technology       | Purpose                            |
|------------------|-------------------------------------|
| Python + Django  | Core backend & admin panel         |
| PostgreSQL       | Relational database                |
| Google Maps API  | Routing, distance, time estimation |
| HTML/CSS         | Admin interface styling            |
| Docker (optional)| Containerization                   |

---

## 🗂️ Project Structure

```bash
Delivery-Bot-Backend/
├── apps/
│   ├── orders/          # Order models & views
│   ├── couriers/        # Courier logic & location
│   ├── customers/       # Customer profiles & requests
│   ├── notifications/   # Status updates
│   └── maps/            # Map & routing integration
├── static/              # CSS, JS, icons
├── templates/           # Django templates
└── manage.py
```

---

## ▶️ Getting Started

```bash
# Clone the project
git clone https://github.com/muhammadnuruz/Delivery-Bot-Backend.git
cd Delivery-Bot-Backend

# Create virtual environment
python -m venv env
source env/bin/activate  # or env\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

---

## 📸 Screenshots (optional)

### 🧾 Admin Panel (Main Page)
![Order panel screenshot](https://github.com/user-attachments/assets/bd4e3748-b1ef-4618-b524-c6b38038d0f8)

### 🧾 Sample — Store Request via Telegram
![Request screenshot](https://github.com/user-attachments/assets/8f769c19-b93f-4891-b74f-b128c0e1d68d)

---

## 📈 Roadmap

- [x] Real-time courier assignment
- [x] Google Maps integration
- [x] Distance & ETA calculations
- [ ] Telegram Bot integration
- [ ] Mobile app version (React Native or Flutter)
- [ ] Live courier tracking on customer side

---

## 👨‍💻 Developed By

**Muhammad Nur Suxbatullayev**  
🎓 Junior Back-End Developer with 1+ years of hands-on experience  
🏫 Full Scholarship Recipient at PDP University  
🧠 Skilled in building scalable and secure back-end systems using:  
- Python & Django  
- Django REST Framework (DRF)  
- PostgreSQL  
- Docker & Containerization  
- Aiogram (Telegram Bot Framework)  
- RESTful API Design & Integration

🔗 **GitHub:** [github.com/muhammadnuruz](https://github.com/muhammadnuruz)  
📬 **Telegram:** [@TheMuhammadNur](https://t.me/TheMuhammadNur)

---

## ⭐ Support the Project

If this project helped you, inspired you, or you simply liked it, please consider giving it a **⭐ on GitHub**.  
Your support boosts the project's visibility and motivates continued improvements and future updates.

Thank you for being part of the journey!
