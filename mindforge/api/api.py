from fastapi import UploadFile, File, Form
from schema import ChatInput, ChatResponse, CustomerTicket, ProductManual
from langchain.schema import HumanMessage
from langchain.storage import InMemoryStore
from agents import Graph
from config import get_llm
from tools import add_product_manual, search_product_manual
from fastapi import APIRouter
import uuid

router = APIRouter()
memory_store = InMemoryStore()

@router.post("/chat")
async def chat_endpoint(chat_input: ChatInput):

    try:
        import pdb; pdb.set_trace()

        session_id = chat_input.session_id

        state = {"session_id": session_id, "message": chat_input.message}
        

        agent = Graph().app

        state = agent.invoke(state)
        import pdb; pdb.set_trace()
        message = state.get('response', None)
        image = state.get("image", None)

        response = {"message": message, "image": image}

        return response

    except Exception as e:
        return {"message": str(e)}

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

@router.post("/get-result")
async def get_result():
    res = search_product_manual("What kind of optimizer is used in tranformers training?")

    return {"message": res}