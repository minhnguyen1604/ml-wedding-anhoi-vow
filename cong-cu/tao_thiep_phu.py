"""Tạo ảnh thiệp ăn hỏi bản nhà trai -> images/thiep/an-hoi.jpg (từ nguon/an-hoi.jpeg)

- viết "Quý khách" (phông chữ ký Photograph Signature, cùng kiểu mặt lời mời 1.jpg) lên dòng chấm, căn phải;
- cho khách nhà trai: giữ mặt thiệp như bản in, đổi hàng biểu tượng thành timeline 4 mốc (12H00 tập trung tại
  nhà trai · 13H00 lễ ăn hỏi tại nhà gái · 15H00 đón dâu · 17H30 tiệc thân mật tại nhà trai) và thêm một dòng
  địa chỉ nhà trai. (Bản đổi hẳn "TƯ GIA NHÀ TRAI" trên mặt thiệp vẫn còn trong script: DOI_NOI_TIEC.)
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


# Đổi nơi tiệc thành TƯ GIA NHÀ TRAI (địa chỉ, giờ chính 17H30) ngay trên mặt thiệp. Đã chọn giữ mặt thiệp
# như bản in gốc, chỉ thêm timeline và địa chỉ nhà trai bên dưới, nên tắt (để lại nếu cần dùng sau).
DOI_NOI_TIEC = False
if DOI_NOI_TIEC:
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

# d) hàng biểu tượng -> timeline 4 mốc: 12H00 tập trung tại nhà trai · 13H00 lễ ăn hỏi tại nhà gái · 15H00 đón dâu
#    · 17H30 tiệc thân mật. Biểu tượng tráp / xe hoa / bát đĩa cắt từ thiệp; mốc 12H00 vẽ thêm ngôi nhà cùng nét.
#    Biểu tượng nằm trên một đường kẻ ngang có chấm tròn, dưới là giờ, tên mốc và nơi (như tờ chương trình tiệc cưới).
nen_trang = tuple(int(v) for v in np.median(np.asarray(an_hoi.crop((1100, 2300, 1640, 2380))).reshape(-1, 3), axis=0))
BT_GOC = {"trap": (596, 1990, 773, 2147), "xe": (923, 2045, 1158, 2142), "dia": (1364, 2029, 1531, 2158)}
bt = {k: an_hoi.crop(v) for k, v in BT_GOC.items()}
co_nhan, _ = khop("LỄ ĂN HỎI", TIMES_NGHIENG, (571, 2177, 797, 2229))
co_gio, _ = khop("13H00", TIMES, (624, 2257, 747, 2290))
an_hoi.paste(Image.new("RGB", (1645 - 430, 2310 - 1985), nen_trang), (430, 1985))   # vùng này chỉ có chữ trên nền trắng


def ve_nha(rong=150):
    """Ngôi nhà nét mảnh màu xanh rêu, cùng độ dày nét với các biểu tượng trên thiệp."""
    k, s = 4, rong / 150
    w, h = round(rong * k) + 8, round(132 * s * k) + 8
    l = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(l)
    nk = round(2.4 * k)
    def P(*ds):
        return [((x * s + 75 * s) * k + 4, (y * s + 66 * s) * k + 4) for x, y in ds]
    d.line(P((-70, -2), (0, -62), (70, -2)), fill=255, width=nk, joint="curve")            # mái
    d.line(P((34, -33), (34, -54), (48, -54), (48, -21)), fill=255, width=nk, joint="curve")  # ống khói
    d.line(P((-54, -14), (-54, 64), (54, 64), (54, -14)), fill=255, width=nk, joint="curve")  # tường
    d.line(P((-16, 64), (-16, 30)), fill=255, width=nk)                                       # cửa vòm
    d.line(P((16, 64), (16, 30)), fill=255, width=nk)
    x0, y0 = P((-16, 14))[0]; x1, y1 = P((16, 46))[0]
    d.arc([x0, y0, x1, y1], 180, 360, fill=255, width=nk)
    for cx in (-36, 36):                                                                      # hai ô cửa sổ
        d.rectangle(P((cx - 9, 10), (cx + 9, 28)), outline=255, width=nk)
    tim = [(0, -22), (-9, -31), (-9, -38), (-4, -42), (0, -38), (4, -42), (9, -38), (9, -31), (0, -22)]
    d.line(P(*tim), fill=255, width=round(2 * k), joint="curve")                              # trái tim trên đầu hồi
    l = l.resize((w // k, h // k), Image.LANCZOS)
    return l


TAM = [596, 882, 1168, 1454]                 # tâm 4 cột, cột cuối giữ đúng chỗ cũ (lề phải chữ TIỆC THÂN MẬT)
DAY_BT, Y_KE = 2145, 2178                    # chân các biểu tượng, hàng đường kẻ
MOC = [("12H00", "TẬP TRUNG", "tại nhà trai", None), ("13H00", "LỄ ĂN HỎI", "tại nhà gái", "trap"),
       ("15H00", "ĐÓN DÂU", "", "xe"), ("17H30", "TIỆC THÂN MẬT", "tại nhà trai", "dia")]
nha = ve_nha()
for x, (gio, ten, noi, k_bt) in zip(TAM, MOC):
    if k_bt:
        im = bt[k_bt]
        an_hoi.paste(im, (round(x - im.width / 2), DAY_BT - im.height + 4))
    else:
        an_hoi.paste(Image.new("RGB", nha.size, MAU_XANH), (round(x - nha.width / 2), DAY_BT - nha.height + 4), nha)
    viet(gio, phong(TIMES, co_gio), x, Y_KE + 58, neo="ms")
    viet(ten, phong(TIMES_NGHIENG, co_nhan * .86), x, Y_KE + 108, neo="ms")
    if noi:
        viet(noi, phong(TIMES_NGHIENG, co_gio * .92), x, Y_KE + 150, neo="ms")
ve = ImageDraw.Draw(lop_moi[MAU_XANH])
ve.line([((TAM[0] - 140) * K, Y_KE * K), (LE_PHAI * K, Y_KE * K)], fill=170, width=round(1.6 * K))
for x in TAM:
    ve.ellipse([(x - 6) * K, (Y_KE - 6) * K, (x + 6) * K, (Y_KE + 6) * K], fill=255)

# e) địa chỉ nhà trai: một dòng nghiêng dưới timeline; dời "Rất hân hạnh được đón tiếp!" xuống cho có chỗ
VUNG_CAM_ON, XUONG = (900, 2385, 1660, 2475), 62
dong = an_hoi.crop(VUNG_CAM_ON)
an_hoi.paste(Image.new("RGB", dong.size, nen_trang), VUNG_CAM_ON[:2])
an_hoi.paste(dong, (VUNG_CAM_ON[0], VUNG_CAM_ON[1] + XUONG))
f_dc = phong(TIMES_NGHIENG, co_gio * .92)
viet("Tư gia nhà trai: P2601, Toà nhà Licogi 13,", f_dc, LE_PHAI, 2384)
viet("164 Khuất Duy Tiến, Thanh Xuân, Hà Nội", f_dc, LE_PHAI, 2424)

for mau, lop_m in lop_moi.items():
    an_hoi = Image.composite(Image.new("RGB", an_hoi.size, mau), an_hoi, lop_m.resize(an_hoi.size, Image.LANCZOS))

thu_nho(an_hoi).save(ra / "an-hoi.jpg", quality=90, optimize=True)
print("Đã ghi images/thiep/an-hoi.jpg")
