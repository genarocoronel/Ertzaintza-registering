import streamlit as st
from replit import db

st.title("Streamlit on Replit")

text = f"""

- More information on streamlit [here](https://docs.streamlit.io/)
- db: {db.keys()}

"""

st.write(text)
db[str(len(db.keys()))] = text