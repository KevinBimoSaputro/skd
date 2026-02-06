from auth import login
from admin import menu_admin
from user import menu_user

while True:
    print("\n=== LOGIN ===")
    nama = input("Username: ")
    password = input("Password: ")

    user = login(nama, password)

    if user:
        print("Login berhasil")

        if user["role"] == "admin":
            menu_admin()
        else:
            menu_user(user)
    else:
        print("Login gagal")
