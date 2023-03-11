from helper import *

st.set_page_config(page_title='GPT Assistant')
st.title('GPT Assistant')
user = "User" if "user" not in st.experimental_get_query_params() else st.experimental_get_query_params()["user"][0]
initial_content = "" if "initial_content" not in st.session_state else st.session_state["initial_content"]
api_key = "" if "api_key" not in st.session_state else st.session_state["api_key"]

if "rerun" not in st.session_state:
    st.session_state["rerun"] = True
else:
    st.session_state.pop("rerun")
if "data" not in st.session_state:
    st.session_state['data'] = load_data(user, initial_content)
try:
    history, paras = (value for key, value in st.session_state['data'].items())
except:
    history, stats, paras = (value for key, value in st.session_state['data'].items())
save_data(history, paras, user)

if user == "User":
    st.markdown("***\nIt seems like you're new to my chatGPT web client! Please create your own user profile in Settings.\n\n")

show_messages(user, st.session_state['data']["history"])
if "r" in st.session_state:
    report = ""
    area = st.empty()
    for e in st.session_state["r"]:
        if "content" in e["choices"][0]["delta"]:
            report += e["choices"][0]["delta"]["content"]
            area.markdown("***\n**Assistant:**\n\n" + report)
    st.markdown("\n")
    history.append({"role": "assistant", "content": report})
    save_data(history, paras, user)
    st.session_state.pop("r")

with st.form("form", clear_on_submit=True):
    user_input = st.text_area(f"**{user}:**", key="input")
    if st.form_submit_button("Submit", use_container_width=True):
        openai.api_key = api_key if api_key != "" else st.secrets["apikey"]
        history.append({"role": "user", "content": user_input.replace('\n', '\n\n')})
        with st.spinner("Processing..."):
            try:
                r = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=history, stream=True, **paras)
            except openai.error.APIConnectionError:
                return_text = "[Warning] API Connection Error, try again."
            except openai.error.InvalidRequestError:
                return_text = "[Warning] Reached chat content limit, go Settings -> 'Clear Chat History'."
            except openai.error.RateLimitError:
                return_text = "[Warning] Reached chat rate limit, do not send request too frequently."
            else:
                st.session_state["r"] = r
            st.experimental_rerun()

with st.expander("Settings"):
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state['data'] = initial_data(initial_content)
        save_data(st.session_state['data']["history"], st.session_state['data']["paras"], user)
        st.experimental_rerun()
    if user == "Admin":
        user_box = st.selectbox("All Users", [json_file.split(".")[0].split("/")[-1] for json_file in glob.glob(os.getcwd() + '/*.json')])
    else:
        user_box = st.text_input("Username (each user have their own chat data)", value=user)
    initial_content_box = st.text_area("Initial Instruction (applies when the chat history is cleared)", value=initial_content)
    api_key_box = st.text_input("OpenAI API Key (optional)", value=api_key)
    if user_box:
        st.experimental_set_query_params(user=user_box)
        if "rerun" in st.session_state:
            st.experimental_rerun()
    if initial_content_box:
        st.session_state["initial_content"] = initial_content_box.replace('\n', '\n\n')
        if "rerun" in st.session_state:
            st.experimental_rerun()
    if api_key_box:
        st.session_state["api_key"] = api_key_box
        if "rerun" in st.session_state:
            st.experimental_rerun()
    st.write("GUI built by shan-mx")

with st.expander("Parameters"):
    temperature_slider = st.slider("Temperature", 0.0, 2.0, float(paras["temperature"]), 0.1)
    top_p_slider = st.slider("Top P", 0.1, 1.0, float(paras["top_p"]), 0.1)
    presence_penalty_slider = st.slider("Presence Penalty", -2.0, 2.0, float(paras["presence_penalty"]), 0.1)
    frequency_penalty_slider = st.slider("Frequency Penalty", -2.0, 2.0, float(paras["frequency_penalty"]), 0.1)
    if temperature_slider and "rerun" in st.session_state:
        paras["temperature"] = temperature_slider
    if top_p_slider and "rerun" in st.session_state:
        paras["top_p"] = top_p_slider
    if presence_penalty_slider and "rerun" in st.session_state:
        paras["presence_penalty"] = presence_penalty_slider
    if frequency_penalty_slider and "rerun" in st.session_state:
        paras["frequency_penalty"] = frequency_penalty_slider