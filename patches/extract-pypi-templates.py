"""Extract pre-built frontend templates from the PyPI gryannote wheel.

The source repo doesn't include built frontend templates (they're build
artifacts). Instead of building them in Docker (which has svelte/vite
resolution issues), we extract the pre-built templates from the PyPI
wheel and copy them into the installed site-packages.
"""
import zipfile
import site
import os
import subprocess
import tempfile

tmpdir = tempfile.mkdtemp()
subprocess.check_call(
    ["pip", "download", "gryannote==0.3.0", "--no-deps", "-d", tmpdir],
)

wheel = os.path.join(tmpdir, "gryannote-0.3.0-py3-none-any.whl")
sp = site.getsitepackages()[0]

with zipfile.ZipFile(wheel) as z:
    for name in z.namelist():
        if "/templates/" in name:
            dest = os.path.join(sp, name)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with z.open(name) as src, open(dest, "wb") as dst:
                dst.write(src.read())
            print(f"Copied: {name}")

import shutil
shutil.rmtree(tmpdir)
print("Done.")
