# -*- coding: utf-8 -*-
"""Encrypt index.source.html into a password-gated index.html for GitHub Pages."""

from __future__ import annotations

import base64
import getpass
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "index.source.html"
OUTPUT = ROOT / "index.html"
PASSWORD_FILE = ROOT / ".site-password"
ITERATIONS = 260_000


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_html(plaintext: bytes, password: str) -> dict[str, str]:
    salt = AESGCM.generate_key(bit_length=128)[:16]
    key = derive_key(password, salt)
    nonce = AESGCM.generate_key(bit_length=128)[:12]
    aes = AESGCM(key)
    ciphertext = aes.encrypt(nonce, plaintext, None)
    return {
        "v": 1,
        "kdf": "pbkdf2-sha256",
        "iter": ITERATIONS,
        "salt": base64.b64encode(salt).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "data": base64.b64encode(ciphertext).decode("ascii"),
    }


def unlocker_page(payload: dict[str, str]) -> str:
    blob = json.dumps(payload, ensure_ascii=True, separators=(",", ":"))
    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex,nofollow">
  <title>東北旅繪 · 家人專用</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=Shippori+Mincho:wght@700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --ink: #1a2a28;
      --pine: #2d5a4a;
      --gold: #c4a574;
      --paper: #f7faf8;
      --mist: #7a9e94;
      --coral: #c45c4a;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      min-height: 100svh;
      display: grid;
      place-items: center;
      padding: 1.5rem;
      font-family: "Noto Sans TC", sans-serif;
      color: var(--ink);
      background:
        linear-gradient(160deg, #1e3d34 0%, #2a5045 45%, #3a6354 100%);
    }}
    .card {{
      width: min(420px, 100%);
      background: var(--paper);
      padding: 2rem 1.5rem;
      box-shadow: 0 24px 60px rgba(0,0,0,.22);
    }}
    h1 {{
      font-family: "Shippori Mincho", serif;
      font-size: 1.75rem;
      color: var(--pine);
      letter-spacing: .08em;
      margin-bottom: .4rem;
    }}
    p {{
      color: var(--mist);
      font-size: .92rem;
      line-height: 1.6;
      margin-bottom: 1.4rem;
    }}
    label {{
      display: block;
      font-size: .78rem;
      font-weight: 700;
      letter-spacing: .08em;
      color: var(--pine);
      margin-bottom: .45rem;
    }}
    input {{
      width: 100%;
      padding: .85rem 1rem;
      border: 1px solid rgba(45,90,74,.25);
      background: #fff;
      font: inherit;
      font-size: 1rem;
      margin-bottom: .9rem;
    }}
    input:focus {{ outline: 2px solid var(--gold); border-color: transparent; }}
    button {{
      width: 100%;
      padding: .9rem 1rem;
      border: none;
      background: var(--gold);
      color: var(--ink);
      font: inherit;
      font-weight: 700;
      letter-spacing: .06em;
      cursor: pointer;
    }}
    button:hover {{ filter: brightness(1.05); }}
    .err {{
      display: none;
      margin-top: .85rem;
      color: var(--coral);
      font-size: .85rem;
      font-weight: 500;
    }}
    .err.show {{ display: block; }}
    .hint {{
      margin-top: 1rem;
      font-size: .75rem;
      color: var(--mist);
    }}
  </style>
