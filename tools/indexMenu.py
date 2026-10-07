"""
tools/index_menu.py

Incrementally index menu items into ChromaDB.

Existing dishes are skipped.
Only new dishes are embedded and added.
"""

from langchain_core.documents import Document

from data.menu import MENU_CATALOG
from tools.rag import vectorstore


def menu_item_to_document(item: dict) -> Document:
    """
    Convert one menu item into a LangChain Document.
    """

    content = (
        f"Dish: {item['name']}\n"
        f"Category: {item['category']}\n"
        f"Cuisine: {item['cuisine']}\n"
        f"Price: ${item['price']:.2f}\n"
        f"Rating: {item['rating']}/5\n"
        f"Dietary: "
        f"{', '.join(item['dietary_tags']) if item['dietary_tags'] else 'None'}\n"
        f"Description: {item['description']}\n"
        f"Available: {'Yes' if item['available'] else 'No'}"
    )

    return Document(
        page_content=content,
        metadata={
            "id": item["id"],
            "name": item["name"],
            "category": item["category"],
            "cuisine": item["cuisine"],
            "price": item["price"],
            "rating": item["rating"],
            "available": item["available"],
        },
    )


def index_menu():
    """
    Add only new menu items to ChromaDB.
    """

    # Get records already stored in Chroma
    existing_records = vectorstore.get()

    existing_ids = set(existing_records["ids"])

    print(f"Existing dishes in ChromaDB: {len(existing_ids)}")

    new_documents = []
    new_ids = []

    for item in MENU_CATALOG:

        dish_id = item["id"]

        if dish_id in existing_ids:
            print(f"Skipping existing dish: {dish_id} - {item['name']}")
            continue

        print(f"New dish found: {dish_id} - {item['name']}")

        document = menu_item_to_document(item)

        new_documents.append(document)
        new_ids.append(dish_id)

    # Nothing new
    if not new_documents:
        print("Menu index is already up to date.")
        return

    # Only NEW documents are embedded here
    vectorstore.add_documents(
        documents=new_documents,
        ids=new_ids,
    )

    print(f"Added {len(new_documents)} new dishes to ChromaDB.")


if __name__ == "__main__":
    index_menu()