from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return "Quora Scraper is ready!"

@app.route('/scrape')
def scrape():
    url = request.args.get("url")
    limit = int(request.args.get("limit", 10))  # Default to 10 if not provided

    if not url:
        return jsonify({"error": "Missing 'url' query parameter"}), 400

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(5000)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    results = []

    for div in soup.select("div.q-box.qu-mb--tiny"):
        question = div.text.strip()
        a_tag = div.find("a", href=True)
        if a_tag and question:
            results.append({
                "question": question,
                "link": f"https://www.quora.com{a_tag['href']}"
            })
        if len(results) >= limit:
            break

    return jsonify(results)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