</head>
<body>
  <main class="card">
    <h1>東北旅繪</h1>
    <p>此行程僅供家人瀏覽。請輸入通行密碼後繼續。</p>
    <form id="gate" autocomplete="off">
      <label for="pw">通行密碼</label>
      <input id="pw" name="password" type="password" required autofocus placeholder="請輸入密碼">
      <button type="submit">進入行程</button>
      <p class="err" id="err" role="alert">密碼不正確，請再試一次。</p>
    </form>
    <p class="hint">提示：正確密碼會暫存在這台裝置，之後約 14 天內不必重輸。</p>
  </main>
  <script>
    const PAYLOAD = {blob};
    const SESSION_KEY = "tohoku-family-unlocked-v1";
    const DAYS = 14;

    async function deriveKey(password, saltB64, iterations) {{
      const enc = new TextEncoder();
      const baseKey = await crypto.subtle.importKey(
        "raw", enc.encode(password), "PBKDF2", false, ["deriveKey"]
      );
      const salt = Uint8Array.from(atob(saltB64), c => c.charCodeAt(0));
      return crypto.subtle.deriveKey(
        {{ name: "PBKDF2", salt, iterations, hash: "SHA-256" }},
        baseKey,
        {{ name: "AES-GCM", length: 256 }},
        false,
        ["decrypt"]
      );
    }}

    async function decryptWithPassword(password) {{
      const key = await deriveKey(password, PAYLOAD.salt, PAYLOAD.iter);
      const nonce = Uint8Array.from(atob(PAYLOAD.nonce), c => c.charCodeAt(0));
      const data = Uint8Array.from(atob(PAYLOAD.data), c => c.charCodeAt(0));
      const plain = await crypto.subtle.decrypt({{ name: "AES-GCM", iv: nonce }}, key, data);
      return new TextDecoder().decode(plain);
    }}

    function remember(password) {{
      const until = Date.now() + DAYS * 24 * 60 * 60 * 1000;
      sessionStorage.setItem(SESSION_KEY, JSON.stringify({{ until }}));
      try {{
        localStorage.setItem(SESSION_KEY, JSON.stringify({{
          until,
          // ponytail: store password locally for convenience on trusted family devices only
          p: password
        }}));
      }} catch (e) {{}}
    }}

    function siteBase() {{
      let path = location.pathname;
      if (/\\/index\\.html?$/i.test(path)) path = path.replace(/\\/index\\.html?$/i, "/");
      if (!path.endsWith("/")) path += "/";
      return location.origin + path;
    }}

    function withAbsoluteAssets(html) {{
      const base = siteBase();
      let out = html;
      if (!/<base\\s/i.test(out)) {{
        out = out.replace(/<head([^>]*)>/i, `<head$1><base href="${{base}}">`);
      }}
      // Extra safety after document.write: force images/ CSS urls absolute
      out = out.replace(
        /(src|href)=(["'])(images\\/[^"']+)\\2/g,
        (_, attr, q, path) => `${{attr}}=${{q}}${{base}}${{path}}${{q}}`
      );
      out = out.replace(
        /url\\((["']?)(images\\/[^"')]+)\\1\\)/g,
        (_, q, path) => `url(${{q}}${{base}}${{path}}${{q}})`
      );
      return out;
    }}

    async function tryUnlock(password, save) {{
      const html = withAbsoluteAssets(await decryptWithPassword(password));
      if (save) remember(password);
      document.open();
      document.write(html);
      document.close();
    }}

    (async function boot() {{
      try {{
        const raw = localStorage.getItem(SESSION_KEY);
        if (!raw) return;
        const saved = JSON.parse(raw);
        if (!saved.until || saved.until < Date.now() || !saved.p) {{
          localStorage.removeItem(SESSION_KEY);
          return;
        }}
        await tryUnlock(saved.p, false);
      }} catch (e) {{
        localStorage.removeItem(SESSION_KEY);
      }}
    }})();

    document.getElementById("gate").addEventListener("submit", async (ev) => {{
      ev.preventDefault();
      const err = document.getElementById("err");
      err.classList.remove("show");
      const password = document.getElementById("pw").value;
      try {{
        await tryUnlock(password, true);
      }} catch (e) {{
        err.classList.add("show");
      }}
    }});
  </script>
</body>
</html>
"""


def read_password() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1]
    if PASSWORD_FILE.exists():
        return PASSWORD_FILE.read_text(encoding="utf-8").strip()
    return getpass.getpass("Family site password: ").strip()


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing source file: {SOURCE}")
    password = read_password()
    if len(password) < 6:
        raise SystemExit("Password should be at least 6 characters.")
    plaintext = SOURCE.read_bytes()
    payload = encrypt_html(plaintext, password)
    OUTPUT.write_text(unlocker_page(payload), encoding="utf-8")
    PASSWORD_FILE.write_text(password + "\n", encoding="utf-8")
    print(f"Locked OK -> {OUTPUT.name} ({OUTPUT.stat().st_size} bytes)")
    print("Edit index.source.html next time, then run: python scripts/lock_site.py")


if __name__ == "__main__":
    main()
