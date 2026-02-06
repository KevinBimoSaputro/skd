from database import supabase

def menu_user(user):

    while True:
        print("\n=== MENU USER ===")
        print("1. Lihat Nilai")
        print("2. Update Nilai")
        print("3. Logout")

        pilih = input("Pilih: ")

        if pilih == "1":
            print(user)

        elif pilih == "2":
            twk = int(input("TWK: "))
            tiu = int(input("TIU: "))
            tkp = int(input("TKP: "))

            supabase.table("users") \
                .update({
                    "twk": twk,
                    "tiu": tiu,
                    "tkp": tkp
                }) \
                .eq("id", user["id"]) \
                .execute()

            print("Nilai berhasil diupdate")

        elif pilih == "3":
            break
