import random
import hashlib
import requests
from ecdsa import SECP256k1
from ecdsa.ellipticcurve import Point
# Thông tin Telegram và Public Key
TELEGRAM_BOT_TOKEN = "xxxxxxxxxxxx"
TELEGRAM_CHAT_ID = "xxxxxxxxx"
# Hàm gửi tin nhắn tới Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except:
        return False

# Thông số elliptic curve
curve = SECP256k1
G = curve.generator
n = curve.order

# Chuyển public key dạng hex -> Point trên đường cong
def hex_to_point(curve, hex_str):
    if hex_str[:2] != "02" and hex_str[:2] != "03":
        raise ValueError("Public key phải ở dạng nén (compressed)")

    x = int(hex_str[2:], 16)
    prefix = int(hex_str[:2], 16)
    p = curve.curve.p()
    a = curve.curve.a()
    b = curve.curve.b()
    y_square = (pow(x, 3, p) + a * x + b) % p
    y = pow(y_square, (p + 1) // 4, p)
    if (y % 2 == 1 and prefix == 2) or (y % 2 == 0 and prefix == 3):
        y = p - y
    return Point(curve.curve, x, y)

# Hàm nhảy (bước nhảy từ 1 đến m)
def kangaroo_jump(point, m):
    data = f"{point.x()}{point.y()}".encode()
    h = int(hashlib.sha256(data).hexdigest(), 16)
    return (h % m) + 1

# Thuật toán Pollard's Kangaroo
def pollard_kangaroo(pubkey_point, lower, upper, max_steps, m):
    N = upper - lower
    tame_x = upper
    tame_point = G * tame_x
    wild_x = 0
    wild_point = pubkey_point
    table = {}
    steps = 0

    print(f"[+] Bắt đầu tame tại x = {tame_x}")
    print(f"[+] Bắt đầu wild tại x = {wild_x}")

    while steps < max_steps:
        # Tame kangaroo
        jump = kangaroo_jump(tame_point, m)
        tame_x += jump
        tame_point += G * jump
        table[(tame_point.x(), tame_point.y())] = tame_x

        # Wild kangaroo
        jump = kangaroo_jump(wild_point, m)
        wild_x += jump
        wild_point += G * jump

        steps += 1

        key = (wild_point.x(), wild_point.y())
        if key in table:
            t_x = table[key]
            d = (t_x - wild_x) % n
            if lower <= d <= upper:
                print(f"[✓] Tìm thấy private key sau {steps} bước: d = {d}")
                return d

        if steps % 10000 == 0:
            print(f"[i] Đã chạy {steps} bước...")

    print("[-] Không tìm thấy trong giới hạn bước.")
    return None

# Cấu hình khoảng tìm kiếm
num = 135
part = 1
lower = 20*1103873984953507439627945351144005829577
upper = 21*1103873984953507439627945351144005829577
max_steps = (upper - lower)**0.5
m = 256
# Public key dạng compressed
pubkey_hex = "03a2efa402fd5268400c77c20e574ba86409ededee7c4020e4b9f0edbee53de0d4"
# Chạy thuật toán
print(f"[#{num}_{part}] Chạy thuật toán Pollard's Kangaroo...")
send_telegram_message(f"#{num}_{part}: Chạy thuật toán Pollard's Kangaroo...")
pubkey_point = hex_to_point(curve, pubkey_hex)
d = pollard_kangaroo(pubkey_point, lower, upper, max_steps, m)

if d:
    send_telegram_message(f"#{num}_{part} Private key (hex): {hex(d)}")
    print(f"✅ #{num}_{part} Private key (hex): {hex(d)}")
else:
    send_telegram_message(f"❌{num} Không tìm thấy private key.")
    print(f"❌#{num}_{part} Không tìm thấy private key.")
