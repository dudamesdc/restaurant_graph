import json
import os
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

    html_items = soup.find_all("div", class_="text-card-foreground")

    print(f"Starting extraction of {len(html_items)} items...")

    for item in html_items:
        title_tag = item.find("h6")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"

        desc_tag = item.find("span", class_="line-clamp-2")
        description = desc_tag.get_text(strip=True) if desc_tag else "No description"

        category_tag = item.find_previous("h5", class_="category-heading")
        category = category_tag.get_text(strip=True) if category_tag else "Others"

        price_tag = item.find("strong")
        price = "Consult"
        if price_tag:
            price = price_tag.parent.get_text(strip=True).replace("\xa0", " ")

        menu.append(
            {
                "categoria": category,
                "prato": title,
                "descricao": description,
                "preco": price,
            }
        )

    with open(BAMBU_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(menu, f, indent=4, ensure_ascii=False)

    print(f"Done! Data saved in {BAMBU_OUTPUT}")


def camaroes_scraper():
    cameroon_dir = "data/cameroon"
    if not os.path.exists(cameroon_dir):
        print(f"Error: Directory {cameroon_dir} not found.")
        return

    output_dir = "json_graphs/cameroon"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(cameroon_dir):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(cameroon_dir, filename)
        output_file = os.path.join(output_dir, filename.replace(".txt", ".json"))

        print(f"Extracting {file_path}...")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                html = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        soup = BeautifulSoup(html, "html.parser")
        product_list = []
        html_products = soup.find_all("div", class_="product")

        for p in html_products:
            cat_tag = p.find_previous(class_="category-title")
            category = cat_tag.get_text(strip=True) if cat_tag else "General"

            name_tag = p.find("span", class_="product-title")
            name = name_tag.get_text(strip=True) if name_tag else "No name"

            desc_tag = p.find("p", class_="description")
            description = (
                desc_tag.get_text(separator=" ", strip=True) if desc_tag else ""
            )

            additional_info = p.find("div", class_="product-additional-info")
            price = "0,00"
            if additional_info:
                price_tag = additional_info.find("span")
                if price_tag:
                    price = price_tag.get_text(strip=True).replace("R$", "").strip()

            product_list.append(
                {
                    "categoria": category,
                    "prato": name,
                    "descricao": description,
                    "preco": price,
                }
            )

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(product_list, f, indent=4, ensure_ascii=False)
        print(f"Success! {len(product_list)} items saved to {output_file}")


if __name__ == "__main__":
    bambu_scraper()
    camaroes_scraper()
