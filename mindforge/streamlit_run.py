import streamlit as st
import requests
import uuid
from PIL import Image

st.set_page_config(
    page_title="NovaBot",  
    page_icon="🤖",
    layout="wide"
)

st.title("NovaBot - Your BigCommerce Support Assistant")

with st.sidebar:
    st.header("Add New Content")
    
    st.subheader("Add Product Manual")
    manual_file = st.file_uploader("Upload Manual", type=["txt", "md", "pdf"])
    manual_title = st.text_input("Manual Title")
    description = st.text_input("Description")
    
    if st.button("Upload Manual") and manual_file and manual_title:
        files = {"file": manual_file}
        data = {
            "title": manual_title,
            "description": description
        }
        response = requests.post("http://localhost:8000/upload-manual", files=files, data=data)
        st.success(response.json()["message"])
    
    st.subheader("Add Customer Ticket")
    ticket_title = st.text_input("Ticket Title")
    ticket_description = st.text_area("Description")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    
    if st.button("Create Ticket") and ticket_title and ticket_description:
        ticket_data = {
            "title": ticket_title,
            "description": ticket_description,
            "priority": priority
        }
        chat_input = f"add ticket {str(ticket_data)}"
        response = requests.post("http://localhost:8000/chat", json={"message": chat_input})
        st.success(response.json()["response"])



if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())  

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("How can I help you today?"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    response = requests.post(
        "http://localhost:8000/chat",
        json={"session_id": st.session_state.session_id, "message": prompt}  
    )
    import pdb; pdb.set_trace()
    
    response = response.json()

    bot_message = response.get('message', None)
    image = response.get("image", None)

    st.session_state.messages.append({"role": "assistant", "content": bot_message})
    
    with st.chat_message("assistant"):
        
        if bot_message and image:
            image = Image.open(image)
            st.markdown(bot_message)
            st.image(image, width=200)
        
        elif bot_message:
            st.markdown(bot_message)
        else:
            st.markdown("I'm sorry, I do not know about that.")
