try:
    from browserbase import BrowserBase
    print("Import successful")
    print(f"Module located at: {BrowserBase.__module__}")
except ImportError as e:
    print(f"Import failed: {e}")
