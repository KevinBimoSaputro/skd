from database import supabase
from grafik import tampil_grafik

def menu_admin():

    while True:
        print("\n=== MENU ADMIN ===")
        print("1. Lihat Semua User")
        print("2. Tambah User")
        print("3. Grafik")
        print("4. Logout")

        pilih = input("Pilih: ")

        if pilih == "1":
            data = supabase.table("users").select("*").execute()
            for d in data.data:
                print(d)

        elif pilih == "2":
            nama = input("Nama: ")
            password = input("Password: ")

            supabase.table("users").insert({
                "nama": nama,
                "password": password,
                "role": "user"
            }).execute()

        elif pilih == "3":
            tampil_grafik()

        elif pilih == "4":
            break
