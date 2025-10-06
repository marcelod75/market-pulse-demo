# dbx_etl_news.py (stub)
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date

spark = SparkSession.builder.appName("market-pulse-etl").getOrCreate()
df = spark.read.json("dbfs:/mnt/raw/news/*.json")
df = df.dropDuplicates(["id"]).withColumn("dt_partition", to_date(col("published_at")))
df.write.mode("overwrite").partitionBy("dt_partition").parquet("dbfs:/mnt/curated/news")
print("ETL ok")
