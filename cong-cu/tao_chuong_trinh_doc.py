"""Tờ "Chương trình tiệc cưới" trình bày dọc, so le, gộp thêm các mốc của lễ vows -> images/thiep/chuong-trinh.jpg

Ghép từ chính các thiệp gốc:
- tiêu đề vàng "Chương trình tiệc cưới", 3 biểu tượng tiệc cưới và câu cảm ơn: cắt từ images/thiep/2.jpg
- 3 biểu tượng lễ vows (máy ảnh, đôi uyên ương đọc lời thề, ly champagne): cắt từ nguon/vows.jpeg (mặt Timeline),
  đổi về cùng màu mực với thiệp
- giờ và tên mốc: viết lại bằng phông Lora (đúng phông của thiệp gốc), cỡ chữ đo theo chữ "17H30" trên 2.jpg
Trục thời gian dọc ở giữa, mỗi mốc một chấm; biểu tượng và chữ đổi bên so le theo từng mốc.

Phông: phong-chu/lora/Lora.ttf (Google Fonts, giấy phép SIL OFL), giữ trên máy như các phông khác.
Chạy:  python cong-cu/tao_chuong_trinh_doc.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

GOC = Path(__file__).resolve().parent.parent
LORA = GOC / "phong-chu" / "lora" / "Lora.ttf"
if not LORA.exists():
    sys.exit(f"Thiếu phông {LORA} (tải Lora[wght].ttf từ github.com/google/fonts, thư mục ofl/lora).")

NEN = (254, 254, 254)            # nền trắng của 2.jpg
MUC = (62, 66, 56)               # màu chữ xanh rêu đậm đo trên 2.jpg
MUC_NET = (68, 72, 62)           # màu nét biểu tượng
K = 3                            # vẽ to gấp 3 rồi thu nhỏ cho nét mượt

goc2 = Image.open(GOC / "images" / "thiep" / "2.jpg").convert("RGB")
vows = Image.open(GOC / "nguon" / "vows.jpeg").convert("RGB")

# ----- Các mảnh cắt từ thiệp gốc (toạ độ đo trên ảnh) -----
TIEU_DE = goc2.crop((200, 95, 781, 200))
CAM_ON = goc2.crop((40, 605, 941, 702))
BT_CUOI = [goc2.crop((196, 241, 302, 352)), goc2.crop((436, 241, 548, 352)), goc2.crop((687, 241, 792, 352))]
NEN_VOWS = np.array([250, 246, 237])
# thu nhỏ biểu tượng vows cho cỡ và nét ngang với biểu tượng tiệc cưới (đôi uyên ương để to hơn một chút)


def bieu_tuong_vows(khung, tl):
    """Cắt biểu tượng trên nền kem, chuyển thành nét màu MUC_NET trên nền trắng."""
    p = np.asarray(vows.crop(khung)).astype(float)
    dam = np.clip((NEN_VOWS.mean() - p.mean(axis=2)) / (NEN_VOWS.mean() - 70), 0, 1)
    ra = np.array(NEN) * (1 - dam[..., None]) + np.array(MUC_NET) * dam[..., None]
    im = Image.fromarray(ra.round().astype(np.uint8))
    return im.resize((round(im.width * tl), round(im.height * tl)), Image.LANCZOS)


BT_VOWS = [bieu_tuong_vows((1553, 406, 1657, 550), .84),     # máy ảnh
           bieu_tuong_vows((1809, 353, 2060, 560), .66),     # đôi uyên ương
           bieu_tuong_vows((2205, 377, 2279, 548), .74)]     # ly champagne

MOC = [  # (giờ, tên mốc, biểu tượng)
    ("15H00", "Đón khách & Chụp hình", BT_VOWS[0]),
    ("15H30", "Lễ Vows", BT_VOWS[1]),
    ("16H00", "Tiệc nhẹ", BT_VOWS[2]),
    ("17H30", "Đón khách & Chụp hình", BT_CUOI[0]),
    ("18H00", "Nghi lễ", BT_CUOI[1]),
    ("18H30", "Khai tiệc", BT_CUOI[2]),
]

# ----- Bố cục -----
RONG = goc2.width                # 981, cùng bề ngang tờ gốc
GIUA = RONG // 2
Y_TIEU_DE = 95
Y_MOC_DAU = 330                  # chấm của mốc đầu tiên
BUOC = 168                       # khoảng cách giữa hai mốc
LECH_CHU = 46                    # chữ cách trục
LECH_HINH = 150                  # tâm biểu tượng cách trục
Y_MOC_CUOI = Y_MOC_DAU + BUOC * (len(MOC) - 1)
Y_CAM_ON = Y_MOC_CUOI + 135
CAO = Y_CAM_ON + CAM_ON.height + 95

CO_CHU = 31                      # chữ "17H30" trên 2.jpg cao 22 điểm ảnh = cỡ 31 của Lora
f = ImageFont.truetype(str(LORA), CO_CHU * K)

anh = Image.new("RGB", (RONG, CAO), NEN)
anh.paste(TIEU_DE, ((RONG - TIEU_DE.width) // 2, Y_TIEU_DE))
anh.paste(CAM_ON, ((RONG - CAM_ON.width) // 2, Y_CAM_ON))

# lớp vẽ nét (trục, chấm, chữ) ở độ phân giải gấp K
lop = Image.new("L", (RONG * K, CAO * K), 0)
v = ImageDraw.Draw(lop)
v.line([(GIUA * K, (Y_MOC_DAU - 40) * K), (GIUA * K, (Y_MOC_CUOI + 40) * K)], fill=200, width=round(1.7 * K))
for i, (gio, ten, hinh) in enumerate(MOC):
    y = Y_MOC_DAU + BUOC * i
    r = 5.5 * K
    v.ellipse([GIUA * K - r, y * K - r, GIUA * K + r, y * K + r], fill=255)
    ben_phai = i % 2 == 0        # mốc lẻ: chữ bên phải, hình bên trái; mốc chẵn ngược lại
    neo = "ls" if ben_phai else "rs"
    x = (GIUA + LECH_CHU) if ben_phai else (GIUA - LECH_CHU)
    v.text((x * K, (y - 4) * K), gio, font=f, fill=255, anchor=neo)
    v.text((x * K, (y + 40) * K), ten, font=f, fill=255, anchor=neo)
    tam = GIUA - LECH_HINH if ben_phai else GIUA + LECH_HINH
    anh.paste(hinh, (round(tam - hinh.width / 2), round(y - hinh.height / 2 + 6)))
lop = lop.resize((RONG, CAO), Image.LANCZOS)
anh = Image.composite(Image.new("RGB", anh.size, MUC), anh, lop)

ra = GOC / "images" / "thiep" / "chuong-trinh.jpg"
anh.save(ra, quality=90, optimize=True)
print("Đã ghi", ra.relative_to(GOC), anh.size)
