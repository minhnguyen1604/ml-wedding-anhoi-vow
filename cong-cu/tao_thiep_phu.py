"""Tạo ảnh các thiệp phụ (thiệp ăn hỏi, thiệp lễ vows) cho thiệp nhà trai và ghi vào images/thiep/.

- nguon/an-hoi.jpeg -> images/thiep/an-hoi.jpg: viết "Quý khách" (phông chữ ký Photograph Signature,
  cùng kiểu với mặt lời mời 1.jpg) lên dòng chấm dưới "TRÂN TRỌNG KÍNH MỜI".
- nguon/vows.jpeg (nếu có) -> images/thiep/vows-1.jpg (Vow ceremony) và images/thiep/vows-2.jpg (Timeline):
  ảnh gốc là hai mặt nằm cạnh nhau, tách ra hai ảnh để trên điện thoại chữ đủ to.

Chạy:  python cong-cu/tao_thiep_phu.py
Ảnh nào tạo ra thì nhớ khai báo trong mục `thiep` của config.js.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

GOC = Path(__file__).resolve().parent.parent
RONG = 1080                                  # bề ngang ảnh xuất ra
PHONG_CHU_KY = GOC / "phong-chu" / "PhotographSignature.otf"
MAU_CHU = (58, 62, 49)                       # xanh rêu đậm, giống chữ "Quý khách" trên 1.jpg

# ----- Thiệp ăn hỏi: toạ độ trên ảnh gốc 1807x2560 -----
DONG_CHAM = (568, 1623, 1109)                # dòng chấm: x đầu, x cuối, hàng
CO_CHU = 150                                 # cỡ chữ "Quý khách" trên ảnh gốc
DAY = DONG_CHAM[2] - 6                       # chân chữ nằm ngay trên dòng chấm


def lop_chu(f, chu, rong, cao, x, day):
    l = Image.new("L", (rong, cao), 0)
    ImageDraw.Draw(l).text((x, day), chu, font=f, fill=255, anchor="ls")
    return np.asarray(l).astype(int)


def lop_quy_khach(f, rong, cao, x, day):
    """Phông chữ ký vẽ chữ "ý" thành dấu mũ: viết "Quy" rồi ghép dấu sắc lấy từ chữ "á" (như cat_thiep.py)."""
    l = lop_chu(f, "Quy khách", rong, cao, x, day)
    s = f.size
    w = h = s * 2
    goc_a = int(h * .75)
    a1, a0 = lop_chu(f, "á", w, h, s // 2, goc_a), lop_chu(f, "a", w, h, s // 2, goc_a)
    sac = np.clip(a1 - a0, 0, 255)
    ys, xs = np.nonzero(sac > 40)
    sac = sac[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    ca = np.nonzero(a0[goc_a - int(s * .45):goc_a].any(axis=0))[0]
    lech = (xs.min() + xs.max()) / 2 - (ca.min() + ca.max()) / 2
    yy = lop_chu(f, "y", rong, cao, x + f.getlength("Qu"), day)
    cy = np.nonzero(yy[day - int(s * .45):day].any(axis=0))[0]
    x0 = int(round((cy.min() + cy.max()) / 2 + lech - sac.shape[1] / 2))
    y0 = day + ys.min() - goc_a
    vung = l[y0:y0 + sac.shape[0], x0:x0 + sac.shape[1]]
    l[y0:y0 + sac.shape[0], x0:x0 + sac.shape[1]] = np.maximum(vung, sac)
    return Image.fromarray(l.astype(np.uint8))


def thu_nho(anh):
    return anh.resize((RONG, round(anh.height * RONG / anh.width)), Image.LANCZOS)


ra = GOC / "images" / "thiep"

# 1. Thiệp ăn hỏi
if not PHONG_CHU_KY.exists():
    sys.exit(f"Thiếu phông {PHONG_CHU_KY} (xem mục 2c trong cong-cu/cat_thiep.py).")
an_hoi = Image.open(GOC / "nguon" / "an-hoi.jpeg").convert("RGB")
K = 3
f = ImageFont.truetype(str(PHONG_CHU_KY), CO_CHU * K)
dai = f.getlength("Quy khách") / K
x = (DONG_CHAM[0] + DONG_CHAM[1]) / 2 - dai / 2                 # đặt giữa dòng chấm
lop = lop_quy_khach(f, an_hoi.width * K, an_hoi.height * K, int(x * K), DAY * K)
lop = lop.resize(an_hoi.size, Image.LANCZOS)
an_hoi = Image.composite(Image.new("RGB", an_hoi.size, MAU_CHU), an_hoi, lop)
thu_nho(an_hoi).save(ra / "an-hoi.jpg", quality=90, optimize=True)
print("Đã ghi images/thiep/an-hoi.jpg")

# 2. Thiệp lễ vows (nếu có): hai mặt cạnh nhau, giữa là khe trắng
duong_vows = GOC / "nguon" / "vows.jpeg"
if duong_vows.exists():
    v = Image.open(duong_vows).convert("RGB")
    a = np.asarray(v).astype(int)
    giua = a.shape[1] // 2
    trang = np.flatnonzero(a[:, giua - 60:giua + 60].min(axis=2).mean(axis=0) >= 251) + giua - 60
    if len(trang) == 0:
        sys.exit("Không thấy khe trắng giữa hai mặt thiệp vows.")
    for ten, khung in (("vows-1.jpg", (0, 0, trang.min(), v.height)),
                       ("vows-2.jpg", (trang.max() + 1, 0, v.width, v.height))):
        thu_nho(v.crop(khung)).save(ra / ten, quality=90, optimize=True)
        print("Đã ghi images/thiep/" + ten, khung)
