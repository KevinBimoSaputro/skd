import matplotlib.pyplot as plt
from database import supabase

def tampil_grafik():

    data = supabase.table("users").select("*").execute().data

    nama = [d["nama"] for d in data]
    twk = [d["twk"] for d in data]
    tiu = [d["tiu"] for d in data]
    tkp = [d["tkp"] for d in data]
    total = [d["total"] for d in data]

    # Grafik 1
    plt.figure()
    plt.plot(nama, twk, marker='o', label='TWK')
    plt.plot(nama, tiu, marker='o', label='TIU')
    plt.plot(nama, tkp, marker='o', label='TKP')

    plt.title("Nilai SKD")
    plt.legend()
    plt.show()

    # Grafik 2
    plt.figure()
    plt.plot(nama, total, marker='o')
    plt.title("Total SKD")
    plt.show()
