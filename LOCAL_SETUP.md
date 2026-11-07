## Keyingi tasdiqlangan nashr

«AI javobi qanday tug‘iladi?» — `media/studio/mirabilis-ai-javobi.mp4`.
2026-11-08 10:00 Asia/Tashkent uchun Metricool’da autoPublish=true,
PENDING holatida saqlandi va alohida kalendar so‘rovi bilan tekshirildi.
Post ID 419874061, UUID 9192951298047626537. Shu sanaga ikkinchi Reel
rejalashtirilmasin. Bu nashr bo‘ldi degani emas.

## To‘liq video brendi — 2026-11-07

Joriy tayyor nusxa: `media/studio/mirabilis-ai-javobi.mp4`.
Tepada MIRABILIS ON, chipda MIRABILIS, pastda @mirabilis_on.
Dastlabki ikki 3D sahna qayta render qilindi; 3–4 sahna asl geometriyadan
qayta foydalanadi. To‘rtta yakuniy kadr tekshirildi, audio original bilan bir xil.
Caption: `media/studio/mirabilis-caption.txt`. Oldingi ikki MP4 tarixiy nusxa;
yangi postga ular yuklanmasin. Nashr holati `media/publication-index.json`da.

## Instagram username — 2026-11-07

Joriy Instagram username: **@mirabilis_on**. Foydalanuvchi o‘zgartirganini
bildirdi; bu o‘sha akkaunt, Metricool brand ID `7904135`. Metricool eski
`giraffe.96069430` nomini keshda qaytarmoqda. Ko‘rinadigan profil nomi uchun
alohida o‘zgartirish so‘ralmagan. Yangi kontent va profil havolalarida joriy
username ishlatilsin. Mavjud VPS/local env’da `INSTAGRAM_HANDLE` berilgan
bo‘lsa, u kod defaultidan ustun: keyingi deployda `mirabilis_on` ga moslang.
Avtomatsiya nomi va prompti yangilandi, jadval saqlandi.

Oldin nashr qilingan video va captionlar tarix sifatida saqlandi. Yangi `media/studio/mirabilis-javob-ortida.mp4` @mirabilis_on bilan qayta
eksport qilindi; 18 soniya, 1080×1920, 24 fps. To‘rtta sahna va footer
tekshirildi, dekodlangan audio original bilan bir xil. Eski MP4 tarixiy
namuna sifatida saqlandi. Yangi video hozircha rejalashtirilmagan.

## 2026-11-06 yangilanishi

Telegram uchun foydalanuvchi so‘ragan interval: 90 daqiqa
(`POST_INTERVAL_HOURS=1.5`), Toshkent kuni uchun 18 ta limit saqlanadi.
Kod, yangi deploy va namuna sozlamalari yangilandi. Mavjud VPS environment
qiymati kod defaultidan ustun turadi: serverdagi intervalni ham yangilash
kerak. Bu sessiyada VPS SSH ulanishi yo‘q; jonli o‘zgarish tasdiqlanmagan.

Instagram tanishtiruv posti Metricool provider yozuvida PUBLISHED deb
tekshirildi: https://www.instagram.com/reel/DfYzwL0jjg9/
YouTube va X ulanmagan; ma’qullangan original studio video uchun platforma
matnlari `media/studio/` ichida tayyorlandi. Ular hali nashr qilinmagan.

# Mahalliy Codex’da davom ettirish

Video shabloni yangilandi: `reel_layout.py`, qisqa subtitrlar, sahna hisoblagichi,
progress chizig‘i va mahalliy demo kliplar uchun `assets.json` qo‘llovi bor.
32 ta host testi o‘tgan, shu jumladan ikki klipning turli sahnalarda to‘g‘ri
chiqishi hamda narratsiya+musiqa aralashuvi. Subtitr so‘z vaqtlari taxminiy.
Yangi modul Docker/installer nusxalash ro‘yxatlariga qo‘shilgan; eski ef0889c
server image’i bu yangilanishni o‘z ichiga olmaydi. Serverda yangi image yig‘ib
alohida preview bilan tekshirish kerak; mavjud Telegram xizmatlariga tegmang.

