import json
import streamlit as st
import openai
import os
import glob
import time


def save_data(history: list, stats: dict, user: str):
    with open(f"chat_data_{user}.json", 'w', encoding='utf-8') as f:
        json.dump({"chat_history": history, "chat_stats": stats}, f)


def load_data(user: str, initial_content: str) -> dict:
    try:
        with open(f"chat_data_{user}.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {"chat_history": [{"role": "system", "content": initial_content}], "chat_stats": initial_stats}
    except json.decoder.JSONDecodeError:
        return {"chat_history": [{"role": "system", "content": initial_content}], "chat_stats": initial_stats}


def show_messages(user: str, messages: list, st):
    for each in messages:
        if each["role"] == "user":
            st.markdown(f"***\n**{user}:**\n\n{each['content']}")
        if each["role"] == "assistant":
            st.markdown(f"***\n**Assistant:**\n\n{each['content']}")
    st.markdown("\n")


initial_stats = {"Total Time": 0, "Total Tokens": 0, "Total Rounds": 0, "Time Used": 0, "Tokens Used": 0, "Averaged Time": 0}
