from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# Inisialisasi Spark session
spark = SparkSession.builder \
    .appName("MongoDB Integration") \
    .config("spark.mongodb.input.uri", "mongodb://localhost:27017/stock_data.idx_emiten") \
    .config("spark.mongodb.output.uri", "mongodb://localhost:27017/stock_data.idx_emiten") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .getOrCreate()

# Membaca data dari MongoDB koleksi
df = spark.read.format("mongo").load()

# Mengonversi kolom 'Date' menjadi tipe tanggal yang benar
df = df.withColumn("Date", F.to_date(F.col("Date")))

# 1. Agregasi Harian (per hari), berdasarkan ticker
df_daily = df.groupBy("Date", "ticker").agg(
    F.avg("Open").alias("avg_open"),
    F.avg("High").alias("avg_high"),
    F.avg("Low").alias("avg_low"),
    F.avg("Close").alias("avg_close"),
    F.avg("Volume").alias("avg_volume"),
    F.avg("Dividends").alias("avg_dividends"),
    F.avg("Stock Splits").alias("avg_stock_splits")
)

# Menyimpan hasil agregasi harian ke MongoDB
df_daily.write.format("mongo") \
    .option("uri", "mongodb://localhost:27017") \
    .option("database", "stock_data") \
    .option("collection", "daily_aggregation_ticker") \
    .mode("overwrite") \
    .save()

# print("Harian agregasi per ticker berhasil disimpan ke MongoDB!")

# 2. Agregasi Bulanan (per bulan), berdasarkan ticker
df_monthly = df.withColumn("Year", F.year(F.col("Date"))) \
               .withColumn("Month", F.month(F.col("Date"))) \
               .groupBy("Year", "Month", "ticker").agg(
                   F.avg("Open").alias("avg_open"),
                   F.avg("High").alias("avg_high"),
                   F.avg("Low").alias("avg_low"),
                   F.avg("Close").alias("avg_close"),
                   F.avg("Volume").alias("avg_volume"),
                   F.avg("Dividends").alias("avg_dividends"),
                   F.avg("Stock Splits").alias("avg_stock_splits")
               )

# Menyimpan hasil agregasi bulanan ke MongoDB
df_monthly.write.format("mongo") \
    .option("uri", "mongodb://localhost:27017") \
    .option("database", "stock_data") \
    .option("collection", "monthly_aggregation_ticker") \
    .mode("overwrite") \
    .save()

# print("Bulanan agregasi per ticker berhasil disimpan ke MongoDB!")

# 3. Agregasi Tahunan (per tahun), berdasarkan ticker
df_yearly = df.withColumn("Year", F.year(F.col("Date"))) \
              .groupBy("Year", "ticker").agg(
                  F.avg("Open").alias("avg_open"),
                  F.avg("High").alias("avg_high"),
                  F.avg("Low").alias("avg_low"),
                  F.avg("Close").alias("avg_close"),
                  F.avg("Volume").alias("avg_volume"),
                  F.avg("Dividends").alias("avg_dividends"),
                  F.avg("Stock Splits").alias("avg_stock_splits")
              )

# Menyimpan hasil agregasi tahunan ke MongoDB
df_yearly.write.format("mongo") \
    .option("uri", "mongodb://localhost:27017") \
    .option("database", "stock_data") \
    .option("collection", "yearly_aggregation_ticker") \
    .mode("overwrite") \
    .save()

# print("Tahunan agregasi per ticker berhasil disimpan ke MongoDB!")

# 4. Agregasi 2 Tahun (per 2 tahun), berdasarkan ticker
df_2year = df.withColumn("Year", F.year(F.col("Date"))) \
             .withColumn("YearRange", F.concat_ws("-", 
                 F.floor(F.col("Year") / 2) * 2,
                 F.floor(F.col("Year") / 2) * 2 + 1)) \
             .groupBy("YearRange", "ticker").agg(
                 F.avg("Open").alias("avg_open"),
                 F.avg("High").alias("avg_high"),
                 F.avg("Low").alias("avg_low"),
                 F.avg("Close").alias("avg_close"),
                 F.avg("Volume").alias("avg_volume"),
                 F.avg("Dividends").alias("avg_dividends"),
                 F.avg("Stock Splits").alias("avg_stock_splits")
             )

# Menyimpan hasil agregasi 2 tahunan ke MongoDB
df_2year.write.format("mongo") \
    .option("uri", "mongodb://localhost:27017") \
    .option("database", "stock_data") \
    .option("collection", "2year_aggregation_ticker") \
    .mode("overwrite") \
    .save()

print("2 Tahun agregasi per ticker berhasil disimpan ke MongoDB!")


