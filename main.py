import streamlit as st
import sys
print("sp", sys.path)
import replit
try:
  from replit import db
  print("rdb", db)
except ModuleNotFoundError:
  db = {}
  print("rmdb")
import xmlsec

st.title("Streamlit on Replit")

text = f"""

- More information on streamlit [here](https://docs.streamlit.io/)
- db: {db.keys()}
- xk: {xmlsec.Key}

"""

st.write(text)
db[str(len(db.keys()))] = text
