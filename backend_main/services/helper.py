def add_chat_message(state, role, text, lang):
    history = state.get("chat_history", [])

    return history + [
        {
            "role": role,
            "text": text,
            "lang": lang
        }
    ]