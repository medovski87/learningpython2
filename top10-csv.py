import streamlit as st
import requests
import csv
import json

API_KEY = "AIzaSyBLrsbit4JdNYB2vbZvSDB9p7lEWqom8u4"  # Replace with your actual API Key
CX = "f39f147910565420e"  # Replace with your Programmable Search Engine ID

def google_search(query):
    """Fetch Google search results with title, description, and link."""
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
        results.append({
            "Title": item.get("title", "No title found"),
            "Description": item.get("snippet", "No description found"),
            "Link": item.get("link", "No link found")
        })

    return results

st.title("Google Search Scraper")
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
            st.write(f"**Description:** {res['Description']}")
            st.write(f"[Link]({res['Link']})")

