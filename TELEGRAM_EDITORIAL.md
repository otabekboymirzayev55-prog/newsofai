# Telegram: ahamiyat bo‘yicha saralash

`bot.py` va `news_selection.py` mavjud Gemini kaliti/modeli bilan ishlaydi.
Yangi API provayderi yoki pullik agent platformasi qo‘shilmagan.

1. RSS xabarlari SQLite’da 14 kungacha yig‘iladi. Bot birinchi ishga tushganda
   faqat RSS’da mavjud tarixni ko‘radi: yo‘q maqolalarni internetdan avtomatik
   orqaga qidirish yoki butun internetni kuzatish amalga oshirilmagan.
2. Turli yoshdagi xabarlardan 80 tagacha sarlavha/summary ko‘rib chiqiladi.
   AI muhim 5–8 nomzodni ajratib, asl manbani tekshirish uchun eng kuchli
   uchtagacha xabarni tartiblaydi. Ahamiyat yangilik sanasidan ustun.
3. Tanlangan maqola ochiladi. Model asl e’lon/tadqiqot havolasini faqat
   sahifada kuzatilgan URL’lardan tanlaydi. Asl manba ham alohida olinadi.
   Yangilikning o‘zi asl e’lon bo‘lsa, o‘sha sahifadan foydalanish mumkin.
4. Model voqea sanasi, ahamiyati, cheklovi va faktlarini baholaydi. Sana va
   faktlarga keltirilgan parchalar yuklangan asl matnda aynan bo‘lishi shart.
   14 kundan eski voqea, uydirma parcha yoki manbasiz katta da’vo rad etiladi.
   Yangi maqolaga qayta joylangan eski voqea yangilik deb olinmaydi.
5. Telegram matni RSS summary’sidan emas, ko‘rib chiqilgan fakt va
   cheklovlardan yoziladi. Maqola va asl manba havolalari qo‘shiladi.
6. Kuchli nomzod topilmasa, interval kelgan bo‘lsa ham post yuborilmaydi.

Asosiy mezon `NEWS_SELECTION.md` bilan bir xil: hayot, ish, tibbiyot,
energiya, robototexnika, hisoblash yoki infratuzilmaga mazmunli ta’sir,
dalil, amaliy yangilik va o‘zbek auditoriyasi uchun ahamiyat. Potensial
ta’sirni allaqachon erishilgan natija sifatida yozish taqiqlanadi.

## Himoyalar va xarajat

Kamida 90 daqiqalik interval va Toshkent kuni uchun 18 ta limit saqlanadi.
18 ta — yuqori chegara, to‘ldiriladigan kvota emas. 90 daqiqalik doimiy
interval bilan odatda bundan kam post chiqadi.

Bir xil URL’lar, tracking-parametrli nusxalar va oldin da’vo qilingan
`event_key` bloklanadi. Voqea kaliti model tomonidan chiqariladi; mazmunan
takrorni aniqlash mukammal emas. Oldingi 100 voqea kontekst sifatida beriladi.
Yuborish noaniq tugasa, `pending` hamda voqea da’vosi saqlanadi; avtomatik
qayta yuborilmaydi. Mavjud `posts` jadvali va yozuvlari o‘zgartirilmaydi.

Saralash urinishlari orasida kamida 90 daqiqa bor, shu jumladan xato yoki
munosib xabar topilmagan holatlar. Bu har 5 daqiqada modelga qayta pullik
so‘rov ketishini cheklaydi. Bitta siklda triage, manbani aniqlash, ko‘rib
chiqish va post yozish uchun avvalgidan ko‘proq Gemini so‘rovi ketadi.
Vaqtli audit: `editorial_runs`; manba tarixi: `news_articles`; voqea
da’volari: `news_events`. Bu jadvallar mavjud bazaga qo‘shiladi.

Modelning manba va ta’sir haqidagi hukmi xato qilishi mumkin. Matndagi
parchalarni tekshirish — inson yoki mustaqil faktcheker tekshiruvi emas.
Post faqat olinadigan manba dalillaridan yoziladi, ammo jonli dry-run ko‘rigi
baribir zarur. `--dry-run` kanalga yubormaydi; saralash/audit jadvallarini
yangilaydi va modelga so‘rov yuboradi.

## VPS’ga qo‘llash

Bu kod o‘zgarishi; jonli VPS’da joriy etilgani hali tasdiqlanmagan.
Yangi modul asosiy va social Dockerfile hamda installer ro‘yxatiga kiritilgan.
Mavjud xizmatga installer’ni qayta ishlatmang — u mavjud xizmatni almashtirmaydi.
Serverdagi haqiqiy image, Quadlet, env fayl va volume’ni tekshirib, yangi
image’ni yig‘ish, haqiqiy manba/Gemini bilan dry-run ko‘rigi va o‘sha SQLite
volume/env bilan xizmatni yangilash kerak. Tokenlar chiqmasin, baza o‘chmasin.
Rollback uchun oldingi image saqlansin; yangi yordamchi jadvallar eski kodga
xalaqit bermaydi. Mavjud env’dagi `POST_INTERVAL_HOURS` va `FEED_URLS`
defaultdan ustun. Kerakli qiymat 1.5; eski faqat-AI RSS ro‘yxati berilgan
bo‘lsa, yangilangan kengroq manbalarni ham alohida moslash kerak.
