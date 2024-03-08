import caller, base64
import streamlit as st
from replit import db
if db is None:
    db = {}

def do_API_call(source, key_file, pswd):
    try:
        return caller.API_call(source, key_file, pswd)
    except Exception as e:
        return (str(e), source)

def decode_source(source):
    toreturn = [None] * len(source)
    for ibytes in (0, 1):
        if isinstance(source[ibytes], str):
            toreturn[ibytes] = base64.b64decode(source[ibytes].encode("utf-8"))
            if ibytes == 0:
                toreturn[ibytes] = toreturn[ibytes].decode("utf-8")
            #assert 0, (toreturn[ibytes], ibytes, source)
    return toreturn
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
        #source = xmlta
        source = base64.b64encode(xmlta.encode("utf-8")).decode('utf-8')
    else:
        if xmlfp is None:
            st.error("No XML file or text provided")
            source = None
        else:
            source = base64.b64encode(xmlfp.read()).decode('utf-8')
            #source = xmlfp.read().decode('utf-8')
    if key_file is None:
        key = ""
    else:
        key = base64.b64encode(key_file.read()).decode('utf-8')
        #key = key_file.read().decode('utf-8')
    if source is not None:
        to_save = [source, key, pswd]
        #call = do_API_call(source, key_file, pswd)
        #to_save = (source, key, pswd, call)
        #st.write("Saving data", to_save)
        #print("Saving data", to_save)
        db_index = f"call-{len(db)+1}"
        db[db_index] = to_save
        #st.write("Number of requests in the database:", len(db))
        new_source = db[db_index]
        new_source_decoded = decode_source(new_source)
        #st.write("Retrieving datasrc", new_source)
        #st.write("Retrieving data", new_source_decoded)
        print("new_source_decoded:", new_source_decoded)
        st.write("Request saved to the database")
st.write()
