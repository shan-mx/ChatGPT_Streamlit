import time
from helper import *
import streamlit as st
import openai

openai.api_key = api_key1 + api_key2
st.set_page_config(page_title='GPT Chatter')
st.title('GPT Chatter')

tab1, tab2, tab3 = st.tabs(["Chat", "Settings", "Statistics"])
initial_content = tab2.text_input("Initial Instruction", "")
use_history = True
user = tab2.text_input("Username", value="User")
if tab2.button("Clear Chat History"):
    st.session_state['data'] = load_data(False, user, initial_content)
    save_data(st.session_state['data']["chat_history"], st.session_state['data']["chat_stats"], user)
if user or initial_content or 'data' not in st.session_state:
    st.session_state['data'] = load_data(use_history, user, initial_content)

chat_stats = st.session_state['data']["chat_stats"]
chat_history = st.session_state['data']["chat_history"]
col1, col2, col3 = tab3.columns(3)
col1.metric("Time Used:", chat_stats["Time Used"])
col1.metric("Averaged Time:", chat_stats["Averaged Time"])
col2.metric("Tokens Used:", chat_stats["Tokens Used"])
col2.metric("Total Tokens:", chat_stats["Total Tokens"])
col3.metric("Total Rounds:", chat_stats["Total Rounds"])
if st.session_state['data']:
    history = st.session_state['data']["chat_history"]
    tab1.markdown(show_messages(user, history))
user_input = tab1.text_area(user + ":", key='input')
if tab1.button("Submit"):
    chat_stats["Total Rounds"] += 1
    t1 = time.time()
    chat_history.append({"role": "user", "content": user_input})
    with st.spinner("Processing..."):
        try:
            r = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=chat_history)
        except openai.error.APIConnectionError:
            st.error("API Connection Error, try again.")
            return_text = ""
        except openai.error.InvalidRequestError:
            st.error("Reached chat content limit, go Settings -> Clear Chat History.")
            return_text = ""
        except openai.error.RateLimitError:
            st.error("Reached chat rate limit, do not send request too frequently.")
            return_text = ""
        else:
            return_text = r["choices"][0]["message"]["content"]
            chat_stats["Total Tokens"] += r["usage"]["total_tokens"]
            chat_stats["Tokens Used"] = r["usage"]["total_tokens"]
        chat_history.append({"role": "assistant", "content": return_text})
        chat_stats["Time Used"] = round(time.time() - t1, 3)
        chat_stats["Total Time"] += chat_stats["Time Used"]
        chat_stats["Averaged Time"] = round(chat_stats["Total Time"] / chat_stats["Total Rounds"], 3)
        save_data(chat_history, chat_stats, user)
        st.experimental_rerun()
