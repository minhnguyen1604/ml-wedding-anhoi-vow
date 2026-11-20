"""Tạo ảnh thiệp ăn hỏi bản nhà trai -> images/thiep/an-hoi.jpg (từ nguon/an-hoi.jpeg)

- viết "Quý khách" (phông chữ ký Photograph Signature, cùng kiểu mặt lời mời 1.jpg) lên dòng chấm, căn phải;
- sửa cho khách nhà trai: TƯ GIA NHÀ TRAI + địa chỉ nhà trai, giờ chính 17H30 (tiệc thân mật ở nhà trai),
  "tại nhà gái" / "tại nhà trai" dưới hàng biểu tượng, dòng "Đoàn nhà trai khởi hành lúc 12H00…".
(Bản có vows: các mốc lễ vows gộp vào tờ chương trình, xem cong-cu/tao_chuong_trinh_doc.py nếu có.)

Phông cần trên máy (không đưa lên GitHub): phong-chu/PhotographSignature.otf, phong-chu/noto-serif-display/;
Times New Roman có sẵn trong Windows.
Chạy:  python cong-cu/tao_thiep_phu.py
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
# Căn phải: mép phải nét chữ thẳng với đầu cuối dòng chấm (cũng là lề phải của khối chữ trên thiệp)
thu = np.asarray(lop_quy_khach(f, an_hoi.width * K, an_hoi.height * K, 0, DAY * K))
mep_phai = np.flatnonzero(thu.max(axis=0) > 40).max()
x = DONG_CHAM[1] * K - mep_phai
lop = lop_quy_khach(f, an_hoi.width * K, an_hoi.height * K, int(x), DAY * K)
lop = lop.resize(an_hoi.size, Image.LANCZOS)

# Căn phải thì chữ Q nằm ngay dưới chữ "TRỌNG": đẩy dòng "TRÂN TRỌNG KÍNH MỜI" lên cho chữ không chạm dấu nặng
# (phía trên còn rộng, cách chữ "Lễ Ăn Hỏi" khoảng 90 điểm ảnh)
day_tran = 979                               # hàng thấp nhất của dòng TRÂN TRỌNG KÍNH MỜI (dấu nặng)
dinh_chu = np.flatnonzero(np.asarray(lop).max(axis=1) > 40).min()
DAY_LEN = max(0, day_tran + 16 - dinh_chu)   # chừa khe 16 điểm ảnh
if DAY_LEN:
    VUNG = (1000, 915, 1650, day_tran + 4)    # vùng dòng TRÂN TRỌNG KÍNH MỜI, nền trắng
    dong = an_hoi.crop(VUNG)
    nen = tuple(int(v) for v in np.median(np.asarray(dong).reshape(-1, 3), axis=0))
    an_hoi.paste(Image.new("RGB", dong.size, nen), VUNG[:2])
    an_hoi.paste(dong, (VUNG[0], VUNG[1] - DAY_LEN))
print("Đẩy dòng TRÂN TRỌNG KÍNH MỜI lên", DAY_LEN, "điểm ảnh")
an_hoi = Image.composite(Image.new("RGB", an_hoi.size, MAU_CHU), an_hoi, lop)

# ----- Bản cho khách nhà trai -----
# Thiệp in sẵn mời tiệc thân mật "tại TƯ GIA NHÀ GÁI". Với khách nhà trai: tập trung ở nhà trai 12H00, cùng đoàn
# sang nhà gái làm lễ ăn hỏi 13H00, đón dâu 15H00 rồi về nhà trai dự tiệc thân mật 17H30. Nên sửa thành:
#   TƯ GIA NHÀ TRAI + địa chỉ nhà trai, giờ chính 17H30 (giờ tiệc), thêm "tại nhà gái" / "tại nhà trai" dưới
#   hàng biểu tượng, và một dòng nghiêng: đoàn nhà trai khởi hành 12H00 từ tư gia nhà trai sang nhà gái.
# Chữ xanh viết lại bằng Times New Roman (đúng phông của thiệp); chữ vàng là phông thương mại không có chữ R,
# nên viết lại cả dòng bằng Noto Serif Display (Google Fonts, OFL) trong phong-chu/noto-serif-display/.
import cv2

TIMES, TIMES_DAM, TIMES_NGHIENG = (f"C:/Windows/Fonts/{t}.ttf" for t in ("times", "timesbd", "timesi"))
NOTO = GOC / "phong-chu" / "noto-serif-display" / "NotoSerifDisplay.ttf"
if not NOTO.exists():
    sys.exit(f"Thiếu phông {NOTO} (tải NotoSerifDisplay[wdth,wght].ttf từ github.com/google/fonts, ofl/notoserifdisplay).")
MAU_XANH = (66, 74, 54)                      # xanh rêu của chữ trên thiệp ăn hỏi
MAU_VANG = (168, 131, 62)                    # vàng của chữ "TƯ GIA NHÀ GÁI"
LE_PHAI = 1627                               # lề phải của khối chữ


def phong(duong, co, dam=None):
    f = ImageFont.truetype(str(duong), round(co * K))
    if dam:
        f.set_variation_by_axes([dam, 100])
    return f


def xoa_chu(anh, khung, nguong, chu_xanh=False):
    """Xoá chữ trong khung rồi vá lại từ nền xung quanh.
    chu_xanh: chỉ lấy điểm có sắc xanh (lục >= đỏ) để không đụng vào nét hoa rum màu be (đỏ > lục) nằm dưới chữ."""
    a = np.asarray(anh).copy()
    x0, y0, x1, y1 = khung
    vung = np.ascontiguousarray(a[y0:y1, x0:x1, ::-1]).astype(np.uint8)
    v = vung.astype(int)
    sang = v.mean(axis=2)
    if chu_xanh:
        mat_na = (sang < 150) | ((v[:, :, 1] >= v[:, :, 2]) & (sang < 246))
        mat_na = cv2.dilate(mat_na.astype(np.uint8) * 255, np.ones((3, 3), np.uint8))
        a[y0:y1, x0:x1] = cv2.inpaint(vung, mat_na, 3, cv2.INPAINT_TELEA)[:, :, ::-1]
    else:
        mat_na = cv2.dilate((sang < nguong).astype(np.uint8) * 255, np.ones((7, 7), np.uint8))
        a[y0:y1, x0:x1] = cv2.inpaint(vung, mat_na, 6, cv2.INPAINT_TELEA)[:, :, ::-1]
    return Image.fromarray(a)


def khop(chu, duong, khung):
    """Cỡ chữ và hàng chân chữ để dòng chữ gốc viết lại bằng phông này trùng đúng khối chữ trên ảnh (khung = mép nét)."""
    x0, y0, x1, y1 = khung
    l, t, r, b = ImageFont.truetype(str(duong), 200).getbbox(chu, anchor="ls")
    co = 200 * (x1 - x0 + 1) / (r - l)
    l, t, r, b = ImageFont.truetype(str(duong), round(co * K)).getbbox(chu, anchor="ls")
    return co, y1 + 1 - b / K


lop_moi = {MAU_XANH: Image.new("L", (an_hoi.width * K, an_hoi.height * K), 0),
           MAU_VANG: Image.new("L", (an_hoi.width * K, an_hoi.height * K), 0)}


def viet(chu, f, x, day, mau=MAU_XANH, neo="rs"):
    ImageDraw.Draw(lop_moi[mau]).text((x * K, day * K), chu, font=f, fill=255, anchor=neo)


# a) dòng vàng: TƯ GIA NHÀ GÁI -> TƯ GIA NHÀ TRAI (chữ I cao 81 điểm ảnh, chân chữ ở hàng 1516)
an_hoi = xoa_chu(an_hoi, (790, 1400, 1645, 1530), 235)
f_vang = phong(NOTO, 100, dam=250)
cao_I = -f_vang.getbbox("I", anchor="ls")[1] / K
f_vang = phong(NOTO, 100 * 81 / cao_I, dam=250)
viet("TƯ GIA NHÀ TRAI", f_vang, LE_PHAI, 1516.5, MAU_VANG)

# b) địa chỉ: hai dòng, cùng cỡ và cùng hàng chân chữ với địa chỉ nhà gái
co_dc, day_2 = khop("MANDARIN GARDEN, HOÀNG MINH GIÁM, HÀ NỘI", TIMES, (491, 1631, 1627, 1680))
_, day_1 = khop("P2705, TẦNG 27, TOÀ B3, CỔNG 3 CHUNG CƯ", TIMES, (646, 1558, 1627, 1613))
an_hoi = xoa_chu(an_hoi, (430, 1545, 1645, 1695), 205, chu_xanh=True)
viet("P2601, TOÀ NHÀ LICOGI 13,", phong(TIMES, co_dc), LE_PHAI, day_1)
viet("164 KHUẤT DUY TIẾN, THANH XUÂN, HÀ NỘI", phong(TIMES, co_dc), LE_PHAI, day_2)

# c) giờ chính: 13H00 -> 17H30 (giờ tiệc thân mật ở nhà trai)
co_ngay, day_ngay = khop("13H00 | CHỦ NHẬT | 27.12.2026", TIMES_DAM, (587, 1777, 1628, 1856))
an_hoi = xoa_chu(an_hoi, (560, 1765, 1645, 1868), 205)
viet("17H30 | CHỦ NHẬT | 27.12.2026", phong(TIMES_DAM, co_ngay), LE_PHAI + 1, day_ngay)

# d) dời "Rất hân hạnh được đón tiếp!" xuống sát đáy để có chỗ cho hai dòng mới
VUNG_CAM_ON, XUONG = (900, 2385, 1660, 2475), 62
dong = an_hoi.crop(VUNG_CAM_ON)
nen = tuple(int(v) for v in np.median(np.asarray(dong).reshape(-1, 3), axis=0))
an_hoi.paste(Image.new("RGB", dong.size, nen), VUNG_CAM_ON[:2])
an_hoi.paste(dong, (VUNG_CAM_ON[0], VUNG_CAM_ON[1] + XUONG))

# e) "tại nhà gái" dưới LỄ ĂN HỎI 13H00, "tại nhà trai" dưới TIỆC THÂN MẬT 17H30 (tâm cột đo trên ảnh)
co_gio, _ = khop("13H00", TIMES, (624, 2257, 747, 2290))
f_noi = phong(TIMES_NGHIENG, co_gio * .92)
viet("tại nhà gái", f_noi, 685, 2338, neo="ms")
viet("tại nhà trai", f_noi, 1454, 2338, neo="ms")

# f) dòng nghiêng: đoàn nhà trai khởi hành 12H00
viet("Đoàn nhà trai khởi hành lúc 12H00 từ tư gia nhà trai sang nhà gái", phong(TIMES_NGHIENG, 38), LE_PHAI, 2410)

for mau, lop_m in lop_moi.items():
    an_hoi = Image.composite(Image.new("RGB", an_hoi.size, mau), an_hoi, lop_m.resize(an_hoi.size, Image.LANCZOS))

thu_nho(an_hoi).save(ra / "an-hoi.jpg", quality=90, optimize=True)
print("Đã ghi images/thiep/an-hoi.jpg")
