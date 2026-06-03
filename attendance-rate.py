import streamlit as st
from supabase import create_client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

st.title("Supabase接続確認")

try:

    result = (
        supabase
        .table("attendance")
        .select("*")
        .limit(5)
        .execute()
    )

    st.success("接続成功")

    st.write(result.data)

except Exception as e:

    st.error(str(e))
