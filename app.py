import os
import tempfile
import streamlit as st

from main import generate_deck

st.title("DeckGen: pitch deck generator")
text = st.text_area("Describe your startup", height=200)

if st.button("Generate deck") and text.strip():
    try:
        with st.spinner("Generating..."):
            with tempfile.TemporaryDirectory() as tmp:
                out_path = os.path.join(tmp, "deck.pptx")
                generate_deck(text, out_path)
                with open(out_path, "rb") as f:
                    st.session_state["deck_bytes"] = f.read()
        st.success("Done!")
    except Exception as e:
        st.session_state.pop("deck_bytes", None)
        st.error(f"Could not generate the deck: {e}")

if "deck_bytes" in st.session_state:
    st.download_button(
        "Download PPTX",
        st.session_state["deck_bytes"],
        file_name="deck.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )