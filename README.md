# 📊 Streamlit XAMPP Log Analyzer

Analisis **Apache Access Log**, **Apache Error Log**, dan **MySQL Error Log** dari XAMPP dengan mudah menggunakan [Streamlit](https://streamlit.io/).  
Aplikasi ini membantu admin server & developer menemukan masalah konfigurasi maupun bug di aplikasi/database.

---

## ✨ Fitur

- **Access Log**
  - Statistik semua status code (200, 301, 404, 500, …).
  - Endpoint paling sering diakses.
  - Endpoint dengan error terbanyak.
  - IP paling aktif (potensi bot/attack).
  - Jam tersibuk (request terbanyak).
  - Tren error HTTP ≥400 per jam.

- **Apache Error Log**
  - Semua level log (INFO, WARN, ERROR, …).
  - Distribusi level log.
  - Tren error per jam.
  - Highlight error spesifik (misalnya `mod_rewrite`, `script timed out`).

- **MySQL Error Log**
  - Parsing fleksibel (ERROR, WARNING, NOTE dengan kata kunci penting).
  - Deteksi masalah InnoDB, file lock, charset/collation.
  - Insight untuk error serius: **Too many connections**, **Out of memory**, **shutdown/crash**.

- **Insight Otomatis**
  - Error rate (%) + alert merah jika >5%.
  - Deteksi broken link (404).
  - Deteksi bug server (500).
  - Deteksi Apache timeout & rewrite error.
  - Deteksi MySQL masalah koneksi, memory, crash.

- **Ekstra**
  - Semua tabel bisa diunduh sebagai **CSV** atau **Excel**.
  - Filter log berdasarkan **N hari terakhir**.
  - UI interaktif dengan grafik (Bar / Line / Pie).
  - Header aplikasi sticky (selalu terlihat saat scroll).

---

## 🚀 Instalasi

1. **Clone repository**
   ```bash
   git clone https://github.com/username/streamlit-xampp-log-analyzer.git
   cd streamlit-xampp-log-analyzer
   ```

2. **Buat virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Aktifkan venv**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Menjalankan Aplikasi

```bash
streamlit run app.py
```

Aplikasi akan berjalan di: [http://localhost:8501](http://localhost:8501)

---

## 📦 Dependencies

- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)
- [XlsxWriter](https://xlsxwriter.readthedocs.io/)

Semua sudah ada di `requirements.txt`.

---

## 📸 Screenshot (contoh)

> Tambahkan screenshot hasil analisis access.log, error.log, dan mysql-error.log di sini.

---

## 💡 Tips Penggunaan

- Upload salah satu atau semua file log:
  - `access.log`
  - `error.log`
  - `mysql-error.log`
- Gunakan sidebar untuk memilih:
  - Jumlah hari terakhir yang ingin dianalisis
  - Jenis grafik (Bar, Line, Pie)
- Insight otomatis akan muncul sesuai log yang tersedia.

---

## 🛠️ Rencana Pengembangan

- Notifikasi otomatis jika error rate tinggi.
- Integrasi dengan email / Telegram untuk alert.
- Support Nginx log format.
- Dashboard multi-server.

---

## 📜 Lisensi

MIT License © 2025
