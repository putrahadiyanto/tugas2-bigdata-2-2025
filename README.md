# Tugas 2 Big Data Platform

Repositori ini berisi implementasi untuk Tugas 2 mata kuliah Big Data Platform yang berfokus pada transformasi dan analisis data keuangan dari Bursa Efek Indonesia (IDX). Proyek ini terdiri dari tiga subproyek berbeda yang saling melengkapi untuk membentuk sebuah ekosistem pengolahan data keuangan yang komprehensif.

## Anggota Kelompok

- 2305995 A Bintang Iftitah FJ
- 2309013 Daffa Faiz Restu Oktavian 
- 2307589 Fariz Wibisono
- 2309245 Hasbi Haqqul Fikri
- 2308163 Putra Hadiyanto Nugroho
- 2308355 Raffi Adzril Alfaiz

## Deskripsi Proyek

Proyek ini bertujuan untuk mendemonstrasikan kemampuan pengolahan data besar (big data) dengan melakukan transformasi dan analisis pada berbagai bentuk data keuangan, meliputi:

1. **Analisis Sentimen dan Ringkasan Berita Keuangan** - Menggunakan AI untuk menganalisis berita keuangan IDX
2. **Agregasi Data Yahoo Finance** - Menyediakan API untuk data saham yang telah diaregasi dalam berbagai periode waktu
3. **Ekstraksi dan Transformasi Data Laporan Keuangan** - Mengolah data XML laporan keuangan menjadi format terstruktur

Ketiga komponen ini bekerja bersama untuk memberikan pemahaman yang lebih mendalam tentang data keuangan dan memudahkan pengambilan keputusan investasi.

## Struktur Proyek

```
tugas2-bigdata-2-2025/
├── README.md                         # Dokumentasi utama proyek
├── LICENSE                           # Lisensi proyek
│
├── financial-news-analyzer-main/     # Subproyek 1: Analisis berita keuangan
│   ├── config.py                     # Konfigurasi aplikasi
│   ├── main.py                       # File utama untuk menjalankan analisis
│   ├── upload_to_mongodb.py          # Script untuk upload hasil ke MongoDB
│   ├── README.md                     # Dokumentasi subproyek 1
│   └── ...                           # File dan direktori pendukung lainnya
│
├── transformasi_api_yfinance/        # Subproyek 2: API data Yahoo Finance
│   ├── app.py                        # Aplikasi Flask API
│   ├── spark.py                      # Script Spark untuk transformasi data
│   └── README.md                     # Dokumentasi subproyek 2
│
└── transformasi_lapkeu/              # Subproyek 3: Transformasi laporan keuangan
    ├── Transformasi Lapkeu.ipynb     # Notebook untuk transformasi laporan keuangan
    ├── json/                         # Data laporan keuangan tahunan
    │   └── lapkeu_tahunan_2024.json  # Data laporan keuangan tahun 2024
    └── README.md                     # Dokumentasi subproyek 3
```

## Subproyek

### 1. Financial News Analyzer

Aplikasi untuk menganalisis berita finansial dari Bursa Efek Indonesia dengan menggunakan AI untuk:

- Analisis sentimen (positif, netral, negatif) berita keuangan
- Ekstraksi ticker saham yang disebutkan dalam berita
- Pembuatan ringkasan otomatis dari konten berita dalam Bahasa Indonesia
- Penyimpanan hasil analisis di MongoDB

[Lihat detail subproyek Financial News Analyzer](./financial-news-analyzer-main/README.md)

### 2. Transformasi API YFinance

API berbasis Flask yang menyediakan akses ke data saham dari Yahoo Finance yang telah diproses menggunakan Apache Spark untuk berbagai periode agregasi:

- Agregasi harian berdasarkan ticker
- Agregasi bulanan berdasarkan ticker
- Agregasi tahunan berdasarkan ticker
- Agregasi per dua tahun berdasarkan ticker

[Lihat detail subproyek Transformasi API YFinance](./transformasi_api_yfinance/README.md)

### 3. Transformasi Laporan Keuangan

Notebook PySpark untuk mentransformasi data XML laporan keuangan dari IDX menjadi format terstruktur berdasarkan sektor industri:

- Transformasi data perbankan
- Transformasi data jasa keuangan
- Transformasi data jasa investasi
- Transformasi data asuransi
- Transformasi data sektor umum lainnya

[Lihat detail subproyek Transformasi Laporan Keuangan](./transformasi_lapkeu/README.md)

## Persyaratan Sistem

- Python 3.9 atau lebih baru
- Apache Spark 3.x
- MongoDB (lokal atau Atlas)
- LM Studio untuk layanan AI (subproyek Financial News Analyzer)
- Pustaka Python: pyspark, flask, pymongo, flask-cors, pandas, requests, dll.

## Bagaimana Cara Menggunakan

Setiap subproyek memiliki instruksi detail dalam README masing-masing. Secara umum:

1. Kloning repositori ini:

   ```
   git clone https://github.com/username/tugas2-bigdata-2-2025.git
   cd tugas2-bigdata-2-2025
   ```

2. Pasang dependensi yang diperlukan:

   ```
   pip install -r requirements.txt
   ```

3. Jalankan masing-masing subproyek sesuai kebutuhan dengan mengikuti petunjuk di README subproyek.

## Kontribusi

Kontribusi untuk proyek ini sangat disambut. Silakan ikuti langkah-langkah berikut:

1. Fork repositori
2. Buat branch fitur (`git checkout -b fitur-baru`)
3. Commit perubahan Anda (`git commit -am 'Menambahkan fitur baru'`)
4. Push ke branch (`git push origin fitur-baru`)
5. Buat Pull Request baru

## Lisensi

Didistribusikan di bawah lisensi MIT. Lihat `LICENSE` untuk informasi lebih lanjut.