# O‘zbek texnologiya auditoriyasi uchun Instagram

Sahifa: **@safeguard_on**. Profil matni va 14 kunlik boshlang‘ich reja:
[SAFEGUARD_ON.md](SAFEGUARD_ON.md). Qoralama, Gemini ko‘rsatmasi va yangi video
ko‘rinishlarida shu username ishlatiladi. Boshqa akkaunt uchun process environment’da
`INSTAGRAM_HANDLE`ni o‘zgartiring. Bu sozlama Instagram’ga kirish huquqini bermaydi.

Telegram yangilik botiga qo‘shimcha tahririy oqim. Gemini RSS yangiligidan Reels
ssenariysi, ovoz matni, vaqtli SRT subtitr, caption, 5 slaydli karusel, 3 Stories
va musiqa qidiruv tavsiyasini tayyorlaydi. Bu versiya Instagram’ga yubormaydi;
Meta tokeni talab qilinmaydi. Asl manbani o‘qish va nashrdan oldin tekshirish zarur.
AI yozgan faktlar va subtitr vaqtlari avtomatik tasdiqlangan hisoblanmaydi.

## Kalitsiz sinash

Python 3.12+ bilan, loyiha papkasida:

```sh
python instagram.py --demo
```

`.local/instagram/demo-.../` ichida `review.md`, `pack.json`, `caption.txt`,
`voiceover.txt` va `subtitles.srt` yaratiladi. Namuna haqiqiy yangilik emas;
DEMO belgisini olib tashlab yangilik sifatida tarqatmang. Qayta bajarish mavjud
fayllarni almashtirmaydi; boshqa `--out` papkasi bilan yangi nusxa olish mumkin.

## Haqiqiy manbadan tayyorlash

Mavjud `GEMINI_API_KEY` process environment orqali beriladi, `.env` avtomatik
o‘qilmaydi. Tokenni buyruq yoki chatga yozmang. Standart RSS manbalari, `FEED_URLS`
va `GEMINI_MODEL` Telegram botidagi kabi. Bu buyruq bitta yangi material yaratadi:

```sh
python instagram.py
```

Faqat so‘nggi 3 kunlik yangiliklar olinadi. Shu manba uchun papka bo‘lsa, keyingi
yangilik tanlanadi. Bu himoya URL bo‘yicha; turli URL’dagi bir mavzuni muharrir
tekshiradi. Gemini so‘rovi pulli bo‘lishi mumkin. Natija noto‘g‘ri formatda bo‘lsa,
hech qanday chala pack saqlanmaydi. Avtomatik pulli qayta so‘rov yo‘q.

Tekshirilgan mahalliy manba bilan:

```sh
python instagram.py --source-json examples/instagram-source.json --out .local/source-review
```

Bu misol fayli DEMO manbadir; haqiqiy ishda uni o‘zingiz tekshirgan `title`, `url`,
`summary`, timezone bilan `published` maydonli JSON bilan almashtiring. Mahalliy
JSON uchun sana filtri qo‘llanmaydi — eski materialni qayta tahrirlash ham mumkin.
URL uchun sahifa yuklanmaydi; berilgan summary modelning yagona fakt manbasidir.

## 9:16 video ko‘rinishi

FFmpeg (drawtext va libx264 bilan) hamda Unicode TrueType font talab qilinadi.
Windows’da mavjud bo‘lmasa FFmpeg o‘rnating va PATH’ga qo‘shing. Renderer 1080×1920
MP4 matnli qoralama yaratadi; haqiqiy mahsulot tasviri yoki AI ovozini yaratmaydi.

```sh
python render_reel.py .local/instagram/demo-0873f3f3e6de3f9cea7bdb9c --output .local/demo-preview.mp4
```

O‘zingiz yozgan o‘zbekcha ovoz va foydalanishga huquqingiz bo‘lgan mahalliy musiqa bilan:

```sh
python render_reel.py PATH_TO_PACK --output .local/review-with-audio.mp4 --voice PATH_TO_VOICE.wav --music PATH_TO_MUSIC.mp3
```

`PATH_TO_...` qismlarini haqiqiy yo‘llar bilan almashtiring; bo‘sh joyli yo‘llarni
qo‘shtirnoqqa oling. Musiqa 10% ovozda aralashtiriladi, ammo eshitib tekshiring.
Video uzunligi ssenariydan olinadi; uzun audio kesiladi. Ovoz va subtitrni sahna
vaqtlariga moslang. Qoralama belgisi saqlanadi. Nashr uchun haqiqiy demo kadrlarini
video muharrirda qo‘shib, tekshirilgan yakuniy videoni eksport qiling.

Bot trend audio topilganini yoki musiqa huquqi tekshirilganini da’vo qilmaydi.
Instagram ichida akkauntingizga ruxsat etilgan audio yoki mos litsenziyali trekni
tanlang. Trend musiqaning Meta API orqali mavjudligi kafolatlanmaydi.

## VPS va Docker

Telegram xizmati avvalgidek ishlaydi. Installer uni avtomatik Instagram oqimiga
almashtirmaydi yoki mavjud xizmatni yangilamaydi. Yangi image ichida qoralama CLI
bor; doimiy `/data` diskini saqlang va o‘sha mavjud volume’dan foydalaning:

```sh
podman run --rm --env-file /etc/newsofai/bot.env -v newsofai-data:/data localhost/newsofai:latest python instagram.py --out /data/instagram
```

Bu buyruq faqat yangilangan image uchun. `/data/posts.sqlite3` o‘zgartirilmaydi.
`/data/instagram`ni ham saqlang: mavjud qoralama va tahrirlar shu yerda. Docker
image’da FFmpeg yo‘q; video ko‘rinishini FFmpeg o‘rnatilgan kompyuterda tayyorlang.

## Dastlabki ikki hafta

- Haftasiga 4–5 Reels: qisqa yangilik, amaliy vosita namoyishi, AI savodxonligi.
- Haftasiga 1–2 karusel: saqlashga arziydigan qadamlar yoki taqqoslash.
- Stories: so‘rovnoma, savol-javob, auditoriya taklif qilgan vosita sinovi.
- Instagram’da yangi auditoriya bilan tanishing; Telegram’da batafsil manbalar
  va muhokama taklif qiling. Caption havolalari bosilmaydi.

Har material uchun URL, mavzu, format, hook, musiqa, vaqt va 24/72 soatlik
natijalarni yozing: reach, o‘rtacha ko‘rish vaqti, ulashishlar, saqlashlar va
obunalar. Faqat ko‘rish soniga qarab xulosa qilmang. Musiqa yoki hook variantlarini
navbatdagi o‘xshash mavzularda sinang; tavsiyalarga chiqish kafolatlanmaydi.

Avtomatik Instagram nashri keyingi bosqich: akkaunt turi, Meta ruxsatlari,
tasdiqlangan media va saqlanadigan nashr holati alohida ulanadi.
