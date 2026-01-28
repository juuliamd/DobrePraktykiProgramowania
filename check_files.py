import os

folder = 'photos'
if not os.path.exists(folder):
    print(f"❌ BŁĄD: Python w ogóle nie widzi folderu '{folder}'!")
else:
    pliki = os.listdir(folder)
    print(f"✅ Folder '{folder}' istnieje.")
    print(f"   Znaleziono {len(pliki)} plików.")
    print("   Pierwsze 5 plików w folderze (dokładne nazwy):")
    for p in pliki[:5]:
        print(f"   -> '{p}'")