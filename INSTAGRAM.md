# @safeguard_on — Instagram oqimi

## Yangi video shabloni

Renderer endi yirik sarlavha, sahna hisoblagichi va uzun xatboshi o‘rniga
to‘rt so‘zli subtitr bo‘laklarini chiqaradi. Subtitr vaqti sahna ichida so‘zlar
sonidan taxmin qilinadi; bu avtomatik nutqni tanish yoki aniq forced alignment emas.
Renderer video yoniga shu qisqa bo‘laklar bilan `.srt` faylini ham chiqaradi.

Pack yonidagi `assets.json` orqali mahalliy demo kliplar ulanadi: har sahnaga
bitta element yoki `null`. Masalan, besh sahna uchun:

```json
[
  null,
  {"path":"clips/demo.mp4","rights":"owned","credit":"O‘zimiz yozgan demo"},
  null,
  null,
  null
]
```

Kliplar manifest papkasi ichida bo‘lsin; mp4/mov/webm qabul qilinadi. `rights`
qiymati `owned`, `licensed` yoki `permission`; `credit` manba yozuvidir.
Klip ovozi ishlatilmaydi, asl narratsiya va fon musiqasi saqlanadi. Klip sahna
vaqtiga joylashtiriladi va kerak bo‘lsa takrorlanadi; UI kesib tashlanmasligi uchun
kadr sig‘dirilib, chetlari fon bilan to‘ldiriladi. `--assets` bilan alohida manifest
ham berish mumkin. Klip topilmasa grafik karta ishlatiladi; haqiqiy mahsulot demosini
avtomatik topish/yuklab olish bu o‘zgarishga kirmaydi.

Profil bio’si va 14 kunlik reja: [SAFEGUARD_ON.md](SAFEGUARD_ON.md).
Kod Telegram holat bazasini o‘zgartirmaydi. Metricool’dagi akkaunt ulanishi
tasdiqlandi; birinchi tanishtiruv Reels 2026-11-06 10:00 Asia/Tashkent uchun
rejalashtirilgan (2026-11-05 tekshiruvida PENDING). Bu jonli nashr tasdig‘i emas.

## Hozir yoqilgan avtomatsiya

`Safeguard On Reels` Codex vazifasi 2026-11-08 dan boshlab haftasiga besh marta
(dushanba, seshanba, payshanba, juma, yakshanba) Toshkent tongida ishlashga
sozlangan. Har ishga tushishda ko‘pi bilan bitta yangi, tekshirilgan yangilikdan
matnli va original musiqali Reels tayyorlash, Metricool’da kelajak vaqtga qo‘yish,
manba/post indeksini saqlash va o‘tgan nashr holatini tekshirish topshirilgan.
Kalitsiz yo‘lda ssenariyni avtomatsiyada ishlayotgan model yozadi; bu Gemini TTS
yoki VPS’da worker ishga tushganini anglatmaydi. Hali birinchi rejalashtirilgan
ishga tushish natijasi yo‘q. Xato yoki kerakli harakat bo‘lsa xabar beradi;
odatdagi muvaffaqiyatlar uchun alohida bildirishnoma yubormaydi.

## Bir buyruqda musiqali demo

Python 3.12+, FFmpeg (libx264/drawtext) va Unicode TrueType font kerak.

```sh
python prepare_reel.py --demo
```

`.local/reels/demo-.../preview.mp4` — original sintezlangan fon musiqasi bilan
1080×1920, 26 soniyalik matnli namuna. Shu papkada review.md, pack.json,
caption.txt, voiceover.txt va subtitles.srt bor. Demo haqiqiy yangilik emas,
AI ovozi yo‘q va uni final post sifatida nashr qilib bo‘lmaydi. Mavjud videolar
almashtirilmaydi; boshqa --out bilan yangi nusxa oling.

## Maxfiy sozlamalar va haqiqiy video

