from services.llm_service import model


def answer_node(state):

    context = "\n\n".join(
        doc.page_content
        for doc in state["docs"]
    )

    question = state["query_en"]

    history = state["messages"]

    user_memory = state.get("memory", {})


    prompt = f"""
    You are a helpful AI assistant for government schemes.

    Use the available information in the following priority order:

    1. Retrieved Context (highest priority)
    2. User Profile Memory (for personalization)
    3. Conversation History (for continuity)


    ---------------------
    User Profile Memory:
    {user_memory}


    ---------------------
    Conversation History:
    {history}


    ---------------------
    Retrieved Context:
    {context}


    ---------------------
    Current Question:
    {question}


    ---------------------
    Instructions:
    - Retrieved context is the primary source of truth.
    - Use user profile memory only to personalize the answer or determine eligibility.
    - Do not make assumptions about missing user information.
    - Use conversation history only for understanding references like "that scheme" or "my previous question".
    - If the answer is not available in the retrieved context, say:
      "I don’t know based on the available data."
    - Keep the answer clear, accurate, and concise.


    Answer:
    """

    response = model.invoke(prompt)

    return {
        "answer_en": response.content
    }

    # prompt = f"""
    #     You are a helpful AI assistant.
        
        
        
    #     Use the following conversation history and retrieved context to answer the user's question accurately.
        
        
        
    #     ---------------------
    #     Conversation History:
    #     {history}
        
        
        
    #     ---------------------
    #     Retrieved Context:
    #     {context}
        
        
        
    #     ---------------------
    #     Current Question:
    #     {question}
        
        
        
    #     ---------------------
    #     Instructions:
    #     - Use retrieved context as primary source of truth
    #     - Use chat history for continuity
    #     - If answer is not in context, say "I don’t know based on available data"
    #     - Keep answer clear and concise
        
        
        
    #     Answer:
    #     """

