from services.llm_service import model
import json
def answer_node(state):

    context = "\n\n".join(
        doc.page_content
        for doc in state["docs"]
    )

    question = state["query_en"]

    history = state["messages"]

    user_memory = state.get("memory", {})

    channel = state.get("channel", "website")


    web_prompt = f"""
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
    Suggested questions should help the user:
    - explore eligibility
    - understand benefits
    - find related schemes
    - or ask "what next steps"

    ---------------------
    Instructions:
    - Retrieved context is the primary source of truth.
    - Use user profile memory only to personalize the answer or determine eligibility.
    - Do not make assumptions about missing user information.
    - Use conversation history only for understanding references like "that scheme" or "my previous question".
    - If the answer is not available in the retrieved context, say:
      "I don’t know based on the available data."
    - Keep the answer clear, accurate, and concise.

    ----------------------
    RULES:
    - suggested_questions MUST be 2 to 3 items
    - questions must be short and related to user query
    - no extra text outside JSON
    - no markdown

    FINAL OUTPUT FORMAT (STRICT JSON ONLY):

    Return ONLY valid JSON in this format:

    {{
      "answer": "final user answer here",
      "suggested_questions": [
        "question 1",
        "question 2",
        "question 3"
      ]
    }}
    Answer:
    """

    wp_prompt = f"""
    You are a helpful AI assistant for government schemes.

    You are answering on WhatsApp. So your response MUST be:

    - extremely concise
    - mobile-friendly
    - structured
    - easy to scan in 3 seconds
    - NO long paragraphs

    You must preserve important information, but compress it intelligently.

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
    CRITICAL INSTRUCTIONS:

    1. Retrieved context is the PRIMARY source of truth.
    2. Do NOT hallucinate missing information.
    3. Keep response short but complete.
    4. Use bullet points / numbering only.
    5. NO long explanations.
    6. NO paragraphs longer than 2 lines.

    ---------------------
    🚨 STRICT WHATSAPP OUTPUT FORMAT (FOLLOW EXACTLY):

    Your answer MUST follow this structure:

    🎯 ANSWER:
    - 1–2 line direct answer only

    📌 KEY POINTS:
    - Bullet points (max 4–6 points)
    - Each point should be short (1 line)

    🧾 DETAILS (ONLY IF NECESSARY):
    - Eligibility / steps / conditions (very brief bullets)

    ⚠️ If information is missing:
    - Say: "I don’t know based on available data."

    ---------------------
    STYLE RULES:

    - Use emojis ONLY for section headers (🎯📌🧾⚠️)
    - Do NOT use emojis in bullet points
    - Do NOT write essays
    - Do NOT repeat information
    - Do NOT add unnecessary context
    - Keep total response under ~10–12 lines
    - Make it scannable in WhatsApp preview

    ---------------------
    ANSWER:
    """
    if channel == "website":
        prompt=web_prompt
    elif channel == "whatsapp":
        prompt = wp_prompt
    else:
        prompt = web_prompt

    response = model.invoke(prompt)
    if channel == "website":
        raw_output = response.content.strip()
        print("RAW-CHAT:",raw_output)
        data = json.loads(raw_output)
        print("JSON-DATA:",data)
        return{
            "answer_en": data["answer"].strip(),
            "suggested_ques": data.get("suggested_questions", [])
        }
    else:
        return{
        "answer_en": response.content.strip()
        }
    # return {
    #     "answer_en": response.content.strip()
    # }
    