import json
import streamlit as st
import openai
import os
import glob
import time


def save_data(history: list, stats: dict, paras: dict, user: str):
    with open(f"{user}.json", 'w', encoding='utf-8') as f:
        json.dump({"history": history, "stats": stats, "paras": paras}, f)


def load_data(user: str, initial_content: str) -> dict:
    try:
        with open(f"{user}.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return initial_data(initial_content)


def show_messages(user: str, messages: list):
    for each in messages:
        st.write(each['content'])
        if each["role"] == "user":
            st.markdown(f"***\n**{user}:**\n\n{each['content']}")
        if each["role"] == "assistant":
            st.markdown(f"***\n**Assistant:**\n\n{each['content']}")
        if each["role"] == "system" and each["content"] != "":
            st.markdown(f"***\n**System:**\n\n{each['content']}")


def initial_data(initial_content: str):
    return {"history": [{"role": "system", "content": initial_content}], "stats": initial_stats, "paras": initial_paras}


initial_stats = {"Total Time": 0, "Total Tokens": 0, "Total Rounds": 0, "Time Used": 0, "Tokens Used": 0, "Averaged Time": 0}
initial_paras = {"temperature": 1, "top_p": 1, "presence_penalty": 0, "frequency_penalty": 0}