Instagram tahririy oqimi ham qo‘shildi: `INSTAGRAM.md`ni o‘qing.
`python prepare_reel.py --demo` tarmoqsiz musiqali vertikal video yaratadi (FFmpeg kerak).
Haqiqiy yangilik va ovoz uchun mavjud Gemini environment sozlamalaridan foydalaniladi.
Meta klienti va final videolar jadvali kodi bor. Metricool akkaunt ulanishi tasdiqlangan.
2026-11-05 tekshiruvida birinchi matnli, original musiqali tanishtiruv Reels
2026-11-06 10:00 Asia/Tashkent uchun Metricool’da autoPublish=true, PENDING
holatida saqlangan; bu hali nashr bo‘ldi degani emas. Video Metricool serveriga ko‘chirilgan.
2026-11-06 foydalanuvchi yuborgan hisobotda ARM64 ijtimoiy image, 29 test va
jonli Gemini TTS muvaffaqiyatli tekshirilgani qayd etilgan. Tafsilotlar:
`VPS_SOCIAL_STATUS.md`. Bu bulut sessiyasi serverdagi sinovni qayta bajarmagan.
Yuborilgan ovozli Muse videosi 2026-11-07 10:00 Asia/Tashkent uchun Metricool’da
rejalashtirildi; holati PENDING, AI belgisi yoqilgan. VPS’dan tayyor videolarni
Metricool’ga doimiy avtomatik uzatish hali o‘rnatilmagan.

Doimiy Instagram matn+musiqa oqimi Codex’da `Mirabilis On Reels` nomli
avtomatsiya sifatida yoqilgan. Boshlanishi 2026-11-08; dushanba, seshanba,
payshanba, juma va yakshanba tongida Asia/Tashkent bo‘yicha bajariladi.
Vazifa yangi manbani tekshirib, modelning o‘zi o‘zbekcha ssenariy yozadi,
matnli vertikal video va original musiqa tayyorlab, Metricool’da rejalashtiradi.
Bu yo‘l Gemini kalitini talab qilmaydi va VPS joylangan degani emas.
Avtomatsiyaning birinchi ishga tushishi hali tasdiqlanmagan; manba/post holati
`media/publication-index.json`da saqlanadi. O‘tgan nashrlar holatini ham tekshiradi.

Codex’da ushbu loyiha papkasini oching va yangi chatda quyidagini yozing:

> LOCAL_SETUP.md, README.md va DEPLOY.md ni o‘qi. Bu Telegram kanalga tabiiy
> o‘zbekcha AI yangiliklarini joylaydigan loyiha. Kuniga Toshkent vaqti bo‘yicha
> 18 ta postdan oshmasin. Oracle Linux 9 ARM64 VPS’ga joylashni davom ettir.
> Windows’dagi mavjud SSH kalitimdan foydalan; kalit va tokenlarni chatga yoki
> Git’ga chiqarma. Avval serverdagi mavjud fayl va xizmatlarni tekshir.

Server IP, SSH foydalanuvchisi va kalitning **yo‘lini** yangi chatga kiriting.
Kalitning o‘zini yubormang. Windows OpenSSH allaqachon o‘rnatilgan; executable
uchun System32 yoki Sysnative yo‘lini Test-Path bilan aniqlang.

Hozirgi holat:

- 7 ta avtomatik test host Python va Docker ichida o‘tgan.
- Docker image yig‘ilgan; ARM64 serverda bajarilishi hali tekshirilmagan.
- `deploy-vps.sh` sintaksisi tekshirilgan, VPS’da hali ishga tushirilmagan.
- VPS’da Podman o‘rnatish bajarilgan, yakuniy natijani qayta tekshirish kerak.
- SSH ulanishi Windows’dan muvaffaqiyatli bo‘lgan, arxivni serverga ko‘chirish
  hali tasdiqlanmagan.
- Jonli RSS, Gemini va Telegram orqali haqiqiy post yuborish tekshirilmagan.
- Dastur `.env.example` yoki `.env` faylini o‘zi o‘qimaydi. Kalitlar process
  environment orqali beriladi. Foydalanuvchi Windows’da to‘ldirgan faylini
  saqlab qolish kerak; uni commit qilmang.
- `deploy-vps.sh` kalitlarni server terminalida yashirin so‘raydi, AI dry-run
  bajaradi, keyin Quadlet xizmatini ishga tushiradi va real post yuborishi mumkin.
- Holat bazasini saqlash zarur: `/data/posts.sqlite3`. Uni yangidan yaratish
  bilan limit yoki takroriy post himoyasini chetlab o‘tmang.

GitHub orqali olingan ZIP ichida `.git` metama’lumotlari bo‘lmaydi. Mavjud Git
loyihaga fayllarni ko‘chirish kerak bo‘lsa, avval foydalanuvchi o‘zgarishlarini
tekshiring va saqlang. Alohida yangi papkaga chiqarish xavfsizroq.
