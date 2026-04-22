import streamlit as st

def get_client():
    try:
        from supabase import create_client
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
        if not url or not key:
            return None
        return create_client(url, key)
    except Exception:
        return None


def load_experiments(client) -> list[dict]:
    if client is None:
        return []
    try:
        res = client.table("experiments").select("*").order("created_at", desc=True).execute()
        return res.data or []
    except Exception:
        return []


def save_experiment(client, record: dict) -> tuple[bool, str]:
    if client is None:
        return False, "Supabase not configured."
    try:
        client.table("experiments").insert(record).execute()
        return True, "Saved."
    except Exception as e:
        return False, str(e)


def update_experiment(client, exp_id: str, updates: dict) -> tuple[bool, str]:
    if client is None:
        return False, "Supabase not configured."
    try:
        client.table("experiments").update(updates).eq("id", exp_id).execute()
        return True, "Updated."
    except Exception as e:
        return False, str(e)


def delete_experiment(client, exp_id: str) -> tuple[bool, str]:
    if client is None:
        return False, "Supabase not configured."
    try:
        client.table("experiments").delete().eq("id", exp_id).execute()
        return True, "Deleted."
    except Exception as e:
        return False, str(e)
