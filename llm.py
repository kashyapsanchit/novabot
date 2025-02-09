import langgraph
from langchain_community.llms import Ollama

llm = Ollama(model="llama3")

output = llm("What is the capital of France?")

print(output)
