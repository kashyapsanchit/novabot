from config import get_llm

class Agent():
    def __init__(self):
        self.llm = get_llm()

    def get_response(self, message):

        return self.llm.invoke(message)