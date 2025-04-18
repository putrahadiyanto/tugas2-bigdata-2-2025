# Transformasi API YFinance

API REST berbasis Flask yang menyediakan akses ke data saham dari Yahoo Finance yang telah ditransformasi dan diagregasikan menggunakan Apache Spark menjadi berbagai periode waktu.

## Deskripsi

Proyek ini merupakan bagian dari Tugas 2 mata kuliah Big Data Platform yang bertujuan untuk mentransformasi data mentah dari Yahoo Finance menjadi data agregasi berbagai periode waktu (harian, bulanan, tahunan, dan dua tahun) menggunakan Apache Spark. Hasil transformasi disimpan ke MongoDB dan dapat diakses melalui API REST menggunakan Flask.

## Fitur Utama

- Transformasi data Yahoo Finance menggunakan Apache Spark
- Agregasi data berdasarkan berbagai periode waktu:
  - Harian per ticker
  - Bulanan per ticker
  - Tahunan per ticker
  - Per dua tahun per ticker
- API REST untuk mengakses data yang telah diaregasi
- Integrasi dengan MongoDB untuk penyimpanan data
- Cross-Origin Resource Sharing (CORS) untuk akses dari aplikasi web

## Struktur Proyek

```
transformasi_api_yfinance/
├── app.py          # Aplikasi Flask API
└── spark.py        # Script Spark untuk transformasi data
```

## Persyaratan Sistem

- Python 3.9 atau lebih baru
- Apache Spark 3.x
- MongoDB (lokal)
- Flask dan pustaka pendukung lainnya (flask-cors, pymongo)

## Cara Menggunakan

### Persiapan Awal

1. Kloning repositori:

   ```
   git clone https://github.com/username/tugas2-bigdata-2-2025.git
   cd tugas2-bigdata-2-2025/transformasi_api_yfinance
   ```

2. Pasang dependensi yang diperlukan:

   ```
   pip install -r requirements.txt
   ```

3. Pastikan MongoDB berjalan di localhost:27017

### Transformasi Data

1. Jalankan script Spark untuk mentransformasi data dari Yahoo Finance dan menyimpannya ke MongoDB:

   ```
   spark-submit spark.py
   ```

2. Script ini akan:
   - Membaca data saham dari MongoDB (koleksi `idx_emiten`)
   - Mengagregasi data menjadi berbagai periode waktu
   - Menyimpan hasil agregasi ke koleksi MongoDB yang berbeda

### Menjalankan API

1. Jalankan aplikasi Flask API:

   ```
   python app.py
   ```

2. API akan berjalan di `http://localhost:5000`

### Endpoint API

API menyediakan akses ke data agregasi berdasarkan ticker saham dan parameter yang diinginkan:

- **GET /api/daily/<ticker>/<column>**: Mendapatkan data agregasi harian untuk ticker dan kolom tertentu
- **GET /api/monthly/<ticker>/<column>**: Mendapatkan data agregasi bulanan untuk ticker dan kolom tertentu
- **GET /api/yearly/<ticker>/<column>**: Mendapatkan data agregasi tahunan untuk ticker dan kolom tertentu

**Parameter**:

- `ticker`: Kode ticker saham (contoh: BBRI, TLKM, ANTM)
- `column`: Kolom data yang ingin diambil (contoh: avg_open, avg_close, avg_volume)

**Contoh Penggunaan**:

```
GET http://localhost:5000/api/monthly/BBRI/avg_close
```

**Contoh Respons**:

```json
[
  {
    "Year": 2023,
    "Month": 1,
    "avg_close": 4521.5
  },
  {
    "Year": 2023,
    "Month": 2,
    "avg_close": 4562.75
  },
  ...
]
```

## Penanganan Error

- API akan mengembalikan error 404 jika ticker saham atau kolom yang diminta tidak ditemukan
- Respons error akan diberikan dalam format JSON:
  ```json
  {
    "error": "404 Not Found: Ticker not found"
  }
  ```

## Tips Penggunaan

1. **Kinerja Query**: Untuk performa yang lebih baik, gunakan proyeksi yang tepat dengan menentukan kolom spesifik yang ingin diambil
2. **CORS**: API sudah dikonfigurasi dengan CORS untuk akses dari domain lain (terutama aplikasi frontend)
3. **Caching**: Pertimbangkan untuk mengimplementasikan mekanisme caching untuk mengurangi beban database

## Kontribusi

Kontribusi untuk proyek ini sangat disambut. Silakan ikuti langkah-langkah berikut:

1. Fork repositori
2. Buat branch fitur (`git checkout -b fitur-baru`)
3. Commit perubahan Anda (`git commit -am 'Menambahkan fitur baru'`)
4. Push ke branch (`git push origin fitur-baru`)
5. Buat Pull Request baru

## Lisensi

Didistribusikan di bawah lisensi MIT. Lihat `LICENSE` untuk informasi lebih lanjut.
