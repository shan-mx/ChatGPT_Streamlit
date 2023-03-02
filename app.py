import time
from helper import *
import streamlit as st
import openai

st.set_page_config(page_title='GPT Assistant')
st.title('GPT Assistant')

tab1, tab2, tab3 = st.tabs(["Chat", "Settings", "Statistics"])
api_key = tab2.text_input("OpenAI API Key")
user = tab2.text_input("Username (each user have their own chat history)", value="User")
initial_content = tab2.text_input("Initial Instruction (applies when the chat history is cleared)", "")
openai.api_key = api_key if api_key != "" else st.secrets["apikey"]

if user or 'data' not in st.session_state:
    st.session_state['data'] = load_data(user, initial_content)
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
if tab1.button("Submit", use_container_width=True):
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
if tab1.button("Clear Chat History", use_container_width=True):
    st.session_state['data']["chat_history"] = [{"role": "system", "content": initial_content}]
    st.session_state['data']["chat_stats"] = initial_stats
    save_data(st.session_state['data']["chat_history"], st.session_state['data']["chat_stats"], user)
    st.experimental_rerun()
