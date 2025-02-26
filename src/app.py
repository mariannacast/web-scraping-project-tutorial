import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# Step 1: Download HTML
url = "https://companies-market-cap-copy.vercel.app/index.html"
response = requests.get(url)

if response.status_code == 200:
    html_content = response.text
    print(f"HTML Content Length: {len(html_content)}")
else:
    print(f"Failed to retrieve page. Status code: {response.status_code}")
    exit()

# Step 2: Parse HTML
soup = BeautifulSoup(html_content, "html.parser")
table = soup.find("table")

if not table:
    print("Error: No table found!")
    exit()

# Step 3: Extract Table Data
rows = table.find_all("tr")
data = []
for row in rows[1:]:
    cols = row.find_all("td")
    if len(cols) >= 2:  # Ensure at least 2 columns exist
        date = cols[0].text.strip()
        revenue = cols[1].text.strip()
        data.append([date, revenue])

# Step 4: Create DataFrame
df = pd.DataFrame(data, columns=["Date", "Revenue"])

# Step 5: Clean Data
df["Revenue"] = df["Revenue"].str.replace("[$B]", "", regex=True)
df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce")
df_cleaned = df.dropna()

print("Final DataFrame:")
print(df_cleaned.head())

# Step 6: Store Data in SQLite
conn = sqlite3.connect("scraped_data.db")
cursor = conn.cursor()

# Create Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS revenue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    revenue REAL
)
""")

# Insert Data
for _, row in df_cleaned.iterrows():
    cursor.execute("INSERT INTO revenue (date, revenue) VALUES (?, ?)", (row["Date"], row["Revenue"]))

conn.commit()
conn.close()

# Step 7: Plot Data
plt.figure(figsize=(10, 6))
plt.plot(df_cleaned["Date"], df_cleaned["Revenue"], marker='o', label="Revenue")
plt.title("Company Revenue Over Time")
plt.xlabel("Date")
plt.ylabel("Revenue in billions (USD)")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)

# Save and Show Plot
plt.savefig("revenue_plot.png")
plt.show()
