import os
import json
import random
import logging
from datetime import datetime
from pathlib import Path

import google.generativeai as genai

# -----------------------------------------------------
# Configuration
# -----------------------------------------------------

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found!")

genai.configure(api_key=API_KEY)

MODEL = genai.GenerativeModel("gemini-2.5-flash")

ROOT = Path(__file__).parent

TOPIC_FILE = ROOT / "topics.json"

NOTES_DIR = ROOT / "notes"

README_FILE = ROOT / "README.md"

HISTORY_FILE = ROOT / "history.json"

NOTES_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# -----------------------------------------------------
# Load Topics
# -----------------------------------------------------

def load_topics():

    with open(TOPIC_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["topics"]


# -----------------------------------------------------
# History
# -----------------------------------------------------

def load_history():

    if not HISTORY_FILE.exists():
        return []

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_history(history):

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)


# -----------------------------------------------------
# Random Topic
# -----------------------------------------------------

def choose_topic():

    topics = load_topics()

    history = load_history()

    recent = history[-15:]

    available = [t for t in topics if t not in recent]

    if not available:
        available = topics

    topic = random.choice(available)

    history.append(topic)

    save_history(history)

    return topic


# -----------------------------------------------------
# Today's filename
# -----------------------------------------------------

def today_filename():

    today = datetime.utcnow().strftime("%Y-%m-%d")

    return NOTES_DIR / f"{today}.md"


# -----------------------------------------------------
# Already Generated?
# -----------------------------------------------------

def already_exists():

    return today_filename().exists()


# -----------------------------------------------------
# README updater
# -----------------------------------------------------

def update_readme(topic):

    today = datetime.utcnow().strftime("%Y-%m-%d")

    history = load_history()

    total = len(history)

    readme = f"""# Daily Learning Repository

Automatically generated using **Gemini AI**

---

## Latest Update

**Date:** {today}

**Today's Topic:** {topic}

**Total Notes Generated:** {total}

---

This repository automatically generates learning notes every day using GitHub Actions.
"""

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(readme)

# -----------------------------------------------------
# Prompt Builder
# -----------------------------------------------------

def build_prompt(topic):

    return f"""
You are an expert software engineer and technical educator.

Create a professional GitHub learning note in Markdown.

Topic:
{topic}

The note must be around 700-1200 words.

Follow this exact structure.

# {topic}

## What is it?

Explain in simple language.

---

## Why is it important?

Explain practical usage.

---

## Real World Example

Give one practical example.

---

## Syntax / Example

Provide clean code examples.

If the topic is not code related,
provide configuration examples.

---

## Advantages

- Point 1
- Point 2
- Point 3

---

## Disadvantages

- Point 1
- Point 2

---

## Common Interview Questions

At least five questions.

---

## Beginner Mistakes

Explain common mistakes.

---

## Best Practices

Provide industry level practices.

---

## Mini Quiz

Create 5 MCQs with answers.

---

## Practice Task

Give one small project/task.

---

## Summary

Summarize everything.

Only return Markdown.

Do not wrap inside triple backticks.

"""


# -----------------------------------------------------
# Generate Markdown
# -----------------------------------------------------

def generate_markdown(topic):

    logging.info(f"Generating note for {topic}")

    prompt = build_prompt(topic)

    response = MODEL.generate_content(prompt)

    return response.text


# -----------------------------------------------------
# Save Markdown
# -----------------------------------------------------

def save_markdown(content):

    filename = today_filename()

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    logging.info(f"Saved {filename}")

    return filename


# -----------------------------------------------------
# Today's Summary
# -----------------------------------------------------

def print_summary(topic, filename):

    print()

    print("=" * 60)

    print("Daily Learning Note Generated")

    print("=" * 60)

    print(f"Topic : {topic}")

    print(f"File  : {filename.name}")

    print("=" * 60)

    print()


# -----------------------------------------------------
# API Retry
# -----------------------------------------------------

def safe_generate(topic):

    try:

        return generate_markdown(topic)

    except Exception as e:

        logging.warning("First attempt failed.")

        logging.warning(str(e))

        try:

            return generate_markdown(topic)

        except Exception as e:

            logging.error("Second attempt failed.")

            raise e

# -----------------------------------------------------
# Update README
# -----------------------------------------------------

def update_readme(topic, filename):

    readme = f"""# Daily Learning

🤖 This repository is automatically updated every day and tells about daily learning.

## Today's Topic

**{topic}**

Latest Note:

- [{filename.name}](notes/{filename.name})

---

Generated Automatically
"""

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)


# -----------------------------------------------------
# Main Program
# -----------------------------------------------------

def main():

    topic = random_topic()

    filename = today_filename()

    # Skip if today's note already exists
    if filename.exists():

        print("Today's note already exists.")
        return

    markdown = safe_generate(topic)

    save_markdown(markdown)

    update_readme(topic, filename)

    print_summary(topic, filename)


# -----------------------------------------------------
# Run
# -----------------------------------------------------

if __name__ == "__main__":

    main()


print("Initialization Complete")
