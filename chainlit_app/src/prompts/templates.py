from typing import List

def get_query_prompt(user_query: str) -> str:
    return f"User query: {user_query}\nPlease provide a detailed response based on the retrieved documents."

def get_document_prompt(documents: List[str]) -> str:
    return "Here are the relevant documents:\n" + "\n".join(documents) + "\nPlease summarize the key points."

def get_error_prompt(error_message: str) -> str:
    return f"An error occurred: {error_message}\nPlease try again or contact support."

