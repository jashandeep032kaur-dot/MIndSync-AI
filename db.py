import streamlit as st
from pymongo import MongoClient

@st.cache_resource
def get_db():
    mongo_uri = st.secrets.get("MONGO_URI") or st.secrets.get("mongo_key")

    if not mongo_uri:
        raise RuntimeError("MongoDB URI not found in Streamlit secrets")

    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000
    )

    # Fail fast if unreachable
    client.admin.command("ping")

    return client["final_chatbot_talks"]