Kalitlar process environment yoki aniq --env-file orqali beriladi. .env fayli
avtomatik o‘qilmaydi. Mavjud Windows .env faylingizni saqlang. Mahalliy interaktiv
terminalda mavjud kalitlarni yashirin kiritish uchun:

```sh
python configure_social.py
python prepare_reel.py --env-file .local/social.env
```

Sozlash yordamchisi .local/social.env yaratadi (Linux’da 600), mavjud faylni
almashtirmaydi. Windows’da papka huquqlarini cheklang. Kalitlarni chatga yoki
Git’ga yubormang. Process environment qiymatlari env-fayldan ustun.

Oqim: so‘nggi 3 kundagi RSS → Gemini ssenariysi → sahnama-sahna ovoz → original
instrumental → vertikal MP4. GEMINI_API_KEY kerak; TTS modeli standarti
gemini-2.5-flash-preview-tts, ovoz Kore. GEMINI_TTS_MODEL va GEMINI_TTS_VOICE bilan
almashtiriladi. Model mavjudligi va o‘zbekcha talaffuz jonli hisobda tekshirilishi
kerak. Har sahna alohida pulli so‘rov; tugallangan sahnalar keshlanadi.
Juda uzun/qisqa ovozda jarayon to‘xtaydi, so‘zlar kesib tashlanmaydi.
--music-style upbeat ritmli, standart calm sokin instrumental yaratadi.
Bu trend musiqani qidirish xizmati emas. Instagram kutubxonasi audiosi uchun
akkaunt va foydalanish huquqini tekshiring.

Tayyor materialni qo‘shimcha yangilik/ssenariy so‘rovisiz davom ettirish:

```sh
python prepare_reel.py --env-file .local/social.env --pack-dir PATH_TO_PACK
```

Matn o‘zgarsa eski narration.wav’ni alohida saqlab, pack’dan olib tashlang.
Yangi matn uchun yangi ovoz olinadi, o‘zgarmagan sahnalar cache’dan ishlatiladi.
Karusel va Stories bu bosqichda matn loyihalari, tayyor rasm emas.

Fakt, manba, caption, ovoz va subtitrni tekshirgandan keyin:

```sh
python prepare_reel.py --env-file .local/social.env --pack-dir PATH_TO_PACK --final
```

final.mp4 va .manifest.json yaratiladi. Rasmiy ovoz yozuvingiz bilan ham:

```sh
python render_reel.py PATH_TO_PACK --output PATH_TO_PACK/final.mp4 --voice PATH_TO_VOICE.wav --music PATH_TO_MUSIC.wav --final
```

PATH_TO_... qismlarini almashtiring, bo‘sh joyli yo‘llarni qo‘shtirnoqqa oling.
Renderer matnli video yaratadi; mahsulotning haqiqiy ekran yozuvi yoki AI tasvirini
yaratmaydi. Kerakli demo kadrlarini alohida yozing. Video H.264 24 fps, ovoz AAC
48 kHz. Matnli video ham ishlatilishi mumkin; talaffuz va faktlarni tekshiring.

Ovozsiz matnli tanishtiruv uchun `render_reel.py --final --text-only` bilan
original fon musiqasini qo‘shish mumkin. Demo baribir final sifatida rad etiladi.

## Instagram’ga ulanish

Metricool orqali akkauntni ulab final video va caption’ni rejalashtirish mumkin.
Codex’dagi ulanish tasdiqlangach, uning mavjud imkoniyatlari bilan davom etiladi.

VPS uchun to‘g‘ridan-to‘g‘ri klient ham bor: Instagram Business yoki Creator
akkaunti, Instagram Login tokeni, instagram_business_basic va
instagram_business_content_publish ruxsatlari kerak. Facebook Login tokeni
bu klientga mos emas. Meta app review/access level va token muddati tekshirilsin.
Tokenni avtomatik olish/yangilash hali bajarilmaydi.

