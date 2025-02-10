from fastapi import Response, FastAPI, Request, UploadFile, File, Form
from schema import ChatInput, ChatResponse, CustomerTicket, ProductManual
from utils.pdf_processor import extract_text_and_images
from config import get_llm
from tools import add_product_manual
from fastapi import APIRouter

router = APIRouter()


# @router.post("/chat", response_model=ChatResponse)
# async def chat_endpoint(chat_input: ChatInput):
#     # Initialize state with any existing conversation history
#     state = state_manager.init_state()
#     state["messages"].append(HumanMessage(content=chat_input.message))
    
#     # Run workflow
#     final_state = workflow.run(state)
    
#     # Get last message
#     response = final_state["messages"][-1].content
#     return ChatResponse(response=response)

@router.post("/upload-manual")
async def upload_manual(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(None),
):
    content = await file.read()

    manual = ProductManual(
        title=title,
        content = content,
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

@router.post("/health-llm")
async def health_llm():
    llm = get_llm()
    res = llm.invoke(input="What is the capital of the United States?")
    return {"message": res.content}