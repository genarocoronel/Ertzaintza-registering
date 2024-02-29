import streamlit as st
import sys
from lxml import etree
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
- xk: {getattr(xmlsec, 'Key', None)}

"""

st.write(text)
db[str(len(db.keys()))] = text
