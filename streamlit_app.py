from requests import get
import streamlit as st
import datetime
import caller, xmlsec
from replit import db


#with st.form("Authentication"):
key_file = st.file_uploader("key", type=None, accept_multiple_files=False, key=None, help=None, on_change=None, args=None, kwargs=None,
             disabled=False, label_visibility="visible")
pswd = st.text_input("Password", value="", type="password", help=None, on_change=None, args=None, kwargs=None, placeholder=None,
                 disabled=False, label_visibility="visible")
#with st.form("XML input"):
xmlfp = st.file_uploader("XML file:", type=None, accept_multiple_files=False, key=None, help=None, on_change=None, args=None, kwargs=None,
             disabled=False, label_visibility="visible")
xmlta = st.text_area("XML text:", value="", height=None, max_chars=None, key=None, help=None, on_change=None, args=None, kwargs=None,
                 placeholder=None, disabled=False, label_visibility="visible")
st.write("If XML text is provided, it will be used instead of the file")
st.title('People registry')

button = st.button('Test API call')

if button:
    if xmlta:
        source = xmlta
    else:
        source = xmlfp
    try:
        call = caller.API_call(source, key_file, pswd)
        st.write("Call", call)
        db[f"call-{len(db)+1}"] = call
    except Exception as e:
        db[f"call-{len(db) + 1}"] = (e, source)
st.write()
