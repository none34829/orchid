import browserbase

# Print available attributes/classes/functions
print("Available attributes in browserbase:")
for attr in dir(browserbase):
    if not attr.startswith('__'):
        print(f"- {attr}")

# Try to import common client class names
print("\nTrying to import common client classes:")
try:
    import browserbase.client
    print("browserbase.client module exists")
    for attr in dir(browserbase.client):
        if not attr.startswith('__'):
            print(f"- client.{attr}")
except ImportError as e:
    print(f"Error importing browserbase.client: {e}")

# Check package version
try:
    print(f"\nPackage version: {browserbase.__version__}")
except AttributeError:
    print("\nNo version attribute found")
