# NewsofAI

Instagram uchun Reels, subtitr, karusel, Stories va musiqa tavsiyalarini
tayyorlash qo‘shildi. Kalitsiz sinov: `python instagram.py --demo`.
To‘liq yo‘riqnoma: [INSTAGRAM.md](INSTAGRAM.md). Bu oqim materiallarni ko‘rib
chiqish uchun saqlaydi, avtomatik Instagram nashrini bajarmaydi.

AI yangiliklarini RSS manbalaridan oladi, Gemini orqali tabiiy o‘zbek tilida
qisqartirib yozadi va Telegram kanalga joylaydi. Python 3.12+ kerak;
qo‘shimcha Python paketlari talab qilinmaydi.

## Ishga tushirish

1. Telegram’da @BotFather orqali bot yarating va uni kanalingizga post yozish
   huquqiga ega administrator qilib qo‘shing.
2. Muhit sozlamalariga `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID`
   (`@kanal_nomi` yoki xususiy kanal uchun raqamli ID), `GEMINI_API_KEY` kiriting.
   Kalitlarni chatga yoki Git’ga yozmang. `.env.example` faqat namuna;
   dastur `.env` faylni avtomatik o‘qimaydi.
3. Repozitoriy katalogida tekshiring: `python3 -m unittest discover -s tests -v`.
4. Avval `python3 bot.py --dry-run` bilan matnni ko‘ring. Bu Gemini so‘rovini
   bajaradi, kanalga yubormaydi va maqolani yuborilgan deb belgilamaydi.
5. `python3 bot.py` doimiy ish rejimini boshlaydi. `--once` bitta siklni bajaradi.

`POST_INTERVAL_HOURS` standart qiymati 2. Bot har 5 daqiqada tekshiradi;
oxirgi yuborishdan kamida belgilangan vaqt o‘tishi kerak. Yangilik bo‘lmasa
post yozmaydi. Toshkent vaqti bo‘yicha bir kunda **ko‘pi bilan 15 ta** post
yuboriladi; bu chegara interval sozlamasidan qat’i nazar amal qiladi.
Faqat oxirgi 3 kundagi maqolalar olinadi. Standart manbalar TechCrunch AI va
The Verge AI; `FEED_URLS` orqali vergul bilan ajratilgan RSS/Atom URL’larini
berish mumkin. `GEMINI_MODEL` standarti `gemini-2.5-flash`.

SQLite holati `.local/posts.sqlite3` da saqlanadi (`STATE_PATH` bilan o‘zgaradi).
Qayta ishga tushirishda shu faylni saqlang va bitta kanal uchun bitta umumiy
baza ishlating. Bir xil URL qayta yuborilmaydi. Bir yangilik turli manbalarda
chiqsa, mavzu bo‘yicha takrorlanishi mumkin.

Telegram so‘rovi javobsiz qolsa, maqola `pending` holatida qoladi va qayta
avtomatik yuborilmaydi: kanalni tekshirib keyin qo‘lda hal qilish kerak.
`pending` yozuvlar ham kunlik limitga kiradi. Tasdiqlanmagan AI xatolari
bo‘lishi mumkin; ishga tushirishdan oldin sinov postlarini ko‘rib chiqing.

Kerakli HTTPS manzillar: `techcrunch.com`, `www.theverge.com`,
`generativelanguage.googleapis.com`, `api.telegram.org`.
Jonli RSS olish, AI yaratish va Telegram yuborish tarmoq ruxsatlari hamda
haqiqiy kalitlar bilan alohida tekshirilishi kerak.
