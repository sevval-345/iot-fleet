# 📡 IoT Fleet Management UI

## 📖 Proje Amacı
Bu proje, IoT cihazlarına ait SIM kartların **kullanımını, risk durumlarını ve yönetim aksiyonlarını** merkezi bir arayüz üzerinden izlemeyi ve yönetmeyi amaçlamaktadır.  
Telekom operatörleri, kurumsal müşteriler veya büyük ölçekli IoT ağları yöneten ekipler için tasarlanmıştır.  

---

## 🚀 Özellikler
- **Filo Tablosu** → arama, filtre, risk renkleri, son sinyal
- **SIM Detayı** → 30 günlük grafik, anomali rozetleri
- **Toplu Eylem Paneli** → çoklu seçim + özet
- **What-If Kartları** → Mevcut, Plan Yükseltme, +200MB Paket
- **Erişilebilirlik** → koyu/açık tema, hata ve boş durum ekranları

---

## ⚙️ Kullanılan Teknolojiler
- **Backend** → FastAPI, SQL Server, Pandas, SQLAlchemy
- **Frontend** → React (Vite + TypeScript), TailwindCSS, Recharts, React Router

---

## 🔌 API Uçları (Backend)
- `GET /api/fleet` → SIM listesi  
- `GET /api/usage/{sim_id}` → Kullanım verileri  
- `GET /api/anomalies/{sim_id}` → Anomali listesi  
- `POST /api/analyze/{sim_id}` → Risk skoru & özet  
- `POST /api/whatif/{sim_id}` → What-If senaryosu  

---



## 📂 Çalıştırma
### Backend
```bash
uvicorn app.main:app --reload  # http://localhost:8000
