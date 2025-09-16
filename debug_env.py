# debug_env.py (run locally)
import os
from dotenv import load_dotenv
load_dotenv()

u = os.getenv("USERNAME")
p = os.getenv("PASSWORD")

print("USERNAME repr:", repr(u))
print("USERNAME length:", len(u) if u is not None else 0)
print("Looks like email? ", ("@" in u) if u else False)
print("PASSWORD length:", len(p) if p is not None else 0)
