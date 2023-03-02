import json


def save_data(history, stats, user):
    with open(f"chat_data{user}.json", 'w', encoding='utf-8') as f:
        json.dump({"chat_history": history, "chat_stats": stats}, f)


def load_data(use_history, user, initial_content):
    if use_history:
        try:
            with open(f"chat_data{user}.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            return {"chat_history": [{"role": "system", "content": initial_content}], "chat_stats": initial_stats}
    else:
        return {"chat_history": [{"role": "system", "content": initial_content}], "chat_stats": initial_stats}


def show_messages(user, messages):
    md_str = ""
    for i in range(len(messages)):
        each = messages[i]
        if each["role"] == "user":
            md_str += f"**{user}:**\n\n{each['content']}\n***\n"
        if each["role"] == "assistant":
            md_str += f"**Assistant:**\n\n{each['content']}\n***\n"
    return md_str


api_key1 = "half of your apikey"
api_key2 = "another half of the apikey"
initial_stats = {
    "Total Time": 0,
    "Total Tokens": 0,
    "Total Rounds": 0,
    "Time Used": 0,
    "Tokens Used": 0,
    "Averaged Time": 0
}
