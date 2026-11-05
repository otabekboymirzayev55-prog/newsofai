# Bulut serverga joylash

Bu bot HTTP sayt emas, doimiy ishlaydigan worker jarayonidir. Hostingda
Docker worker yoki VPS tanlang. Uxlab qoladigan web hosting mos kelmaydi.
Bir kanal uchun bitta instance ishlating.

## Hostingdagi sozlamalar

- Dockerfile: `Dockerfile`.
- Muhit o‘zgaruvchilari: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID`,
  `GEMINI_API_KEY`. Kalitlarni hostingning maxfiy sozlamalariga kiriting,
  Git yoki Dockerfile ichiga yozmang. `.env.example` avtomatik o‘qilmaydi.
- Doimiy diskni `/data` ga ulang. `STATE_PATH=/data/posts.sqlite3` image
  ichida belgilangan. Qayta deploy paytida diskni saqlang.
- Bitta replica, avtomatik qayta ishga tushirish yoqilgan bo‘lsin.
- `POST_INTERVAL_HOURS=2` ixtiyoriy; Toshkent kuni uchun 15 ta limit qat’iy.
- Bot kanalda post joylash huquqiga ega administrator bo‘lishi kerak.

Avval shu image va sozlamalar bilan `python bot.py --dry-run` ni ishga
tushiring. Uzbekcha matn va manba havolasini ko‘rgandan keyin odatiy
`python bot.py` buyrug‘iga o‘ting. Kanalda haqiqiy post chiqqanini tekshiring.
AI so‘rovlari va hosting xizmatida to‘lov bo‘lishi mumkin.

## Docker o‘rnatilgan VPS

Quyidagi buyruqlarni loyiha katalogida bajaring. `secrets.env` faylini
serverda checkout tashqarisida yarating, o‘qish huquqini faqat egasiga bering
(`chmod 600`), yuqoridagi uchta o‘zgaruvchini kiriting. Namuna yo‘lni haqiqiy
absolyut yo‘l bilan almashtiring. Faylni chatga yoki Git’ga yubormang.

```sh
docker build -t newsofai .
docker volume create newsofai-data
docker run --rm --env-file /absolute/private/secrets.env -v newsofai-data:/data newsofai python bot.py --dry-run
docker run -d --name newsofai --restart unless-stopped --env-file /absolute/private/secrets.env -v newsofai-data:/data newsofai
docker logs --tail 30 newsofai
```

Kunlik limit va takroriy postlardan himoya shu diskka bog‘liq. Uni o‘chirmang
va boshqa bo‘sh disk bilan ikkinchi botni ishga tushirmang. `pending` yozuv
bo‘lsa, qayta yuborishdan oldin kanalni tekshiring.

Bu fayl joylash yo‘riqnomasi; hosting yaratilgani yoki bot jonli ishlayotgani
degani emas. Ushbu cloud ish maydonidagi jarayon ham 24/7 hosting kafolati emas.
