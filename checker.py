import base64
import os
import socket
import urllib.parse
import urllib.request

# Ваша ссылка на источник
URL = "https://raw.githubusercontent.com/nikita29a/FreeProxyList/refs/heads/main/mirror/1.txt"
OUTPUT_DIR = "vpn-configs-checked"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "1.txt")


def fetch_configs(url):
  try:
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
      content = resp.read().decode("utf-8", errors="ignore").strip()

      try:
        decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
        if "://" in decoded:
          return decoded.splitlines()
      except Exception:
        pass

      return content.splitlines()
  except Exception as e:
    print(f"Ошибка при скачивании списка: {e}")
    return []


def check_proxy(line):
  line = line.strip()
  if not line or "://" not in line:
    return False

  if not line.startswith(
      ("vless://", "trojan://", "vmess://", "ss://", "hysteria2://", "hy2://")
  ):
    return False

  try:
    parsed = urllib.parse.urlparse(line)
    host = parsed.hostname
    port = parsed.port
    if not port:
      port = 443

    if host and port:
      with socket.create_connection((host, int(port)), timeout=2.0):
        return True
  except Exception:
    pass
  return False


def main():
  print("Скачивание серверов по ссылке...")
  lines = fetch_configs(URL)
  print(f"Всего найдено строк в источнике: {len(lines)}")

  working = []
  seen = set()

  for line in lines:
    line = line.strip()
    if not line or line in seen:
      continue
    seen.add(line)

    if check_proxy(line):
      working.append(line)
      print(f"[ЖИВ] {line[:35]}...")

    if len(working) >= 150:
      break

  os.makedirs(OUTPUT_DIR, exist_ok=True)

  with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(working))

  print(
      f"Готово! Рабочие сервера ({len(working)} шт.) сохранены в"
      f" {OUTPUT_FILE}"
  )


if __name__ == "__main__":
  main()
