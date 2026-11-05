# Mahalliy Codex’da davom ettirish

Codex’da ushbu loyiha papkasini oching va yangi chatda quyidagini yozing:

> LOCAL_SETUP.md, README.md va DEPLOY.md ni o‘qi. Bu Telegram kanalga tabiiy
> o‘zbekcha AI yangiliklarini joylaydigan loyiha. Kuniga Toshkent vaqti bo‘yicha
> 15 ta postdan oshmasin. Oracle Linux 9 ARM64 VPS’ga joylashni davom ettir.
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
