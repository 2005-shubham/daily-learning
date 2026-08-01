import google.generativeai as genai
import os
from datetime import datetime

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

today = datetime.now().strftime("%Y-%m-%d")

os.makedirs("notes", exist_ok=True)

filename = f"notes/{today}.md"

if not os.path.exists(filename):

    prompt = f"""
Generate a markdown note for today's learning.

Choose ONE topic randomly from:
- Python
- Java
- JavaScript
- React
- Node.js
- Express
- MongoDB
- SQL
- Linux
- Git
- GitHub
- Docker
- AWS
- Terraform
- Data Structures
- Algorithms
- DevOps

Requirements:
- Title
- Explanation
- Example
- Interview Tip
- Around 300-500 words
- Markdown format
"""

    response = model.generate_content(prompt)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(response.text)

print("Done")
