import caller
import streamlit as st
from replit import db
if db is None:
    db = {}

def do_API_call(source, key_file, pswd):
    try:
        return caller.API_call(source, key_file, pswd)
    except Exception as e:
        return (str(e), source)

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
        source = xmlfp.read()
    if key_file is None:
        key = None
    else:
        key = key_file.read()
    #assert 0, (pswd,)
    to_save = (source, key, pswd)
    #call = do_API_call(source, key_file, pswd)
    #to_save = (source, key, pswd, call)
    st.write("Saving data", to_save)
    db_index = f"call-{len(db)+1}"
    db[db_index] = to_save
    print("Saving data", to_save)
    st.write("Number of requests in the database:", len(db))
    st.write("Retrieving data", db[db_index])
st.write()
