from langchain.tools import tool
from langchain_core.tools import Tool
from config import get_qdrant_client
from qdrant_client.http.models import PointStruct
from qdrant_client.models import Distance, VectorParams, CollectionStatus
from schema import CustomerTicket, ProductManual
from utils import Embedding

qdrant_client = get_qdrant_client()
embeddings = Embedding()

@tool
def search_product_manual(query: str) -> str:
    """Search product manuals for relevant information."""
    
    search_result = qdrant_client.search(
        collection_name="product_manuals",
        query_vector=[0.1] * 1536,  
        limit=1
    )
    return "Product manual information: " + str(search_result)

@tool
def search_customer_tickets(query: str) -> str:
    """Search previous customer tickets for similar issues."""
    # Implement vector search in Qdrant
    search_result = qdrant_client.search(
        collection_name="customer_tickets",
        query_vector=[0.1] * 1536, 
        limit=1
    )
    return "Related ticket information: " + str(search_result)

@tool
def add_customer_ticket(ticket_data: str) -> str:
    """Add a new customer ticket to the system."""
    try:
        # Convert string input to CustomerTicket object
        ticket_dict = eval(ticket_data)
        ticket = CustomerTicket(**ticket_dict)
        
        # Create embedding for ticket content
        ticket_text = f"{ticket.title} {ticket.description}"
        ticket_vector = embeddings.embed_text(ticket_text)
        
        # Store in Qdrant
        qdrant_client.upsert(
            collection_name="customer_tickets",
            points=[{
                "id": hash(ticket.created_at + ticket.customer_id),
                "vector": ticket_vector,
                "payload": ticket.dict()
            }]
        )
        return f"Successfully added ticket: {ticket.title}"
    except Exception as e:
        return f"Error adding ticket: {str(e)}"

@tool
def add_product_manual(manual_data) -> str:
    """Add a new product manual to the system."""
    try:
        manual_dict = eval(manual_data)
        manual_data = ProductManual(**manual_dict)
        manual_vector = embeddings.create_manual_embeddings(manual_data.content)

        payload = {
                "title": manual_data.title,
                "description": manual_data.description,
                "last_updated": manual_data.last_updated
            }
        
        points = PointStruct(
            id=manual_data.product_id,
            vector=manual_vector,
            payload=payload
        )

        qdrant_client.upsert(
            collection_name="product_manuals",
            points=[points]
        )
        return f"Successfully added manual for product: {manual_data.title}"
    except Exception as e:
        return f"Error adding manual: {str(e)}"
    
    

tools = [
    Tool(
        name="search_product_manual",
        description="Search product manuals for information",
        func=search_product_manual
    ),
    Tool(
        name="search_customer_tickets",
        description="Search customer tickets for similar issues",
        func=search_customer_tickets
    ),
    Tool(
        name="add_customer_ticket",
        description="Add a new customer ticket",
        func=add_customer_ticket
    ),
    Tool(
        name="add_product_manual",
        description="Add a new product manual",
        func=add_product_manual
    )
]