# -*- coding: utf-8 -*-
import json

pkg_path = r"E:\Trabajo\03_Trading\ingenusfx\package.json"

with open(pkg_path, "r", encoding="utf-8") as f:
    pkg = json.load(f)

pkg["scripts"]["scan-secrets"] = "node scripts/scan-bundle-secrets.mjs dist"
pkg["scripts"]["build"] = "vite build --config config/vite.config.js && node scripts/scan-bundle-secrets.mjs dist"

with open(pkg_path, "w", encoding="utf-8") as f:
    json.dump(pkg, f, indent=2)

print("Updated ingenusfx/package.json with automated secret scan")
