# Financial News Analyzer

Aplikasi untuk menganalisis berita finansial dari sumber IDX dengan menggunakan kecerdasan buatan (AI) untuk ekstraksi sentimen, identifikasi ticker saham, dan pembuatan ringkasan berita.

## Deskripsi

Financial News Analyzer adalah alat untuk memproses dan menganalisis berita keuangan dari Bursa Efek Indonesia (IDX). Aplikasi ini menggunakan model bahasa AI (LLM) untuk melakukan analisis mendalam terhadap artikel berita keuangan, yang mencakup:

1. **Analisis Sentimen**: Mengidentifikasi apakah berita memiliki sentimen positif, netral, atau negatif terhadap pasar atau saham tertentu.
2. **Ekstraksi Ticker**: Mengidentifikasi kode ticker saham (seperti BBRI, TLKM, ANTM) yang disebutkan dalam berita.
3. **Pembuatan Ringkasan**: Membuat ringkasan padat dari isi berita untuk memudahkan pembacaan cepat.
4. **Penyimpanan Data Analisis**: Menyimpan hasil analisis ke MongoDB Atlas untuk penggunaan lebih lanjut.

## Fitur Utama

- Pemrosesan paralel berita menggunakan multi-threading untuk kinerja yang optimal
- Analisis sentimen (positif, netral, negatif) dengan nilai keyakinan (confidence)
- Identifikasi ticker saham yang terkait dengan berita
- Pembuatan ringkasan otomatis dari konten berita panjang
- Pemrosesan inkremental dengan penyimpanan hasil sementara untuk mencegah kehilangan data
- Upload hasil analisis ke MongoDB Atlas dengan penanganan duplikasi yang cerdas

## Struktur Proyek

```
financial-news-analyzer/
├── config.py                 # Konfigurasi aplikasi
├── main.py                   # File utama untuk menjalankan analisis
├── upload_to_mongodb.py      # Script untuk upload hasil analisis ke MongoDB
├── requirements.txt          # Daftar dependensi
├── data/                     # Direktori data
│   ├── news.json             # Data berita mentah
│   └── ticker_company.json   # Informasi ticker dan perusahaan
├── interfaces/               # Interface untuk loading data
│   └── news_loader.py        # Loader untuk data berita
├── output/                   # Output dari proses analisis
│   └── analysis.json         # Hasil analisis berita
├── services/                 # Layanan inti aplikasi
│   ├── combined_analysis_service.py  # Layanan untuk analisis gabungan
│   ├── llm_service.py               # Layanan untuk akses model bahasa
│   ├── sentiment_service.py         # Layanan untuk analisis sentimen
│   ├── summarizer_service.py        # Layanan untuk pembuatan ringkasan
│   └── ticker_extractor.py          # Layanan untuk ekstraksi ticker
└── utils/                    # Utilitas pendukung
    ├── logger.py             # Modul untuk logging
    └── text_utils.py         # Utilitas untuk pemrosesan teks
```

## Persyaratan Sistem

- Python 3.9 atau lebih baru
- LM Studio API (berjalan di localhost:1234)
- Koneksi internet untuk akses ke MongoDB Atlas
- Minimal RAM 4GB (direkomendasikan 8GB atau lebih untuk set data besar)

## Cara Menggunakan

### Persiapan Awal

1. Kloning repositori ini:

   ```
   git clone https://github.com/username/financial-news-analyzer.git
   cd financial-news-analyzer
   ```

2. Pasang dependensi yang diperlukan:

   ```
   pip install -r requirements.txt
   ```

3. Pastikan LM Studio sudah berjalan dengan API endpoint aktif di `http://localhost:1234`

### Konfigurasi

Sesuaikan parameter aplikasi di `config.py`:

- `MAX_WORKERS`: Jumlah thread untuk pemrosesan paralel
- `MAX_TOKENS`: Jumlah token maksimum untuk output LLM
- `TEMPERATURE`: Tingkat kreativitas LLM (nilai rendah untuk respons lebih deterministik)
- `MAX_CONTENT_LENGTH`: Panjang maksimum konten artikel yang akan diproses

### Menjalankan Analisis

1. Pastikan data berita mentah sudah tersedia di `data/news.json`

2. Jalankan analisis dengan perintah:

   ```
   python main.py
   ```

