"""Streamlit window for manual probing. Every message is logged (test_type = manual).

    streamlit run app.py -- --card cards/C07.json
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from chatbot import Chatbot, load_card

ap = argparse.ArgumentParser()
ap.add_argument("--card", default=os.environ.get("WOC_CARD", "cards/C01.json"))
args, _ = ap.parse_known_args()

card = load_card(args.card)
st.set_page_config(page_title="WOC7015 chatbot under test")
st.title("Example University assistant")
with st.sidebar:
    st.subheader("Your configuration (read-only)")
    st.json(card)
    if st.button("New session"):
        st.session_state.pop("bot", None)
        st.session_state.pop("msgs", None)

if "bot" not in st.session_state:
    st.session_state.bot = Chatbot(card, os.path.join("logs", f"{card['candidate_id']}_manual.csv"))
    st.session_state.msgs = []

for m in st.session_state.msgs:
    st.chat_message(m["role"]).write(m["content"])

if prompt := st.chat_input("Ask the assistant"):
    st.chat_message("user").write(prompt)
    reply = st.session_state.bot.ask(prompt, test_type="manual")
    st.chat_message("assistant").write(reply)
    st.session_state.msgs += [{"role": "user", "content": prompt}, {"role": "assistant", "content": reply}]
