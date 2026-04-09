
import sqlite3
import pandas as pd
import ast

conn = sqlite3.connect("ria_menu44.db")

df = pd.read_sql_query("SELECT * FROM menu", conn)
df = df.drop(columns=["img_url"])

df["nutrition"] = df["nutrition"].apply(
    lambda x: ast.literal_eval(x) if x and x.strip().startswith("{") else {}
)

df.to_json("ria_menu2.json", orient="records", force_ascii=False, indent=2)

print("JSON 저장 완료")