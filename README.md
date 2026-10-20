# 👗 Smart Fashion Inventory Management System

A modern, feature-rich fashion inventory management dashboard built with Django and Bootstrap 5. Manage products, categories, suppliers, and stock with beautiful charts and a responsive dark-themed UI.

---

## ✨ Features

- **Dashboard** — Real-time stats, Chart.js charts (category distribution, stock status, monthly activity, top products)
- **Product Management** — Full CRUD with search, filter by category/stock status, pagination, image upload
- **Category Management** — Create and manage fashion categories (Clothes, Beauty, Accessories, Footwear, Sportswear)
- **Supplier Management** — Track suppliers with contact info and product count
- **Inventory Management** — Stock in/out with validation, stock history logs, low-stock alerts
- **Reports** — Summary statistics and visual charts
- **Settings** — System configuration overview
- **Dummy Data** — One-command generation of 50+ products, 10 suppliers, 5 categories, 80 stock logs

---

## 🛠 Tech Stack

| Layer     | Technology              |
|-----------|-------------------------|
| Backend   | Django 5.2              |
| Database  | SQLite                  |
| Frontend  | HTML5, CSS3, JavaScript |
| UI        | Bootstrap 5             |
| Charts    | Chart.js 4              |
| Icons     | Font Awesome 6          |
| Font      | Inter (Google Fonts)    |

---

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.10+
- pip

### 2. Install Django
```bash
pip install django pillow
```

### 3. Navigate to the project
```bash
cd fashion_inventory_system
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Generate Dummy Data
```bash
python manage.py generate_dummy_data
```

### 6. Create Superuser (optional, for Django admin)
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

### 8. Open in browser
```
http://127.0.0.1:8000/
```

---

## 📁 Project Structure

```
fashion_inventory_system/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── dashboard/       # Dashboard views & chart APIs
│   ├── products/        # Product CRUD + dummy data command
│   ├── categories/      # Category CRUD
│   ├── suppliers/       # Supplier CRUD
│   └── inventory/       # Stock management, reports, settings
├── templates/
│   ├── base.html
│   ├── dashboard/
│   ├── products/
│   ├── categories/
│   ├── suppliers/
│   └── inventory/
├── static/
│   ├── css/style.css
│   └── js/main.js
└── media/               # Uploaded product images
```

---

## 📊 Dashboard

The dashboard displays:
- **6 stat cards** — Total Products, Categories, Suppliers, Low Stock, Out of Stock, Stock Value
- **4 charts** — Products by Category (doughnut), Stock Distribution (pie), Monthly Activity (bar), Top Products (horizontal bar)
- **Recent tables** — Newly added products, recent stock updates, low stock alerts

---

## 📝 License

This project is for educational and demonstration purposes.
"# Smart-IMS-" 
"# fashion-inventory-system-prpject" 
