from pydantic import BaseModel
import datetime
import uuid

class CustomerTicket(BaseModel):
    customer_id: str = str(uuid.uuid4())
    title: str
    description: str
    priority: str
    status: str = "New"
    created_at: str = datetime.now().isoformat()

class ProductManual(BaseModel):
    product_id: str = str(uuid.uuid4())
    title: str
    content: str
    description: str
    last_updated: str = datetime.now().isoformat()


class ChatInput(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str