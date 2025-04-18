# Transformasi Laporan Keuangan

Notebook PySpark untuk mentransformasi data laporan keuangan XML dari Bursa Efek Indonesia (IDX) menjadi format terstruktur yang konsisten, dengan atribut-atribut penting yang disesuaikan berdasarkan sektor industri.

## Deskripsi

Proyek ini merupakan bagian dari Tugas 2 mata kuliah Big Data Platform yang bertujuan untuk mengolah dan menyederhanakan data laporan keuangan perusahaan publik dari IDX. Data laporan keuangan aslinya berformat XML yang kompleks dan memiliki struktur berbeda untuk masing-masing sektor industri. Transformasi ini menyeragamkan struktur data dan mengekstrak informasi keuangan penting untuk kemudahan analisis.

## Fitur Utama

- Transformasi data laporan keuangan XML menjadi format JSON terstruktur
- Ekstraksi atribut-atribut keuangan penting secara spesifik per sektor industri
- Dukungan untuk berbagai sektor industri:
  - Perbankan (G1. Banks)
  - Jasa Keuangan (G2. Financing Service)
  - Jasa Investasi (G3. Investment Service)
  - Asuransi (G4. Insurance)
  - Sektor Lainnya (non-keuangan)
- Penyimpanan hasil transformasi ke MongoDB
- Penanganan perhitungan nilai untuk kolom yang hilang atau tidak lengkap

## Struktur Proyek

```
transformasi_lapkeu/
├── Transformasi Lapkeu.ipynb  # Notebook Jupyter untuk transformasi data
└── json/                      # Direktori untuk data mentah
    └── lapkeu_tahunan_2024.json # Data laporan keuangan tahunan 2024
```

## Persyaratan Sistem

- Python 3.9 atau lebih baru
- Apache Spark 3.x
- Hadoop (untuk koneksi MongoDB)
- MongoDB (lokal)
- Jupyter Notebook atau JupyterLab
- Pustaka Python: pyspark, pandas, os, logging

## Cara Menggunakan

### Persiapan Awal

1. Kloning repositori:

   ```
   git clone https://github.com/username/tugas2-bigdata-2-2025.git
   cd tugas2-bigdata-2-2025/transformasi_lapkeu
   ```

2. Pasang dependensi yang diperlukan:

   ```
   pip install pyspark pandas jupyter
   ```

3. Pastikan MongoDB berjalan di localhost:27017

4. Pastikan Hadoop diinstal dan terkonfigurasi dengan benar

### Menjalankan Transformasi

1. Buka notebook Jupyter di lingkungan pengembangan Anda:

   ```
   jupyter notebook "Transformasi Lapkeu.ipynb"
   ```

2. Jalankan semua sel di notebook secara berurutan

3. Notebook akan:
   - Terhubung ke MongoDB
   - Membaca data laporan keuangan dari koleksi yang ditentukan
   - Melakukan transformasi berdasarkan sektor industri
   - Menyimpan hasil transformasi ke koleksi MongoDB baru (`2024_transformed`)

## Detail Transformasi per Sektor

### 1. Perbankan (G1. Banks)

Mengekstrak atribut keuangan spesifik perbankan seperti:

- Interest Income dan Sharia Income sebagai revenue
- Profit from Operation
- Assets dan Equity
- Short-term dan Long-term Borrowing
- Cash flow dari operasi, investasi, dan pendanaan

### 2. Jasa Keuangan (G2. Financing Service)

Atribut keuangan yang diekstrak meliputi:

- Income dari Murabahah, Consumer Financing, dll
- Profit Loss Before Income Tax
- Cash and Cash Equivalents
- Borrowings dan Bonds Payable
- Cash flow dari operasi, investasi, dan pendanaan

### 3. Jasa Investasi (G3. Investment Service)

Mengekstrak:

- Income dari Brokerage, Underwriting, dan Investment Management
- Profit Loss Before Income Tax dan Net Profit
- Assets dan Liabilities
- Bank Loans
- Cash flow dari operasi, investasi, dan pendanaan

### 4. Asuransi (G4. Insurance)

Atribut keuangan meliputi:

- Revenue from Insurance Premiums
- Claim Expenses
- Insurance Liabilities
- Assets dan Equity
- Cash flow dari operasi, investasi, dan pendanaan

### 5. Sektor Lainnya

Untuk sektor non-finansial (manufaktur, ritel, dll):

- Sales and Revenue
- Gross Profit
- Operating Profit dan Net Profit
- Short-term dan Long-term Bank Loans
- Assets dan Liabilities
- Cash flow dari operasi, investasi, dan pendanaan

## Format Data Output

Data output disimpan dalam format terstruktur dengan kolom yang konsisten:

```json
{
  "entity_name": "PT Bank Rakyat Indonesia Tbk",
  "emiten": "BBRI",
  "report_date": "2024-03-31",
  "revenue": 47382193,
  "gross_profit": 18926714,
  "operating_profit": 18926714,
  "net_profit": 14146653,
  "cash": 45678219,
  "total_assets": 1892673461,
  "short_term_borrowing": 142376594,
  "long_term_borrowing": 27658291,
  "total_equity": 329467912,
  "liabilities": 1563205549,
  "cash_dari_operasi": 24678293,
  "cash_dari_investasi": -15463728,
  "cash_dari_pendanaan": 5628475
}
```

## Tantangan dan Solusi

- **Struktur Data Berbeda**: Solusi dengan implementasi filter kondisional berdasarkan subsektor
- **Nilai yang Hilang**: Implementasi fungsi helper `calculate_sum_if_exists` untuk menangani nilai null
- **Perbedaan Format Pelaporan**: Transformasi khusus per sektor dengan mapping atribut yang berbeda
- **Ukuran Data Besar**: Penggunaan Apache Spark untuk memproses data laporan keuangan secara efisien

## Kontribusi

Kontribusi untuk proyek ini sangat disambut. Silakan ikuti langkah-langkah berikut:

1. Fork repositori
2. Buat branch fitur (`git checkout -b fitur-baru`)
3. Commit perubahan Anda (`git commit -am 'Menambahkan fitur baru'`)
4. Push ke branch (`git push origin fitur-baru`)
5. Buat Pull Request baru

## Lisensi

Didistribusikan di bawah lisensi MIT. Lihat `LICENSE` untuk informasi lebih lanjut.
