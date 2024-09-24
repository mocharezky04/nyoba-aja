umur = int(input("Masukkan umur = "))

if umur >= 31:
    print("Orang tua")
elif umur >= 17:
    print("Pemuda")
elif umur >= 13:
    print("remaja")
elif umur >= 5:
    print("anak-anak")
else:
    print("bayi")