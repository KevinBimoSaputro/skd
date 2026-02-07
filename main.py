import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import bcrypt

from auth import login, logout
from database import supabase

st.set_page_config(
    page_title="SKD App",
    layout="wide"
)

# ======================
# DESIGN SYSTEM (CSS)
# ======================
def inject_global_css():
    st.markdown(
        """
        <style>
        /* 1. Reset Global & Sidebar Header */
        [data-testid="stSidebarHeader"] {
            display: none !important;
        }
        
        /* 2. Paksa Latar Belakang Putih Total */
        .stApp {
            background-color: #FFFFFF !important;
        }

        /* 3. Sidebar Cerah & Modern */
        [data-testid="stSidebar"] {
            background-color: #F8FAFB !important;
            border-right: 1px solid #EAEFEF !important;
        }
        
        [data-testid="stSidebarNav"] {
            padding-top: 0px !important;
        }

        /* 4. Typography: Abu Gelap untuk kenyamanan mata */
        h1, h2, h3, p, span, label {
            color: #34495E !important; 
        }

        /* 5. Pop-up Tengah Layar (Cerah & Kontras) */
        @keyframes popIn {
            0% { opacity: 0; transform: translate(-50%, -60%) scale(0.9); }
            15% { opacity: 1; transform: translate(-50%, -50%) scale(1.05); }
            20% { transform: translate(-50%, -50%) scale(1); }
            85% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
            100% { opacity: 0; transform: translate(-50%, -40%) scale(0.9); }
        }

        .custom-toast-container {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 1000001;
            pointer-events: none;
        }

        .custom-toast {
            background: #FFFFFF !important;
            color: #25343F !important;
            padding: 30px 50px !important;
            border-radius: 25px !important;
            text-align: center;
            box-shadow: 0 20px 60px rgba(37, 52, 63, 0.2) !important;
            border: 3px solid #FF9B51 !important;
            animation: popIn 4s ease-in-out forwards;
            min-width: 350px;
        }

        .toast-text {
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            display: block;
            color: #25343F !important;
        }

        /* 6. Tombol Orange Custom */
        div.stButton > button {
            background-color: #FF9B51 !important;
            color: white !important;
            border-radius: 10px !important;
            border: none !important;
            padding: 0.5rem 2rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease;
        }
        
        div.stButton > button:hover {
            background-color: #e68a46 !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(255, 155, 81, 0.3) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
def show_toast(message: str):
    st.markdown(
        f"""
        <div class="custom-toast-container">
            <div class="custom-toast">
                <div style="font-size: 40px; margin-bottom: 10px;">✨</div>
                <span class="toast-text">{message}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Panggil CSS di awal
inject_global_css()

# ======================
# DATA FETCHING FUNCTIONS
# ======================
def fetch_all_users():
    response = supabase.table("users").select("*").execute()
    return getattr(response, "data", []) or []

def fetch_all_scores():
    try:
        response = supabase.table("scores").select("*").execute()
        return getattr(response, "data", []) or []
    except Exception:
        return []

def fetch_user_scores(user_id: str):
    try:
        response = (
            supabase.table("scores")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return getattr(response, "data", []) or []
    except Exception:
        return []

def fetch_latest_score(user_id: str):
    scores = fetch_user_scores(user_id)
    return scores[0] if scores else None

# Cek toast msg dari session state
if "toast_msg" in st.session_state:
    show_toast(st.session_state.toast_msg)
    del st.session_state.toast_msg

# ======================
# UI PAGES
# ======================
def admin_user_management():
    st.header("👤 User Management (Admin)")
    users = fetch_all_users()
    with st.container(border=True):
        if users:
            df = pd.DataFrame(users)
            cols = [c for c in ["nama", "role"] if c in df.columns]
            st.subheader("Daftar User")
            st.dataframe(df[cols], use_container_width=True)
        else:
            st.info("Belum ada user di database.")

    st.markdown("---")

    with st.container(border=True):
        st.subheader("Edit User")
        users = fetch_all_users()
        if users:
            nama_list = [u["nama"] for u in users]
            nama_pilih = st.selectbox("Pilih User", nama_list, key="edit_user_select")
            user_pilih = next(u for u in users if u["nama"] == nama_pilih)
            current_role = user_pilih.get("role", "user")

            with st.form("edit_user"):
                new_password = st.text_input("Password baru (kosongkan jika tidak diubah)", type="password")
                new_role = st.selectbox("Role", ["admin", "user"], index=0 if current_role == "admin" else 1)
                submitted_edit = st.form_submit_button("Simpan Perubahan")

            if submitted_edit:
                update_data = {"role": new_role}
                if new_password:
                    password_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                    update_data["password"] = password_hash
                supabase.table("users").update(update_data).eq("id", user_pilih["id"]).execute()
                st.session_state.toast_msg = "User berhasil diupdate"
                st.rerun()

    st.markdown("---")

    with st.container(border=True):
        st.subheader("Hapus User")
        users = fetch_all_users()
        if users:
            nama_list_hapus = [u["nama"] for u in users]
            nama_hapus = st.selectbox("Pilih User untuk dihapus", nama_list_hapus, key="delete_user_select")
            user_hapus = next(u for u in users if u["nama"] == nama_hapus)
            if st.button("Hapus User"):
                supabase.table("users").delete().eq("id", user_hapus["id"]).execute()
                st.session_state.toast_msg = "User berhasil dihapus"
                st.rerun()

def user_self_page(user: dict):
    st.header("📑 Profil & Nilai Saya")
    with st.container(border=True):
        st.write(f"Nama: **{user.get('nama')}**")
        st.write(f"Role: **{user.get('role', 'user')}**")

    st.markdown("---")
    
    with st.container(border=True):
        st.subheader("Input / Update Nilai SKD")
        latest = fetch_latest_score(user["id"])
        current_twk = (latest or {}).get("twk") or 0
        current_tiu = (latest or {}).get("tiu") or 0
        current_tkp = (latest or {}).get("tkp") or 0

        with st.form("update_nilai_saya"):
            twk = st.number_input("TWK", min_value=0, value=int(current_twk))
            tiu = st.number_input("TIU", min_value=0, value=int(current_tiu))
            tkp = st.number_input("TKP", min_value=0, value=int(current_tkp))
            submitted_nilai = st.form_submit_button("Simpan Nilai")

    if submitted_nilai:
        total = twk + tiu + tkp
        supabase.table("scores").insert({
            "user_id": user["id"], "twk": twk, "tiu": tiu, "tkp": tkp, "total": total
        }).execute()
        user.update({"twk": twk, "tiu": tiu, "tkp": tkp, "total": total})
        st.session_state.user = user
        st.session_state.toast_msg = "Nilai berhasil disimpan"
        st.rerun()

    st.markdown("---")
    scores = fetch_user_scores(user["id"])
    if scores:
        df_scores = pd.DataFrame(scores)
        if "created_at" in df_scores.columns:
            df_scores = df_scores.sort_values("created_at")
        df_scores["skd_ke"] = range(1, len(df_scores) + 1)
        
        with st.container(border=True):
            st.subheader("Riwayat Nilai SKD")
            cols = [c for c in ["skd_ke", "created_at", "twk", "tiu", "tkp", "total"] if c in df_scores.columns]
            st.dataframe(df_scores[cols], use_container_width=True)

def grafik_dashboard():
    st.header("📈 Dashboard & Grafik Nilai SKD")
    users = fetch_all_users()
    scores = fetch_all_scores()

    if not users or not scores:
        st.info("Belum ada data yang cukup untuk dashboard.")
        return

    df_users = pd.DataFrame(users)
    df_scores = pd.DataFrame(scores)
    for col in ["twk", "tiu", "tkp"]:
        df_scores[col] = pd.to_numeric(df_scores[col], errors="coerce").fillna(0)
    df_scores["total"] = df_scores["twk"] + df_scores["tiu"] + df_scores["tkp"]

    df = pd.merge(df_scores, df_users[["id", "nama", "role"]], left_on="user_id", right_on="id", how="inner")
    df = df[df["role"] != "admin"]

    if df.empty:
        st.warning("Tidak ada data nilai dari user.")
        return

    df = df.sort_values(["user_id", "created_at"])
    df["skd_ke"] = df.groupby("user_id").cumcount() + 1

    user_list = ["Semua User"] + sorted(df["nama"].unique().tolist())
    pilih_user = st.selectbox("Pilih User", user_list)
    
    max_skd = int(df["skd_ke"].max())
    options = ["Terakhir", "Semua"] + [f"SKD ke-{i}" for i in range(1, max_skd + 1)]
    pilih_skd = st.selectbox("Pilih Percobaan SKD", options, index=1 if pilih_user != "Semua User" else 0)

    if pilih_user != "Semua User":
        df = df[df["nama"] == pilih_user]

    if pilih_skd == "Terakhir":
        filtered = df.sort_values("created_at").groupby("user_id").tail(1)
    elif pilih_skd == "Semua":
        filtered = df.copy()
    else:
        n = int(pilih_skd.split("-")[-1])
        filtered = df[df["skd_ke"] == n]

    with st.container(border=True):
        st.subheader("Visualisasi Nilai")
        fig, ax = plt.subplots(figsize=(10, 4))
        label_col = "nama" if pilih_skd != "Semua" else "skd_ke"
        ax.plot(filtered[label_col].astype(str), filtered["twk"], marker="o", label="TWK", color="#25343F")
        ax.plot(filtered[label_col].astype(str), filtered["tiu"], marker="o", label="TIU", color="#BFC9D1")
        ax.plot(filtered[label_col].astype(str), filtered["tkp"], marker="o", label="TKP", color="#FF9B51")
        ax.legend()
        plt.xticks(rotation=45)
        st.pyplot(fig)

def user_personal_dashboard(user: dict):
    st.header("📊 Dashboard Nilai Saya")
    scores = fetch_user_scores(user["id"])
    if not scores:
        st.info("Silakan input nilai terlebih dahulu di menu User.")
        return
    df = pd.DataFrame(scores).sort_values("created_at")
    df["skd_ke"] = range(1, len(df) + 1)
    
    with st.container(border=True):
        fig, ax = plt.subplots()
        ax.plot(df["skd_ke"], df["total"], marker="o", color="#FF9B51", linewidth=3)
        ax.set_title("Progres Total Nilai")
        st.pyplot(fig)

def admin_maintenance():
    st.header("🛠️ Maintenance / Reset Data")
    st.warning("Aksi ini menghapus semua data scores dan akun 'user' secara permanen.")
    confirm_phrase = "RESET SEMUA DATA"
    input_confirm = st.text_input(f"Ketik '{confirm_phrase}' untuk konfirmasi")
    if st.button("🚀 Jalankan Reset Data", disabled=(input_confirm != confirm_phrase)):
        supabase.table("scores").delete().neq("twk", -1).execute()
        supabase.table("users").delete().eq("role", "user").execute()
        st.session_state.toast_msg = "Reset Berhasil"
        st.balloons()
        st.rerun()

# ======================
# LOGIN & ROUTING
# ======================
if not login():
    st.stop()

user = st.session_state.get("user")
role = user.get("role", "user") if user else "user"

# Header Sidebar Kustom (Ganti Tampilan yang kamu mau hapus)
st.sidebar.markdown(
    """
    <div style='text-align: center; padding-bottom: 20px; border-bottom: 1px solid #EAEFEF; margin-bottom: 20px;'>
        <h1 style='color: #25343F; font-size: 1.5rem; margin-bottom: 0;'>SKD<span style='color: #FF9B51;'>.pro</span></h1>
        <p style='color: #BFC9D1; font-size: 0.8rem;'>Monitoring System</p>
    </div>
    """, 
    unsafe_allow_html=True
)

menu_options = ["Dashboard", "User"]
if role == "admin":
    menu_options.append("Maintenance")

menu = st.sidebar.radio("Navigasi Utama", menu_options)
logout()

# Page Logic
if menu == "Dashboard":
    if role == "admin":
        grafik_dashboard()
    else:
        user_personal_dashboard(user)
elif menu == "User":
    if role == "admin":
        admin_user_management()
    else:
        user_self_page(user)
elif menu == "Maintenance" and role == "admin":
    admin_maintenance()
