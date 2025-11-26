# 📊 Step 6: Metabase Dashboard Setup

This folder sets up Metabase — a powerful open-source business intelligence tool — to visualize real-time sensor data and ML predictions from the Krushaka Vikas platform.

## 🧰 What This Does

- Hosts Metabase via Docker or Docker Compose
- Connects to your existing sensor + prediction database (e.g., MySQL or PostgreSQL)
- Lets you build intuitive dashboards and charts without writing complex queries

## 🚀 How to Run Metabase

1. Pull the latest Metabase image:
```bash
docker pull metabase/metabase:latest
```

2. Run Metabase:
```bash
docker run -d -p 3000:3000 --name metabase metabase/metabase
```

3. Access Metabase:
```
http://localhost:3000
```

4. To use a custom port:
```bash
docker run -d -p 12345:3000 --name metabase metabase/metabase
```

## 🔌 Database Connection

During setup, connect Metabase to the database used by your backend (e.g., `krushaka_vikas`):

- Host: `localhost`
- Port: `3306` or `5432` (depending on your DB)
- User: `your_db_user`
- Password: `your_db_password`
- DB Name: `krushaka_vikas`
