import uuid
import json
from config import get_llm
from tools import tools
from langchain.storage import InMemoryStore
from langgraph.prebuilt import create_react_agent

memory_store = InMemoryStore()

def novabot(state):
    import pdb; pdb.set_trace()
    llm = get_llm()
    session_id = state["session_id"]  
    tool_names = ['search_product_manual']

    user_message = state.get('message', 'How can I help you today?')

    past_messages = memory_store.mget([session_id]) or []
    past_messages = [msg for msg in past_messages if msg is not None]
    context = "\n".join(past_messages[-5:]) if past_messages else ""

    prompt_template = """You are a helpful support chatbot for BigCommerce. 
    You assist customers with product information and support issues.

    Analyse the User message and choose from the tools below:

    You can use the following tools:
    {tool_names}

    You remember past interactions in a session to provide contextual responses.
    Review the tool outputs carefully and provide a relevant, complete answer based on the information retrieved.
    If the tool output doesn't contain sufficient information, say so and suggest an alternative approach.

    Previous messages:
    {context}

    User: {message}

    Your response **must** be valid JSON with exactly the following format:
    {{
        "response": "Your final response here using the text returned."
        "img_path": "The path of the image in the second output of the tool."
    }}
    Strictly return only JSON. Do not include anything outside of the JSON format.
    """

    prompt_inputs = {"tool_names": tool_names, "context": context, "message": user_message}
    formatted_prompt = prompt_template.format(**prompt_inputs)
    
    inputs = {"messages": [{"role": "system", "content": formatted_prompt}, {"role": "user", "content": user_message}]}
    import pdb; pdb.set_trace()

    agent = create_react_agent(model=llm,tools=tools)

    state = agent.invoke(inputs)

    messages = state.get('messages', [])

    data = json.loads(messages[-1].content)

    response = data["response"]
    img_path = data["img_path"]

    state['response'] = response
    state['image'] = img_path

    # Update conversation history
    updated_messages = past_messages + [user_message, response]
    memory_store.mset([(session_id , updated_messages)])

    return state
