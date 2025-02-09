from fastapi import Response, FastAPI, Request, UploadFile, File
from schema import ChatInput, ChatResponse, CustomerTicket, ProductManual
from tools import add_product_manual
from fastapi import APIRouter

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_input: ChatInput):
    # Initialize state with any existing conversation history
    state = state_manager.init_state()
    state["messages"].append(HumanMessage(content=chat_input.message))
    
    # Run workflow
    final_state = workflow.run(state)
    
    # Get last message
    response = final_state["messages"][-1].content
    return ChatResponse(response=response)

@router.post("/upload-manual")
async def upload_manual(
    file: UploadFile = File(...),
    title: str = None,
    description: str = None
):
    content = await file.read()
    manual = ProductManual(
        title=title,
        content=content.decode(),
        description=description
    )
    result = add_product_manual(str(manual.model_dump()))
    return {"message": result}

@router.post("/create-ticket")
async def create_ticket(
    file: UploadFile = File(...),
    title: str = None,
    description: str = None
):
    content = await file.read()
    manual = ProductManual(
        title=title,
        content=content.decode(),
        description=description
    )
    result = add_product_manual(str(manual.model_dump()))
    return {"message": result}