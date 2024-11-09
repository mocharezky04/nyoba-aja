import os
import sys
import re
import json
import pwinput
from prettytable import PrettyTable

os.system("cls")
# Disini akan menggunakan rangkaian mulai dari Otak(dictionary), Badan(input), dan Kaki(mulainya atau berjalannya suatu program)

# Otak(Dictionary)
# Fungsi load data dari json
def load_data():
    try:
        with open(r"C:\Users\Acer\Documents\Kerjaan\kuliah\dp\percobaan 2\PArestoran.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"users": [], "invoices": [], "reservasi": []}

# Fungsi untuk menyimpan data ke json
def simpan_data(data):
    with open(r"C:\Users\Acer\Documents\Kerjaan\kuliah\dp\percobaan 2\PArestoran.json", "w") as file:
        json.dump(data, file, indent=4)

# Fungsi untuk menampilkan meja reservasi
def tampilkan_meja_reservasi():
    data = load_data()
    table = PrettyTable()
    table.field_names = ["Nomor Meja", "Deskripsi", "Harga", "Status", "Pemesan"]
    
    for reservasi in data["reservasi"]:
        nomor_meja = reservasi.get("meja", "N/A")
        deskripsi = reservasi.get("deskripsi", "N/A")
        harga = reservasi.get("harga", 0)
        status = reservasi.get("status", "Ada")
        pemesan = reservasi.get("pemesan", "-")
        format_harga = f"Rp {harga}"
        table.add_row([nomor_meja, deskripsi, format_harga, status, pemesan])
    
    print("\nDaftar Meja dan Status:")
    print(table)

# Fungsi reservasi meja
def reservasi_meja(user):
    data = load_data()
    tampilkan_meja_reservasi()
    nomor_meja = input("Masukkan nomor meja yang ingin dipesan(isi kosong jika mau keluar): ")
    for reservasi in data["reservasi"]:
        if reservasi["meja"] == nomor_meja:
            if reservasi["status"] == "Sudah diambil":
                print("Meja sudah dipesan. Silahkan pilih meja lain.")
                return
            elif user["saldo"] < reservasi["harga"]:
                print("Saldo tidak cukup untuk reservasi meja ini.")
                return
            else:
                reservasi["status"] = "Sudah diambil"
                reservasi["pemesan"] = user["nama"]
                user["saldo"] -= reservasi["harga"]
                print(f"Reservasi meja {nomor_meja} berhasil! Saldo Anda sekarang: Rp {user['saldo']}")
                for u in data["users"]:
                    if u["username"] == user["username"]:
                        u["saldo"] = user["saldo"]
                simpan_data(data)
                return
    print("Nomor meja tidak valid.")

# Fungsi top up saldo
def top_up_saldo(user):
    while True:
        try:
            jumlah_input = input(f"Uang IDR tersisa: Rp {user['uang_idr']}, Masukkan jumlah saldo yang mau ditambahkan: Rp ")
            if jumlah_input.strip() == "":
                print("Input tidak boleh kosong. Silakan masukkan jumlah saldo yang ingin ditambahkan.")
                continue
            jumlah = float(jumlah_input)
            if jumlah <= 0:
                print("Jumlah harus lebih dari 0.")
                continue
            if user["uang_idr"] < jumlah:
                print("Uang IDR tidak cukup untuk melakukan top-up ini.")
                return
            break
        except ValueError:
            print("Input tidak valid. Masukkan angka.")
    
    user["saldo"] += jumlah
    user["uang_idr"] -= jumlah
    
    data = load_data()
    for u in data["users"]:
        if u["username"] == user["username"]:
            u["saldo"] = user["saldo"]
            u["uang_idr"] = user["uang_idr"]
    
    simpan_data(data)
    print(f"Top-up berhasil! Saldo Anda sekarang: Rp {user['saldo']}, Uang IDR tersisa: Rp {user['uang_idr']}")

# Fungsi invoice
def buat_invoice(user):
    data = load_data()
    # Cari meja yang sudah dipesan oleh user
    meja_dipesan = [reservasi for reservasi in data["reservasi"] if reservasi.get("pemesan") == user["nama"]]
    if not meja_dipesan:
        print("Anda belum memiliki reservasi meja.")
        return
    
    total_harga = sum(meja["harga"] for meja in meja_dipesan)
    daftar_meja = [meja["meja"] for meja in meja_dipesan]
    
    invoice = {
        "nama": user["nama"],
        "total_harga": total_harga,
        "meja_dipesan": daftar_meja
    }
    
    data["invoices"].append(invoice)
    simpan_data(data)
    
    print("\n--- Invoice ---")
    print(f"Nama: {invoice['nama']}")
    print(f"Meja Dipesan: {', '.join(invoice['meja_dipesan'])}")
    print(f"Total Harga: Rp {invoice['total_harga']}")
    print("----------------")

# Fungsi buat register
def register_user():
    data = load_data()
    while True:
        nama_panjang = input("Masukkan Nama Panjang: ").strip()
        if nama_panjang and all(char.isalpha() or char.isspace() for char in nama_panjang):
            break
        print("Nama Panjang hanya boleh mengandung huruf dan tidak boleh kosong.")
    
    while True:
        username = input("Masukkan Username: ").strip()
        if not username:
            print("Username tidak boleh kosong.")
        elif any(user["username"] == username for user in data["users"]):
            print("Username sudah terdaftar kak, Silahkan Login ya!")
        else:
            break
    while True:
        password = pwinput.pwinput("Masukkan Password: ").strip()
        if password:
            break
        print("Password tidak boleh kosong.")
    while True:
        try:
            uang_idr_input = input("Masukkan jumlah uang IDR Anda (opsional, tekan Enter untuk Rp 0): Rp ")
            if uang_idr_input.strip() == "":
                uang_idr = 0  
            else:
                uang_idr = float(uang_idr_input)
            if uang_idr < 0:
                print("Jumlah uang IDR tidak bisa negatif.")
                continue
            break
        except ValueError:
            print("Input tidak valid. Masukkan angka.")
    
    user_baru = {
        "nama": nama_panjang,
        "username": username,
        "password": password,
        "saldo": 0,
        "uang_idr": uang_idr
    }
    
    data.setdefault("users", []).append(user_baru)
    simpan_data(data)
    print("Registrasi berhasil!, Selamat Datang!")

# Fungsi login
def login_user():
    data = load_data()
    username = input("Masukkan Username: ")
    password = pwinput.pwinput("Masukkan Password: ")
    for user in data["users"]:
        if user["username"] == username and user["password"] == password:
            print("Login berhasil")
            return user
    print("Username atau password salah.")
    return None

# Badan/Menu(input)
# Fungsi admin
def admin_menu():
    data = load_data()
    while True:
        try:
            print("\n--- Menu Admin ---")
            print("1. Buat User")
            print("2. Lihat Daftar User")
            print("3. Update User")
            print("4. Hapus User")
            print("5. Lihat Meja dan Status")
            print("6. Ubah status Meja Reservasi")
            print("7. Kembali ke Menu Utama")
            
            pilihan_admin = input("Pilih opsi: ")
            if pilihan_admin == "1":
                register_user()
            elif pilihan_admin == "2":
                table = PrettyTable()
                table.field_names = ["Nama Panjang", "Username", "Saldo"]
                for user in data["users"]:
                    table.add_row([user["nama"], user["username"], f"Rp {user['saldo']}"])
                print(table)
            elif pilihan_admin == "3":
                username = input("Masukkan Username yang ingin diupdate: ")
                for user in data["users"]:
                    if user["username"] == username:
                        while True:
                            nama_baru = input("Masukkan Nama Panjang baru: ")
                            if nama_baru and all(char.isalpha() or char.isspace() for char in nama_baru):
                                user["nama"] = nama_baru
                                break
                            print("Nama Panjang hanya boleh mengandung huruf dan tidak boleh kosong.")
                        user["password"] = pwinput.pwinput("Masukkan Password baru: ").strip()
                        simpan_data(data)
                        print("User berhasil diupdate.")
                        break
                else:
                    print("User tidak ditemukan.")
            elif pilihan_admin == "4":
                table = PrettyTable()
                table.field_names = ["Nama Panjang", "Username", "Saldo"]
                for user in data["users"]:
                    table.add_row([user["nama"], user["username"], f"Rp {user['saldo']}"])
                print(table)
                username = input("Masukkan Username yang ingin dihapus: ")
                for user in data["users"]:
                    if user["username"] == username:
                        data["users"].remove(user)
                        simpan_data(data)
                        print("User berhasil dihapus.")
                        break
                else:
                    print("User tidak ditemukan.")
            elif pilihan_admin == "5":
                tampilkan_meja_reservasi()
            elif pilihan_admin == "6":
                tampilkan_meja_reservasi()
                ubah_status_meja = input("Masukkan nomor meja reservasi yang ingin diubah (1-10, selain itu untuk keluar): ")
                for reservasi in data["reservasi"]:
                    if reservasi["meja"] == ubah_status_meja:
                        while True:
                            deskripsi_baru = input("Masukkan deskripsi baru (Kosongkan jika tidak ingin mengubah): ")
                            if deskripsi_baru == "" or (deskripsi_baru and not re.search(r'[\t\n\r\x0b\x0c]', deskripsi_baru)):
                                if deskripsi_baru:  
                                    reservasi["deskripsi"] = deskripsi_baru
                                break 
                            print("Deskripsi tidak boleh mengandung karakter khusus.")
                        
                        while True:
                            status_baru = input("Masukkan status baru (Ada/Sudah diambil): ")
                            if status_baru in ["Ada", "Sudah diambil"]:
                                reservasi["status"] = status_baru
                                if status_baru == "Ada":
                                    reservasi["pemesan"] = "-"
                                break 
                            else:
                                print("Status tidak valid. Harap input 'Ada' atau 'Sudah diambil'.")

                        simpan_data(data)
                        print(f"Reservasi meja {ubah_status_meja} berhasil diubah.")
                        break  
                else:
                    print("Reservasi tidak ditemukan.")
            elif pilihan_admin == "7":
                break
        except KeyboardInterrupt:
            print("\nTolong jangan menekan ctrl+c ya")
            continue 

# Menu login dan register
def menu_login():
    while True:
        try:
            print("\n=== Menu Utama ===")
            print("1. Register (jika belum punya akun)")
            print("2. Login (jika sudah punya akun)")
            print("3. Keluar")
            pilihan = input("Pilih opsi: ")
            
            if pilihan == "1":
                register_user()
            elif pilihan == "2":
                user = login_user()
                if user:
                    if user["username"] == "admin":
                        admin_menu()  # Menu admin
                    else:
                        try:
                            print(f"Selamat datang, {user['nama']}!")
                            while True:
                                print("\n--- Menu User ---")  # Menu user
                                print("1. Top up Saldo")
                                print("2. Invoice")
                                print("3. Reservasi Meja")
                                print("4. Lihat status meja")
                                print("5. Logout")
                                pilihan_user = input("Pilih opsi: ")
                                
                                if pilihan_user == "1":
                                    top_up_saldo(user)
                                elif pilihan_user == "2":
                                    buat_invoice(user)
                                elif pilihan_user == "3":
                                    reservasi_meja(user)
                                elif pilihan_user == "4":
                                    tampilkan_meja_reservasi()
                                elif pilihan_user == "5":
                                    break
                        except KeyboardInterrupt:
                            print("\nTolong jangan menekan ctrl+c ya!")
                            continue
            elif pilihan == "3":
                print("Terima Kasih")
                break
        except KeyboardInterrupt:
            print("\nTolong jangan menekan ctrl+c ya!")
            continue

# Kaki(Menjalankan program)
# Memanggil menu untuk menjalankan program
menu_login()