3. Hasil analisis akan disimpan di `output/analysis.json`

### Upload Hasil ke MongoDB

1. Setelah analisis selesai, upload hasil ke MongoDB dengan perintah:

   ```
   python upload_to_mongodb.py
   ```

2. Sistem akan menampilkan log status upload, termasuk entri baru, pembaruan entri yang sudah ada, dan catatan kesalahan.

## Format Data

### Input (data/news.json)

```json
[
  {
    "headline": "BBRI: BRI CATAT LABA BERSIH KONSOLIDASI Rp25,2 TRILIUN HINGGA JULI 2023",
    "link": "http://www.iqplus.info/news/stock_news/bbri-bri-catat-laba-bersih-konsolidasi-rp25-2-triliun-hingga-juli-2023,35010388.html",
    "published_at": "24/08/23 - 14:16",
    "content": "Thursday 24/Aug/2023 at 14:16\nBRI CATAT LABA BERSIH KONSOLIDASI..."
  },
  ...
]
```

### Output (output/analysis.json)

```json
{
  "metadata": {
    "generated_at": "2025-04-18T10:15:30.123456",
    "article_count": 1000,
    "last_updated": "2025-04-18T10:30:45.654321"
  },
  "results": [
    {
      "headline": "BBRI: BRI CATAT LABA BERSIH KONSOLIDASI Rp25,2 TRILIUN HINGGA JULI 2023",
      "effective_date": "2023-08-24T14:16:00.000000",
      "sentiment": "positive",
      "confidence": 0.92,
      "tickers": ["BBRI"],
      "reasoning": "Berita melaporkan laba bersih yang tinggi, menunjukkan kinerja keuangan yang positif",
      "summary": "PT Bank Rakyat Indonesia (Persero) Tbk mencatat laba bersih konsolidasi sebesar Rp25,2 triliun hingga Juli 2023, didukung oleh pertumbuhan penyaluran kredit mikro dan peningkatan pendapatan berbasis komisi."
    },
    ...
  ]
}
```

## Penanganan Error

- Sistem dilengkapi dengan penanganan kesalahan yang akan melanjutkan pemrosesan artikel lain jika satu artikel gagal diproses
- Artikel yang gagal diproses akan tetap disertakan dalam hasil dengan informasi kesalahan
- Untuk upload MongoDB, sistem akan mencatat entri duplikat dan memperbarui data yang sudah ada

## Tips Penggunaan

1. **Pengaturan Thread**: Untuk komputer dengan CPU lebih banyak, tingkatkan nilai `MAX_WORKERS` di `config.py` untuk pemrosesan lebih cepat.

2. **Manajemen Memori**: Jika mengalami masalah memori saat memproses file berita besar, kurangi nilai `MAX_WORKERS`.

3. **Kualitas Analisis**: Untuk analisis yang lebih akurat, turunkan nilai `TEMPERATURE` di `config.py` mendekati 0.

4. **Backup Data**: Lakukan backup regular `output/analysis.json` untuk mencegah kehilangan data.

## Troubleshooting

### LM Studio API tidak tersedia

- Pastikan LM Studio berjalan di mesin lokal
- Verifikasi API endpoint tersedia di `http://localhost:1234`

### Error Koneksi MongoDB

- Periksa kredensial MongoDB di `upload_to_mongodb.py`
- Pastikan jaringan internet berfungsi dengan baik
- Periksa apakah IP Anda diizinkan di pengaturan MongoDB Atlas

### Duplikasi Entri MongoDB

- Sistem secara otomatis menangani duplikasi dengan memperbaharui entri yang sudah ada
- Periksa log untuk melihat status pembaruan entri duplikat

## Kontribusi

Kontribusi untuk project ini sangat disambut. Silakan ikuti langkah-langkah berikut:

1. Fork repositori
2. Buat branch fitur (`git checkout -b fitur-baru`)
3. Commit perubahan Anda (`git commit -am 'Menambahkan fitur baru'`)
4. Push ke branch (`git push origin fitur-baru`)
5. Buat Pull Request baru

## Lisensi

Didistribusikan di bawah lisensi MIT. Lihat `LICENSE` untuk informasi lebih lanjut.

## Kontak

Email: [alamat-email@example.com](mailto:alamat-email@example.com)
