from langchain_core.tools import tool

from tools.rag import menu_retriever


@tool
def search_menu_catalog(query: str) -> str:
    """
    Search the FoodLoop menu for dishes that match the customer's request.

    Use this tool for:
    - finding dishes by cuisine
    - dietary preferences
    - price preferences
    - dish type
    - food recommendations

    Args:
        query: Customer's menu search request.

    Returns:
        Matching menu items from the FoodLoop menu.
    """

    documents = menu_retriever.invoke(query)

    if not documents:
        return "No matching menu items were found."

    results = []

    for doc in documents:
        results.append(doc.page_content)

    return "\n\n".join(results)