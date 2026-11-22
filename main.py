"""Copy the pre-rendered entry.png to /output/entry.png (stdlib only)."""
import os, shutil

os.makedirs("/output", exist_ok=True)
shutil.copyfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png"),
                "/output/entry.png")
