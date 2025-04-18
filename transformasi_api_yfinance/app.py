from flask import Flask, jsonify, abort
from pymongo import MongoClient
from flask_cors import CORS  # Mengaktifkan CORS untuk mengizinkan akses dari domain lain

# Inisialisasi aplikasi Flask
app = Flask(__name__)
CORS(app)  # Mengaktifkan CORS untuk aplikasi React

# Koneksi ke MongoDB lokal
client = MongoClient("mongodb://localhost:27017")  # Koneksi ke MongoDB lokal
db = client["stock_data"]  # Menggunakan database "stock_data"

# API untuk mengambil data saham berdasarkan emiten dan kolom untuk daily
@app.route('/api/daily/<ticker>/<column>', methods=['GET'])
def get_stock_data_daily(ticker, column):
    collection = db["daily_aggregation_ticker"]  # Mengakses koleksi daily_aggregation_ticker
    return get_stock_data(collection, ticker, column)

# API untuk mengambil data saham berdasarkan emiten dan kolom untuk monthly
@app.route('/api/monthly/<ticker>/<column>', methods=['GET'])
def get_stock_data_monthly(ticker, column):
    collection = db["monthly_aggregation_ticker"]  # Mengakses koleksi monthly_aggregation_ticker
    return get_stock_data(collection, ticker, column)

# API untuk mengambil data saham berdasarkan emiten dan kolom untuk yearly (tahunan)
@app.route('/api/yearly/<ticker>/<column>', methods=['GET'])
def get_stock_data_yearly(ticker, column):
    collection = db["yearly_aggregation_ticker"]  # Mengakses koleksi yearly_aggregation_ticker
    return get_stock_data(collection, ticker, column)

# Fungsi untuk mengambil data saham berdasarkan emiten dan kolom yang diminta
def get_stock_data(collection, ticker, column):
    # Mengambil data berdasarkan ticker dan kolom yang diminta
    if collection.name == "daily_aggregation_ticker":
        # Mengambil data daily
        data = collection.find({"ticker": ticker}, {"_id": 0, "Date": 1, column: 1}).limit(100)
    elif collection.name == "monthly_aggregation_ticker":
        # Mengambil data monthly
        data = collection.find({"ticker": ticker}, {"_id": 0, "Year": 1, "Month": 1, column: 1}).limit(100)
    elif collection.name == "yearly_aggregation_ticker":
        # Mengambil data yearly
        data = collection.find({"ticker": ticker}, {"_id": 0, "Year": 1, column: 1}).limit(100)
    
    # Jika tidak ada data ditemukan, kirim error 404
    if data.count() == 0:
        abort(404, description="Ticker not found")

    # Menyusun data untuk dikirim dalam format JSON
    if collection.name == "daily_aggregation_ticker":
        stock_data = [{"Date": item["Date"], column: item.get(column, "Column not available")} for item in data]
    elif collection.name == "monthly_aggregation_ticker":
        stock_data = [{"Year": item["Year"], "Month": item["Month"], column: item.get(column, "Column not available")} for item in data]
    elif collection.name == "yearly_aggregation_ticker":
        stock_data = [{"Year": item["Year"], column: item.get(column, "Column not available")} for item in data]

    return jsonify(stock_data)  # Mengembalikan data dalam format JSON

# Menangani kesalahan 404 jika ticker tidak ditemukan
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": str(error)}), 404

if __name__ == '__main__':
    app.run(debug=True)  # Menjalankan aplikasi Flask di localhost:5000
