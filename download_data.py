import gdown
import os

# Google Drive direct download link
url = "https://drive.google.com/uc?id=1JhbFj29mP-729WG19WCrRQxgcGwKyPH6"

os.makedirs("data", exist_ok=True)
output = "data/nbpdcl1_data.csv"

gdown.download(url, output, quiet=False)

print("✅ Dataset downloaded successfully")
