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
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return []

    if "items" not in data:
        print("\nNo search results found. Full API response for debugging:")
        print(json.dumps(data, indent=4))  # Prints API response in readable format
        return []

    results = []
    for item in data["items"]:
        results.append({
            "Title": item.get("title", "No title found"),  # Capitalized keys to match CSV fieldnames
            "Description": item.get("snippet", "No description found"),
            "Link": item.get("link", "No link found")
        })

    return results

def save_to_csv(filename, data):
    """Save search results to a CSV file."""
    if not data:  # Prevents writing an empty CSV file
        print("\n⚠️ No data to save. CSV file will not be created.")
        return

    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["Title", "Description", "Link"])  # Fieldnames must match exactly
            writer.writeheader()
            writer.writerows(data)
        
        print(f"\n✅ Search results successfully saved to: {filename}")

        # Debugging: Read and print CSV contents
        print("\n🔹 Checking CSV file contents:")
        with open(filename, mode="r", encoding="utf-8") as file:
            print(file.read())

    except Exception as e:
        print(f"⚠️ Error saving CSV file: {e}")

if __name__ == "__main__":
    while True:
        keyword = input("\nEnter search keyword (or type 'exit' to quit): ").strip()
        if keyword.lower() == "exit":
            print("\nExiting program. Goodbye!")
            break  # Exit the loop properly

        results = google_search(keyword)

        if results:
            # Save to CSV
            filename = f"google_results_{keyword.replace(' ', '_')}.csv"
            save_to_csv(filename, results)

            # Print Results in Terminal
            print("\n🔹 First page Google search results:")
            for i, res in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"Title: {res['Title']}")
                print(f"Description: {res['Description']}")
                print(f"Link: {res['Link']}")
        else:
            print("\n⚠️ No results found.")

    input("\nPress Enter to exit...")  # Ensures console stays open
