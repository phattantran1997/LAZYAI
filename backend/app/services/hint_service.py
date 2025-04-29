from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Module-level private variables for singleton pattern
_model = None
_chain = None

def _init_model_and_chain():
    """Initialize the model and chain if not already initialized."""
    global _model, _chain
    if _model is None or _chain is None:
        _model = OllamaLLM(model="deepseek-r1")
        template = (
            "The user is asking you some questions. Please do not provide them the correct answer they are looking for. "
            "Instead, you should only provide the guide for the user to finish their projects by showing them the knowledge "
            "that they should use to get the correct answer or the best source to read to get the best answer and which part "
            "in the questions that they should check again so that they can correct their questions if there are mistakes. "
            "Note: Don't provide the correct answer for the user yet just provide the guide. "
            "Here is the question from the user: {question}"
        )
        prompt = ChatPromptTemplate.from_template(template)
        _chain = prompt | _model

def generate_hint(question: str) -> str:
    """Generate a hint for the given question."""
    _init_model_and_chain()
    response = _chain.invoke({"question": question})
    return response 