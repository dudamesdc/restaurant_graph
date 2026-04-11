import json
from bs4 import BeautifulSoup


BAMBU_FILE = "data/bambu.txt" 
CAMAROES_FILE = "data/camaroon.txt"
BAMBU_OUTPUT = "json_graphs/bambu.json"
CAMAROES_OUTPUT = "json_graphs/camaroon.json"

def bambu_scraper():

    try:
        with open(BAMBU_FILE, "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: The file {BAMBU_FILE} was not found in the folder.")
        return

    soup = BeautifulSoup(html_content, "html.parser")
    menu = []

   
    # In the HTML you sent, the items are in divs with the class 'text-card-foreground'
    html_items = soup.find_all("div", class_="text-card-foreground")

    print(f"Starting extraction of {len(html_items)} items...")

    for item in html_items:
        # Extract Title (h6)
        title_tag = item.find("h6")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"

        # Extract Description (span)
        desc_tag = item.find("span", class_="line-clamp-2")
        description = desc_tag.get_text(strip=True) if desc_tag else "No description"

        # Extract Category (h5)
        # The find_previous method searches for the first h5 (category) that appeared before this item
        category_tag = item.find_previous("h5", class_="category-heading")
        category = category_tag.get_text(strip=True) if category_tag else "Others"

        # Extract Price (inside a strong or price div)
        price_tag = item.find("strong")
        price = "Consult"
        if price_tag:
            # Gets the text from the strong's parent to get the full value: "R$ 74,00"
            price = price_tag.parent.get_text(strip=True).replace('\xa0', ' ')

        # Add to dictionary
        menu.append({
            "categoria": category,
            "prato": title,
            "descricao": description,
            "preco": price
        })

  
    with open(BAMBU_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(menu, f, indent=4, ensure_ascii=False)

    print(f"Done! Data saved in {BAMBU_OUTPUT}")

def camaroes_scraper():
    try:
        with open(CAMAROES_FILE, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        print("Error: File not found.")
        return

    soup = BeautifulSoup(html, "html.parser")
    product_list = []

    # Find all products
    html_products = soup.find_all("div", class_="product")

    for p in html_products:
        # CATEGORY EXTRACTION
        cat_tag = p.find_previous(class_="category-title")
        category = cat_tag.get_text(strip=True) if cat_tag else "General"

        # DISH EXTRACTION
        name_tag = p.find("span", class_="product-title")
        name = name_tag.get_text(strip=True) if name_tag else "No name"

        # DESCRIPTION EXTRACTION
        desc_tag = p.find("p", class_="description")
        description = desc_tag.get_text(separator=" ", strip=True) if desc_tag else ""

        # PRICE EXTRACTION
        additional_info = p.find("div", class_="product-additional-info")
        price = "0,00"
        if additional_info:
            price_tag = additional_info.find("span")
            if price_tag:
                # Clears "R$" and spaces to facilitate future calculations
                price = price_tag.get_text(strip=True).replace("R$", "").strip()

        product_list.append({
            "categoria": category,
            "prato": name,
            "descricao": description,
            "preco": price
        })

    # Save the structured result
    with open(CAMAROES_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(product_list, f, indent=4, ensure_ascii=False)

    print(f"Success! {len(product_list)} items processed with their categories.")

if __name__ == "__main__":
    bambu_scraper()
    camaroes_scraper()