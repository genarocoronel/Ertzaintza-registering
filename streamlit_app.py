from requests import get
import streamlit as st
import datetime
import caller, xmlsec


fip = st.file_uploader("key", type=None, accept_multiple_files=False, key=None, help=None, on_change=None, args=None, kwargs=None,
                 disabled=False, label_visibility="visible")
xmlfp = st.file_uploader("XML file:", type=None, accept_multiple_files=False, key=None, help=None, on_change=None, args=None, kwargs=None,
                 disabled=False, label_visibility="visible")
xmlta = st.text_area("XML text:", value="", height=None, max_chars=None, key=None, help=None, on_change=None, args=None, kwargs=None,
                     placeholder=None, disabled=False, label_visibility="visible")
st.write("If XML text is provided, it will be used instead of the file")
st.title('People registry')

button1 = st.button('PV call')
button2 = st.button('RH call')

if button1:
    if xmlta:
        call = caller.test_PV(xml_file=xmlta)
    else:
        call = caller.test_PV(xml_file=xmlfp)
    st.write(call[0])

if button2:
    if xmlta:
        call = caller.test_RH(xml_file=xmlta)
    else:
        call = caller.test_RH(xml_file=xmlfp)
    st.write(call[0])
st.write(f"Writing this page at {datetime.datetime.now()}, being xmlsec.Key {getattr('xmlsec', 'Key', None)} -v {str(xmlsec)}")
