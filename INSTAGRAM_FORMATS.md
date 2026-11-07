# Mirabilis On: yangilikka qarab video formatini tanlash

2026-11-07: foydalanuvchi yettita Blender videosining bir xil tuzilishini
tanqid qildi va yangilik sahifalarining usullarini o‘rganishni so‘radi.
Oldingi ma’qullangan bitta studio film barcha yangiliklarga bir xil shakl
berishga asos bo‘lmaydi. Brend saqlanadi, har bir hikoyaning tasviri va montaji
yangilik mazmunidan kelib chiqadi.

## Tekshiruv chegarasi va ochilgan misollar

Instagram profillari to‘liq ochilmadi: `@verge` va `@techcrunch` fetch xatosi,
`@interestingengineering` 429 qaytardi. Cloud HTTP orqali Instagram 403 bilan
bloklangan; shared desktop boshqaruv vositasi bu sessiyada yo‘q. Reels’lar
to‘liq ko‘rib yoki eshitib tahlil qilingan deb aytilmaydi. Quyidagi xulosalar
ochilgan rasmiy video sahifalari va ochiq post metama’lumotlariga tayanadi;
aniq kesish tezligi, ovoz uslubi yoki retention raqamlari o‘lchanmagan.

| Namuna | Tekshirilgan dalil | Mirabilis uchun olinadigan usul |
|---|---|---|
| [The Verge video sahifasi](https://www.theverge.com/video) | Mualliflarning amaliy mahsulot sinovlari va taqqoslashlari bor. | Haqiqiy funksiyani ko‘rsatish, keyin baholash va cheklovni tushuntirish. |
| [TechCrunch Instagram postlari ochiq qaydi](https://picmany.com/techcrunch), [suhbat posti](https://picmany.com/reel/DfFTTQ1NuBV) | Uchinchi tomon keshi: asoschi bilan suhbat va mahsulot yangilanishi haqidagi post tavsiflari. Video ijrosi ko‘rilmagan, ko‘rsatkichlar tasdiqlanmagan. | Savol–javob yoki mahsulot namoyishi hikoyaga tayanch bo‘lishi mumkin. |
| [Interesting Engineering: robot qo‘li](https://interestingengineering.com/ai-robotics/video-robot-hand-performs-magic-tricks-with-precision-using-20-independent-joints) | Maqola ishlab chiqaruvchining haqiqiy namoyishiga havola beradi. | Obyektning o‘rniga dekorativ model yasashdan oldin asl harakatni tushuntirish. |
| [Texnoplov ochiq kanali](https://t.me/s/texnoplov/5405) | Kanal o‘z Instagram profilini va ilmiy mavzudagi Shorts havolasini ko‘rsatadi. | Mahalliy auditoriya uchun qo‘shimcha kuzatish nomzodi; videoning yuz/ovoz/montaj uslubi ko‘rildi deb da’vo qilinmaydi. |

Bular formatni o‘rganish misollari. Eski misolni yangi xabar sifatida chiqarish
buyurtmasi emas. Nashr qilinadigan yangilik uchun 14 kunlik qoida saqlanadi.

## Ishlab chiqarish qarori

Avval yangilik va tekshirilgan dalilni tanlang, keyin tasvir formatini belgilang.
Blender majburiy emas; FFmpeg bilan asl kadr, ekran yozuvi, foto, subtitr,
grafik va ovozni montaj qilish ham mumkin.

| Yangilik turi | Asosiy tasvir | Qo‘shimcha tushuntirish |
|---|---|---|
| AI ilova / yangi funksiya | Haqiqiy ekran yozuvi: vazifa → jarayon → natija | Qisqa taqqoslash, haqiqiy xato yoki cheklov. Kirish bo‘lmasa sinab ko‘rdik deyilmaydi. |
| Robot / yangi qurilma | Foydalanish huquqi tekshirilgan asl demo yoki o‘z sinovimiz | Kerakli joyni kattalashtirish, sekinlashtirish, bitta mexanizmga belgi. |
| Kosmos / zavod / energetika | Asl voqea kadri yoki tekshirilgan rasmiy foto | Xarita, jarayon sxemasi yoki bitta muhim raqam. |
| Hisobot / xavfsizlik / yangi ilmiy natija | Asl hujjatning kerakli qismi, tushunarli raqam yoki taqqoslash | O‘zimiz chizgan 2D infografika, avval/endi yoki reja/natija farqi. |
| Ichki mexanizm ko‘rinmaydigan mavzu | Haqiqiy dalil va unga mos tushuntirish | Faqat zarur qism uchun original 2D/3D animatsiya, konsept ekani aniq ko‘rsatiladi. |

Har mavzuda turli foydali kadr bo‘lsin. Bir obyektning to‘rt rakursi va katta
yozuvni almashtirish avtomatik asosiy format bo‘lmasin. Faqat matnni yoki obyektni
almashtirish yetarli qayta ishlash hisoblanmaydi.

Tavsiya etiladigan skelet: dastlabki 1–2 soniyada kuchli haqiqiy kadr va
aniq savol/xabar; keyin nima yangiligi, amaliy foyda, dalil va cheklov.
Davomiylik va kadrlar soni hikoyaga qarab tanlanadi, hammasi 18 soniya va
to‘rtta sahnaga majburlanmaydi. Montaj voqea va fikrni kuzatsin; har ikki
soniyada kesish yoki ko‘p effekt avtomatik talab emas. Bu tahririy tavsiya,
raqiblarning o‘lchangan montaj statistikasi emas.

Ravon o‘zbekcha sharh va qisqa subtitr afzal. Haqiqiy sozlangan Gemini ovozi
bo‘lsa talaffuzini tekshirib ishlatish mumkin. Ovoz bu sessiyada tayyorlangani
da’vo qilinmasin; yangi pullik provayder yoki obuna buyurtma qilinmagan.
Muhim narsa tomoshabin nimani ko‘rib tushunayotgani; musiqa sharhni bosmasin.
Boshlovchi majburiy emas, uydirma odam yoki soxta mahsulot namoyishi yaratilmang.

## Hozirgi yettita draft

`media/batches/2026-11-07/` MP4’lari texnik jihatdan tayyor, lekin yangi
format talabi bo‘yicha **needs_format_revision**, `publication_hold=true`.
Fayllar va yaxshi faktlar saqlanadi. Ular shu holatda avtomatik navbatga
qo‘yilmasin. Hikoyalar qidiruv va saralashda qoladi, tayyor eski MP4 esa
nashrga yaroqli deb hisoblanmaydi.

Qayta ishlashdan keyin yangi video, huquq qaydi, tekshirilgan manba, haqiqiy
audio/vizual ko‘rik va SHA saqlanadi. Shundan keyin muharrir `publication_hold`
ni olib tashlashi mumkin; yangi qidiruv natijalarini birlashtirish bu belgini
avtomatik yechmaydi. Yangi foydalanuvchi ruxsatini har safar so‘rash talab
qilinmaydi: odatdagi fakt, sifat, huquq, jadval va takror himoyalari bilan ishlang.

8-noyabrga oldin kelishilgan studio posti bu yettita draftdan alohida;
ushbu tuzatish mavjud nashrni bekor qilish yoki nusxa yaratish buyrug‘i emas.

## Konkret yangi montaj rejasi: NASA X-70

Bu hali yaratilgan yangi video emas, mavjud yangilik uchun tahririy reja:

1. Rasmiy, huquqi tekshirilgan X-70 fotosi/kadri bilan boshlash: «NASA’ning
   yangi uchuvchi laboratoriyasi». Umumiy 3D samolyotni asosiy tasvir qilmaslik.
2. Qisqa o‘zbekcha sharhda 4-noyabr e’loni va platforma nima uchun kerakligini
   aytish. Foto/video shu samolyotga tegishli ekanini tekshirish.
3. Almashtiriladigan tajriba yuki va boshqaruv sinovini o‘zimiz chizgan oddiy
   2D belgilar bilan tushuntirish; hisoblangan parvoz natijasi qilib ko‘rsatmaslik.
4. Asl tasvirga qaytib foydani va ilk NASA parvozi hali oldinda ekanini aytish.
5. Qisqa yakun, manba va @mirabilis_on. Yakuniy uzunlik o‘qish/ovoz ritmiga mos.

Tasvirni olish imkoni yoki huquqi yetishmasa, qo‘shimcha manba izlanadi yoki
mos boshqa kuchli xabar tanlanadi. Qo‘lda yasalgan umumiy modelni haqiqiy demo
sifatida berib bo‘shliq to‘ldirilmaydi.
