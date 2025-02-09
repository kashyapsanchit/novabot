import streamlit as st
import requests

st.title("NovaBot - Your BigCommerce Support Assistant")

with st.sidebar:
    st.header("Add New Content")
    
    # Add Product Manual
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
    
    # Add Customer Ticket
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

# Main chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("How can I help you today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get bot response
    response = requests.post(
        "http://localhost:8000/chat",
        json={"message": prompt}
    )
    bot_message = response.json()["response"]
    
    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": bot_message})
    with st.chat_message("assistant"):
        st.markdown(bot_message)