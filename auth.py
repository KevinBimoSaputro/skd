import streamlit as st
import bcrypt

from database import supabase


def _is_bcrypt_hash(value: str) -> bool:
    """Cek apakah string sudah berupa hash bcrypt."""
    return isinstance(value, str) and value.startswith("$2b$")


def _get_user_by_username(username: str):
    """Ambil data user dari Supabase berdasarkan nama."""
    response = supabase.table("users").select("*").eq("nama", username).execute()
    data = getattr(response, "data", None)
    if data:
        return data[0]
    return None


def login():
    """Halaman login dengan penyimpanan user di session_state."""
    st.title("🔐 Login SKD App")

    # kalau sudah login, tidak perlu login lagi
    if st.session_state.get("user") is not None:
        return True

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not username or not password:
            st.error("Username dan password wajib diisi")
            return False

        user = _get_user_by_username(username)
        if not user:
            st.error("User tidak ditemukan")
            return False

        stored_password = user.get("password")
        ok = False

        if stored_password:
            # jika sudah hash bcrypt
            if _is_bcrypt_hash(stored_password):
                try:
                    ok = bcrypt.checkpw(
                        password.encode("utf-8"), stored_password.encode("utf-8")
                    )
                except ValueError:
                    ok = False
            else:
                # fallback: cocokkan plaintext; jika cocok, migrasi ke bcrypt
                if password == stored_password:
                    ok = True
                    try:
                        new_hash = bcrypt.hashpw(
                            password.encode("utf-8"), bcrypt.gensalt()
                        ).decode("utf-8")
                        supabase.table("users").update(
                            {"password": new_hash}
                        ).eq("id", user["id"]).execute()
                    except Exception:
                        # kalau gagal migrasi, abaikan tapi login tetap jalan
                        pass

        if not ok:
            st.error("Username atau password salah")
            return False

        # login sukses: simpan info user di session
        st.session_state.user = user
        st.session_state.role = user.get("role", "user")
        st.success("Login berhasil")
        st.rerun()

    return False


def logout():
    """Tombol logout di sidebar."""
    if st.sidebar.button("Logout"):
        for key in ("user", "role", "logged_in"):
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
