import sys

if __name__ == "__main__":
    try:
        # Lazy import; clearer error if stdlib ssl is missing on the system.
        import uvicorn  # noqa
    except ModuleNotFoundError as e:
        if "ssl" in str(e).lower():
            print("HATA: Python ortamınızda standart `ssl` modülü yok. Python'u resmi kurulumla (Add to PATH + pip) yeniden kurun veya yeni bir venv oluşturun." 
                  "Windows için: python.org'dan x64 installer, 'Install for all users' ve 'Add to PATH' işaretli olsun." 
                  "Geçici çözüm: `python -m pip install certifi` sonrası tekrcar deneyin (kalıcı çözüm değildir).", file=sys.stderr)
            sys.exit(1)
        raise
    # Uvicorn import'u başarılıysa server'ı başlat
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
