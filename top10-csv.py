import streamlit as st
import requests
import json
from bs4 import BeautifulSoup

API_KEY = "AIzaSyBLrsbit4JdNYB2vbZvSDB9p7lEWqom8u4"  # Replace with your actual API Key
CX = "f39f147910565420e"  # Replace with your Programmable Search Engine ID

def google_search(query):
    """Fetch Google search results with title, meta description, and link."""
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {e}"

    try:
        data = response.json()
    except json.JSONDecodeError:
        return "Error decoding JSON response."

    if "items" not in data:
        return "No results found."

    results = []
    for item in data["items"]:
        link = item.get("link", "No link found")
        meta_description = get_meta_description(link)  # Fetch actual meta description
        word_count = len(meta_description.split()) if meta_description else 0  # Count words

        results.append({
            "Title": item.get("title", "No title found"),
            "Meta Description": meta_description,
            "Word Count": word_count,
            "Link": link
        })

    return results

def get_meta_description(url):
    """Fetch the actual meta description from the page source."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and "content" in meta_tag.attrs:
            return meta_tag["content"]
    except requests.exceptions.RequestException:
        return "Could not retrieve meta description"
    return "No meta description found"

st.title("Google Search Scraper with Meta Descriptions")
query = st.text_input("Enter search keyword:")

if st.button("Search"):
    results = google_search(query)
    if isinstance(results, str):
        st.error(results)
    elif results:
        st.success("Results found!")
        for i, res in enumerate(results, 1):
            st.subheader(f"Result {i}")
            st.write(f"**Title:** {res['Title']}")
            st.write(f"**Meta Description:** {res['Meta Description']}")
            st.write(f"**Word Count:** {res['Word Count']}")
            st.write(f"[Link]({res['Link']})")
