import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

API_KEY = "AIzaSyBLrsbit4JdNYB2vbZvSDB9p7lEWqom8u4"  # Replace with your actual API Key
CX = "f39f147910565420e"  # Replace with your Programmable Search Engine ID

def google_search(query):
    """Fetch Google search results with title, meta description, link, and internal link count."""
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
    top_10_links = [item.get("link", "No link found") for item in data["items"]]

    for item in data["items"]:
        page_url = item.get("link", "No link found")
        main_page_name = get_main_page_name(page_url)  # Extract main page (domain) name
        meta_description = get_meta_description(page_url)  # Fetch actual meta description
        full_text_word_count = get_page_word_count(page_url)  # Fetch full page text and count words
        
        # Crawl the whole domain and count internal links pointing to this specific page
        internal_links_pointing_to_page = crawl_website_for_internal_links(main_page_name, page_url, depth=3)

        results.append({
            "Title": item.get("title", "No title found"),
            "Main Page Name": main_page_name,
            "Meta Description": meta_description,
            "Full Page Word Count": full_text_word_count,
            "Internal Links to This Page (Whole Site)": internal_links_pointing_to_page,
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

def crawl_website_for_internal_links(start_url, target_page, depth=3):
    """Crawl the entire website and count internal links pointing to the target page."""
    base_domain = urlparse(start_url).netloc
    to_crawl = {start_url}  # Start crawling from homepage
    crawled = set()
    internal_links_pointing_to_target = 0

    while to_crawl and depth > 0:
        current_page = to_crawl.pop()
        if current_page in crawled:
            continue

        crawled.add(current_page)
        depth -= 1  # Reduce crawling depth

        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(current_page, headers=headers, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            for link in soup.find_all("a", href=True):
                full_link = urljoin(current_page, link["href"])
                parsed_link = urlparse(full_link)

                # Keep only links within the same domain
                if parsed_link.netloc == base_domain:
                    if full_link == target_page:
                        internal_links_pointing_to_target += 1  # Count links to the target page
                    if full_link not in crawled:
                        to_crawl.add(full_link)

        except requests.exceptions.RequestException:
            continue  # Skip failed requests

    return internal_links_pointing_to_target

st.title("Google Search Scraper - Internal Links (Whole Domain)")
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
            st.write(f"**Internal Links to This Page (Whole Site):** {res['Internal Links to This Page (Whole Site)']}")
            st.write(f"[Link]({res['Link']})")

