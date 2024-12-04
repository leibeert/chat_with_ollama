import ollama as client
import streamlit as st
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

def stream_data(stream):
    for chunk in stream:
        yield chunk['message']['content'] + ""

def init_authentication():
    # Load configuration file
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Create an authentication object
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    return authenticator

def main():
    st.set_page_config(page_title="Ollama Chat", page_icon="🤖")
    
    # Initialize authentication
    authenticator = init_authentication()

    # Create login widget
    authenticator.login()

    if st.session_state['authentication_status'] is False:
        st.error('Username/password is incorrect')
        return
    elif st.session_state['authentication_status'] is None:
        st.warning('Please enter your username and password')
        return

    # If authentication successful, show the main app
    if st.session_state['authentication_status']:
        # Add logout button
        authenticator.logout("Logout", "sidebar")
        
        st.title(f"Welcome {st.session_state['name']} to Ollama Chat! 🤖")

        if "llm_model" not in st.session_state:
            st.session_state["llm_model"] = "tinyllama"

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Add model selector in sidebar
        with st.sidebar:
            st.title("Settings")
            st.session_state["llm_model"] = st.selectbox(
                "Select Model",
                ["tinyllama", "llama2", "mistral"],
                index=0
            )

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("What would you like to know?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                stream = client.chat(
                    model=st.session_state["llm_model"],
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                )

                response = st.write_stream(stream_data(stream))
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()