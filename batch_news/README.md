# Mirabilis On — 7 ta yangilik videosi

Bu buyurtma: 7 ta original video va keyingi tanlov uchun 10 ta zaxira mavzu.
Tanlov manbalari 2026-11-07 kuni ochib tekshirildi. Ommaboplik kafolatlanmaydi;
ahamiyat, dalil va tomoshabinga foyda bo‘yicha tahririy baholandi.

- `stories.json`: 7 ta ssenariy, asl manba, voqea sanasi va cheklovlar.
- `../media/batches/2026-11-07/`: yakuniy MP4, muqova, caption, subtitr va tekshiruv.
- `../media/batches/2026-11-07/reserve.json`: saqlangan 10 ta mavzu.
- `../media/news-pool.json`: keyingi qidiruvlar bilan birlashtiriladigan doimiy ro‘yxat.
- `../news_pool.py`: yangi qidiruvda topilmagan eski muhim mavzuni ham saqlaydi;
  nashr qilingan va muddati o‘tgan yozuvlarni o‘chirmaydi.

Videolar mahsulot ishlashining haqiqiy yozuvi emas. Har mavzuga alohida
original konseptual geometriya: virtual olam, soat, batareya bloklari, avtomobil,
kvant qurilmasi, tajriba samolyoti va molekula. Vendor videosi ishlatilmagan.
Original instrumental bor, diktor ovozi yo‘q. Bu pullik video generatori emas.

## Renderni davom ettirish

Talablar: Linux, Python + Pillow/NumPy, Blender 4.3, FFmpeg, Open Sans shriftlari,
original OIDN 2.5.1 **x86_64** kutubxonasi:
`.local/tools/oidn-2.5.1.x86_64.linux/lib/libOpenImageDenoise.so`.
Kutubxona repoga kiritilmagan. Mavjud ARM64 VPS’da shu fayl ishlamaydi;
arxitekturaga mos denoiser va render muhiti alohida tayyorlanishi kerak.

Repo ildizidan ikki terminalda:

```bash
python batch_news/run_batch.py
python batch_news/monitor.py
```

Runner `flock` bilan ikkinchi nusxani bloklaydi. Tayyor, metama’lumoti mos
MP4’ni tekshiradi va o‘tkazadi. Uzilgan fayllarni alohida saqlaydi; yaroqli
kadrlar mavjud bo‘lsa ulardan davom etadi. Holat:
`.local/news-batch-v1/state.json`; har video uchun `render.log` va `finish.log`.
PID mavjudligi jarayon ishlayapti degani emas — zombie holatini ham tekshiring.

Monitor ishlasa, batch logi `VIDEO DONE N id` qatorlarini saqlashi kerak:
`python batch_news/run_batch.py >> .local/news-batch/batch.log 2>&1`.
`.local/news-batch` avval yaratilgan bo‘lishi kerak. Monitor texnik tekshiruvdan
keyin faqat shu buyurtmaning tugagan videoga tegishli xom kadr keshini o‘chiradi.
Yakuniy video, muqova, metadata va hisobot saqlanadi.

Native 3D: **432×768, 8 fps, 4 Cycles samples**, OIDN tozalash. Har bir kadr
ichida alohida optical flow bilan 24 fps; yozuvlar native 1080×1920.
Yakuniy 18 soniya: H.264 1080×1920 24 fps, AAC 48 kHz stereo.
Bu native 1080p 3D render emas. `production.json` texnik hisobot;
`visual_review` faqat har bir sahna haqiqatan ko‘rilgandan keyin yangilanadi.
Texnik ovoz tekshiruvi musiqa subyektiv eshitib baholangani degani emas.

## Avtomatik qayta boshlash chegarasi

Render Blender/FFmpeg orqali lokal hisoblanadi; model API tokeni sarflanmaydi.
Lekin cloud sessiyasi pauza bo‘lsa, jarayonlar ham to‘xtashi mumkin. Suhbat
o‘z limitining tiklanganini kuzatib o‘zini shu zahoti qayta ishga tushira olmaydi.
Mavjud `Mirabilis On Reels` rejalashtirilgan vazifasiga tugallanmagan batch’ni
keyingi jadvaldagi ishga tushishda davom ettirish ko‘rsatmasi qo‘shilgan.
Bu hali muvaffaqiyatli avtonom render sikli kuzatilgani yoki limitni chetlab
o‘tish kafolati emas. Yangi pullik agent platformasi kerak emas.

## Nashrdan oldin

`suggested_slot` faqat taklif. Bu 7 ta video avtomatik navbatga qo‘yilgan degani
emas. Asl manbani yana ochib, tuzatishlar va voqea 14 kunlik chegarada ekanini
tekshirish kerak. 27-oktabr mavzusi 10-noyabrdan keyingi nashr uchun yaroqsiz;
3-noyabr mavzularining oxirgi kuni 17-noyabr. Eskirgan tayyor videoni shunchaki
jadvalni to‘ldirish uchun chiqarmang. Muhim yangi xabar chiqsa reja o‘zgarishi mumkin.

2026-11-08 10:00 Toshkent uchun mavjud video saqlanadi:
UUID `9192951298047626537`; ikkinchi nusxa yaratilmaydi.
Mavjud cheklov: bir kunda bittagacha, haftasiga beshtagacha; Metricool Free
hisobida barcha tarmoqlar uchun oyiga jami 20 ta nashr. Keyingi ko‘rib chiqish:
qisqa kundalik yangilash, taxminan 12-noyabrda chuqurroq qayta saralash.
Zaxiradagi 10 mavzu uchun hozir video ishlab chiqarish buyurilmagan.
