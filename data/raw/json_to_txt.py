import json

# Read the JSON file
with open("khmer_articles.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Create a text file
with open("khmer_articles.txt", "w", encoding="utf-8") as f:
    for article in data:
        f.write(f"Title: {article['title']}\n")
        f.write(f"URL: {article['url']}\n")
        f.write(f"Length: {article['length']} characters\n")
        f.write(f"Source: {article['source']}\n")
        f.write("Content:\n")
        f.write(article["content"])
        f.write("\n" + "=" * 80 + "\n\n")
