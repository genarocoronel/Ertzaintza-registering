import streamlit as st
import xmlsec
try:
  from replit import db
except ModuleNotFoundError:
  db = {}

st.title("Streamlit on Replit")

text = f"""

- More information on streamlit [here](https://docs.streamlit.io/)
- db: {db.keys()}
- xk: {xmlsec.Key}

"""

st.write(text)
db[str(len(db.keys()))] = text