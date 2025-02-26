import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

API_KEY = "AIzaSyBLrsbit4JdNYB2vbZvSDB9p7lEWqom8u4"  # Replace with your actual API Key
CX = "f39f147910565420e"  # Replace with your Programmable Search Engine ID

def google_search(query):
    """Fetch Google search results with title, meta description, link, and internal/external link counts."""
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
        page_url = item.get("link", "No link found")
        main_page_name = get_main_page_name(page_url)  # Extract main page (domain) name
        meta_description = get_meta_description(page_url)  # Fetch actual meta description
        full_text_word_count = get_page_word_count(page_url)  # Fetch full page text and count words
        
        # Count internal & outgoing links FROM the page
        internal_links_from_page, outgoing_links_from_page = count_links_from_page(page_url, main_page_name)

        results.append({
            "Title": item.get("title", "No title found"),
            "Main Page Name": main_page_name,
            "Meta Description": meta_description,
            "Full Page Word Count": full_text_word_count,
            "Internal Links from This Page": internal_links_from_page,
            "Outgoing Links from This Page": outgoing_links_from_page,
            "Link": page_url
        })

    return results

def get_main_page_name(url):
    """Extract the main domain name from the URL."""
    parsed_url = urlparse(url)
    return parsed_url.scheme + "://" + parsed_url.netloc  # Returns base domain (e.g., 'https://example.com')

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

def get_page_word_count(url):
    """Fetch the full page text and count words."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.extract()

        full_text = soup.get_text(separator=" ")  # Extract all readable text
        words = full_text.split()  # Split into words
        return len(words)  # Return word count

    except requests.exceptions.RequestException:
        return "Could not retrieve page content"

def count_links_from_page(url, base_domain):
    """Count total internal & outgoing links FROM the given page."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        internal_links = set()
        outgoing_links = set()

        for link in soup.find_all("a", href=True):
            full_link = urljoin(url, link["href"])
            parsed_link = urlparse(full_link)

            if parsed_link.netloc == base_domain:
                internal_links.add(full_link)  # Internal link
            else:
                outgoing_links.add(full_link)  # Outgoing link

        return len(internal_links), len(outgoing_links)

    except requests.exceptions.RequestException:
        return "Could not retrieve links", "Could not retrieve links"

st.title("Google Search Scraper - Internal & Outgoing Links")
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
            st.write(f"**Main Page Name:** {res['Main Page Name']}")
            st.write(f"**Meta Description:** {res['Meta Description']}")
            st.write(f"**Full Page Word Count:** {res['Full Page Word Count']}")
            st.write(f"**Internal Links from This Page:** {res['Internal Links from This Page']}")
            st.write(f"**Outgoing Links from This Page:** {res['Outgoing Links from This Page']}")
            st.write(f"[Link]({res['Link']})")