INSTAGRAM_ACCESS_TOKEN, raqamli INSTAGRAM_USER_ID va qo‘llab-quvvatlanadigan
INSTAGRAM_GRAPH_VERSION (masalan v25.0, Meta ilovasida tekshiring)ni sozlang.

```sh
python publish_instagram.py --env-file .local/social.env --check-account
```

Haqiqiy username @safeguard_on’ga mosligi tekshiriladi. Meta videoni o‘zi yuklab
oladi: aynan final MP4’ni ommaviy HTTPS manziliga joylang. Hosting/HTTPS’ni
repozitoriy avtomatik tashkil qilmaydi. Masofadagi video mahalliy final bilan
bir xil bo‘lishini ta’minlang; manifest mahalliy fayllarnigina tekshiradi.

Avval tarmoqsiz mahalliy tekshiruv:

```sh
python publish_instagram.py --pack-dir PATH_TO_PACK --video PATH_TO_PACK/final.mp4
```

Haqiqiy nashr:

```sh
python publish_instagram.py --env-file .local/social.env --pack-dir PATH_TO_PACK --video PATH_TO_PACK/final.mp4 --video-url https://YOUR_MEDIA_HOST/final.mp4 --publish
```

Standart buyruq yubormaydi; faqat --publish nashr qiladi. Demo, boshqa akkaunt
uchun pack yoki finaldan keyin o‘zgargan fayllar rad etiladi. processing bo‘lsa
kamida bir daqiqadan keyin --env-file bilan quyidagini bajaring:

```sh
python publish_instagram.py --resume https://SOURCE_ARTICLE_URL
```

creating yoki publishing — noaniq natija: akkauntni tekshirmasdan qayta yubormang.
Kod bunday holatni avtomatik takrorlamaydi. --state bazasini doimiy diskda saqlang;
standart .local/instagram-publications.sqlite3. Toshkent kuni uchun 15 urinish
limiti pending holatlarni ham sanaydi. Baza Telegram bazasidan alohida.

## Vaqtli jadval

.local/queue.json misoli (yo‘llar shu JSON papkasiga nisbatan):

```json
[
  {
    "publish_at": "2026-11-10T19:00:00+05:00",
    "pack_dir": "reels/PACK_ID",
    "video": "reels/PACK_ID/final.mp4",
    "video_url": "https://YOUR_MEDIA_HOST/final.mp4"
  }
]
```

Sana va yo‘llarni haqiqiy rejangizga almashtiring. Timezone majburiy.

```sh
python run_social_queue.py .local/queue.json
```

Bu faqat vaqti kelgan final fayllarni tekshiradi. --env-file .local/social.env
--publish bilan nashr yoqiladi. Cron/systemd yoki Windows Task Scheduler orqali
har 5 daqiqada chaqiring. Bazadagi published yozuvlar takrorlanmaydi.
Scheduler xizmati avtomatik o‘rnatilmaydi. Noaniq holat xato kodi bilan tugaydi.

## Docker va Oracle Linux ARM64

```sh
podman build -f Dockerfile.social -t localhost/newsofai-social:latest .
podman run --rm --env-file /etc/newsofai/social.env -v newsofai-data:/data localhost/newsofai-social:latest python prepare_reel.py --out /data/reels
```

Social image FFmpeg va fontlarni o‘z ichiga oladi. Telegram image alohida.
Mavjud xizmatni almashtirmang. /data/posts.sqlite3 va /data/reels saqlansin.
Queue ishlatilsa --state /data/instagram-publications.sqlite3 bering.
Serverdagi /etc/newsofai/social.env huquqi 600 bo‘lsin. Oracle ARM64 joylash,
jonli Gemini TTS, Instagram nashri va masofaviy media hosting alohida tekshiriladi.

Manbalar: [Gemini speech generation](https://ai.google.dev/gemini-api/docs/generate-content/speech-generation),
[Meta content publishing](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/content-publishing),
[Meta Reels media specifications](https://www.postman.com/meta/instagram/folder/830j7my/reels-publishing).
