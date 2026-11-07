# Mirabilis On: yangilik tanlash siyosati

Asosiy va’da: muhim texnologiya voqealarini saralab, tekshirib, o‘zbekcha
tushuntirish. Faqat bugungi xabarlar bilan cheklanmaymiz. Nashr paytida oxirgi
14 kun ichida yuz bergan voqealar orasidan ahamiyatlisi tanlanadi.

## Har ishlab chiqarishdagi tanlov

Imkon qadar 5–8 ta ishonchli nomzodni solishtiring. Kamroq munosib voqea
topilsa, ro‘yxatni uydirma yoki mayda xabarlar bilan to‘ldirmang.

Quyidagi ustuvorlikda baholang:

1. **Ta’sir:** odamlarning hayoti, ishi, sog‘lig‘i, energiya, ilm-fan yoki
   infratuzilmada nimani sezilarli o‘zgartiradi? Kimlarga va qanday?
2. **Mazmunli yangilik:** avval bo‘lmagan amaliy imkoniyat yoki jiddiy texnik
   yutuq bormi? Oddiy dizayn yoki mayda funksiya yangilanishi yetarli emas.
3. **Dalil:** rasmiy manba nimani tasdiqlaydi? Tadqiqotmi, cheklangan demo,
   sotuvga chiqqan mahsulotmi yoki haqiqiy joriy etishmi? Ularni farqlang.
   Katta da’volarni imkon qadar mustaqil ishonchli manba bilan solishtiring.
4. **Auditoriya uchun ahamiyat:** o‘zbek tomoshabin nima uchun qiziqishi
   kerak? Mahalliy mavjudlik, narx yoki til qo‘llovini taxmin qilmang.
5. **Tushuntirish:** qiziqarli va rost ssenariy hamda aynan shu yangilikka
   mos tasvirlar bilan mohiyatini ko‘rsatish mumkinmi?

Potensial katta ta’sir — hali yuz bergan natija emas. Kutilma va cheklovlar
ochiq aytilsin. Dunyoni o‘zgartirish haqidagi reklama gapi dalil hisoblanmaydi.
Mashhur kompaniya nomi, ko‘p ko‘rishlar yoki chiroyli demo o‘zi yetarli emas.

## Qamrov

AI, robototexnika, chiplar va hisoblash, tibbiy texnologiyalar, energiya,
kosmos, muhim raqamli infratuzilma va xavfsizlik voqealari ko‘rib chiqiladi.
Har safar bitta eng kuchli voqea tanlanadi; umumiy AI darsi bilan almashtirilmaydi.

Voqea sanasi, dastlabki e’lon sanasi va keyingi tuzatishlarni tekshiring.
Yangi maqola eski voqeani qayta yozsa, bu uni yangi qilmaydi. Bir haftalik
xabarni «bugun» yoki «hozirgina» deb bermang. Muhim va tasdiqlangan nomzod
topilmasa, shunchaki post sonini to‘ldirish uchun video chiqarilmang.

## Tanlovni qayd etish

Video formati [INSTAGRAM_FORMATS.md](INSTAGRAM_FORMATS.md) bo‘yicha yangilikka
qarab tanlanadi. Har safar bir xil Blender obyekt/yozuv shabloni ishlatilmaydi.
`publication_hold=true` — tayyor MP4’ni chiqarish to‘xtatilganini bildiradi;
mavzuning o‘zi yangi saralashda qoladi. Mavjud materialni ko‘chirishdan oldin
foydalanish huquqi va haqiqiy namoyishligi tekshiriladi.

Har post papkasidagi `selection.json`da nomzodlarning ochiq manba havolalari,
voqea va e’lon sanalari, ta’siri, dalili, cheklovi hamda nima uchun yakuniy
mavzu tanlangani qisqa qayd etilsin. Shaxsiy ma’lumot yoki kalit yozilmasin.

8-noyabrdagi oldindan tayyorlangan studio filmi bir martalik kelishilgan
istisno. Undan keyingi Mirabilis videolari shu yangilik mezoniga amal qiladi.
Mavjud jadval, bepul tarif kvotasi, takroriy post himoyasi va sifat tekshiruvi
saqlanadi. Bu hujjat tayyor yangi video yoki uning nashri tasdig‘i emas.

## Telegram’dagi joriy amalga oshirish

Xuddi shu tahririy mezon `news_selection.py` orqali Telegram kodiga qo‘shilgan.
RSS tarixi yig‘iladi, 80 tagacha lead saralanadi, kuchli nomzodlar manbasi
ko‘rib chiqiladi. Telegram auditini `selection.json` emas, mavjud SQLite’dagi
`editorial_runs` saqlaydi. Cheklov va deploy holati `TELEGRAM_EDITORIAL.md`da.
VPS’ga hali qo‘llanmagan; Instagram va Telegram hali alohida ijrochilar.
