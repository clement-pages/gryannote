"""Patch @gradio/preview to handle TypeScript 'import type' statements.

The Vite plugin in @gradio/preview transforms svelte imports like:
  import { X } from "svelte"
into:
  const { X } = window.__gradio__svelte__internal;

But it doesn't handle 'import type { X } from "svelte"' correctly,
producing invalid JS: 'const type { X } = window.__gradio__svelte__internal;'

Fix: strip 'import type' lines entirely (they have no runtime effect).
"""
import glob
import os

patterns = [
    "node_modules/@gradio/preview/dist/index.js",
    "*/node_modules/@gradio/preview/dist/index.js",
]

found = False
for pattern in patterns:
    for filepath in glob.glob(pattern):
        with open(filepath, "r") as f:
            content = f.read()

        old = "transform(code) {"
        new = """transform(code) {
      code = code.replace(/import\\s+type\\s+\\{[^}]*\\}\\s+from\\s+['"][^'"]+['"]\\s*;?/g, '');"""

        if old in content and "import\\\\s+type" not in content:
            content = content.replace(old, new, 1)
            with open(filepath, "w") as f:
                f.write(content)
            print(f"Patched: {filepath}")
            found = True
        else:
            print(f"Already patched or pattern not found: {filepath}")
            found = True

if not found:
    print("No @gradio/preview/dist/index.js found")
