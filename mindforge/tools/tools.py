from langchain.tools import tool
from langchain_core.tools import Tool 
from schema import CustomerTicket, ProductManual
from utils import insert_data, search_data
import logging
import base64
import tempfile

logging.basicConfig(level=logging.INFO)


@tool
def search_product_manual(query: str) -> str:
    """Search product manuals for relevant information using query input as string."""
    try:
        data = search_data(query)  
        text_results = data.get('text_results', [])
        image_results = data.get('image_results', [])

        if image_results:
            img_data = base64.b64decode(image_results) 
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                temp_file.write(img_data)
                filename = temp_file.name
        else:
            filename = "No image found."

        combined_result = "\n".join(text_results) if text_results else "No relevant text found."
        return f"{combined_result}\nImage File: {filename}"

    except Exception as e:
        logging.info(f"Error searching product manual: {str(e)}")
        return "Error retrieving manual information."


def add_product_manual(manual_data) -> str:
    """Add a new product manual to the system."""
    try:
        manual_dict = eval(manual_data)
        manual_data = ProductManual(**manual_dict)

        insert_data(manual_data.content)

        return f"Successfully added manual for product: {manual_data.title}"
    
    except Exception as e:
        return f"Error adding manual: {str(e)}"
    
    

tools = [
    Tool(
        name="search_product_manual",
        description="Searches product manuals for relevant information. Requires a parameter 'query' as a string input (e.g., {'query': 'icolor 500 printer manual'}).",
        func=search_product_manual
    )
]




# @tool
# def search_customer_tickets(query: str) -> str:
#     """Search previous customer tickets for similar issues."""
#     # Implement vector search in Qdrant
#     search_result = qdrant_client.search(
#         collection_name="customer_tickets",
#         query_vector=[0.1] * 1536, 
#         limit=1
#     )
#     return "Related ticket information: " + str(search_result)

# @tool
# def add_customer_ticket(ticket_data: str) -> str:
#     """Add a new customer ticket to the system."""
#     try:
#         # Convert string input to CustomerTicket object
#         ticket_dict = eval(ticket_data)
#         ticket = CustomerTicket(**ticket_dict)
        
#         # Create embedding for ticket content
#         ticket_text = f"{ticket.title} {ticket.description}"
#         ticket_vector = embeddings.embed_text(ticket_text)
        
#         # Store in Qdrant
#         qdrant_client.upsert(
#             collection_name="customer_tickets",
#             points=[{
#                 "id": hash(ticket.created_at + ticket.customer_id),
#                 "vector": ticket_vector,
#                 "payload": ticket.dict()
#             }]
#         )
#         return f"Successfully added ticket: {ticket.title}"
#     except Exception as e:
#         return f"Error adding ticket: {str(e)}"
