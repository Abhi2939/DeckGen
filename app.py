import streamlit as st
from io import BytesIO

from main import generate_deck  

st.title("DeckGen: pitch deck generator")
text = st.text_area("Describe your startup", height=200)

if st.button("Generate deck") and text.strip():
    with st.spinner("Generating..."):
        prs = generate_deck(text)
        buf = BytesIO()
        prs.save(buf)
        buf.seek(0)
    st.success("Done!")
    st.download_button(
        "Download PPTX",
        buf,
        file_name="deck.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )