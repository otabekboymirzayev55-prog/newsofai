"""Build a local review catalogue from verified exports; no publication side effects."""
from datetime import date, timedelta
from html import escape
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'media/batches/2026-11-07'


def build():
    stories = json.loads((ROOT / 'batch_news/stories.json').read_text())
    reserves = json.loads((OUT / 'reserve.json').read_text())
    candidates = {c['id']: c for c in json.loads((ROOT / 'media/news-pool.json').read_text())['candidates']}
    held = sum(bool(candidates.get(s['id'], {}).get('publication_hold')) for s in stories)
    hold_note = f'{held} ta eksport yangi format uchun qayta ishlanishi kerak; shu nusxalar nashrga qo‘yilmasin.' if held else 'Nashrdan oldin manba va sifat yana tekshiriladi.'
    cards, rows = [], []
    ready = 0
    for index, story in enumerate(stories, 1):
        ident = story['id']
        folder = OUT / ident
        report = json.loads((folder / 'production.json').read_text()) if (folder / 'production.json').exists() else {}
        video = folder / 'video.mp4'
        checked = (report.get('status') == 'technical_checks_passed'
                   and report.get('visual_review', '').startswith('assistant inspected')
                   and video.is_file() and hashlib.sha256(video.read_bytes()).hexdigest() == report.get('sha256'))
        ready += checked
        status = 'Tayyor, tekshirildi' if checked else 'Ishlab chiqarish / ko‘rik davom etmoqda'
        if checked and candidates.get(ident, {}).get('publication_hold'):
            status = 'Texnik eksport tayyor; format qayta ishlanishi kerak'
        title = escape(story['title'])
        expiry = (date.fromisoformat(story['date']) + timedelta(days=14)).isoformat()
        slot = story['suggested_slot'][:10]
        if checked:
            media = f'<video controls preload="none" poster="{ident}/cover.jpg" aria-label="{title}"><source src="{ident}/video.mp4" type="video/mp4"></video>'
            links = f'<a href="{ident}/video.mp4" download>MP4 olish</a> · <a href="{ident}/caption.txt">Post matni</a> · <a href="{ident}/contact.jpg">4 sahna</a>'
            md_video = f'[MP4]({ident}/video.mp4) · [post]({ident}/caption.txt)'
        else:
            media = '<div class="pending">Render / ko‘rik</div>'
            links = ''
            md_video = 'Tugallanmagan'
        cards.append(f'''<article><div>{media}</div><div class="copy"><p class="eyebrow">{index:02} / {escape(status)}</p>
<h2>{title}</h2><p>Voqea: {story['date']} · <a href="{escape(story['source'], quote=True)}">{escape(story['publisher'])}</a></p>
<p>{escape(story['caption'])}</p><p class="limit">Cheklov: {escape(story['limitation'])}</p>
<p>Nashr uchun taklif: {slot}, 10:00 Toshkent. 14 kunlik oxirgi sana: {expiry}. <strong>Hali navbatga qo‘yilmadi.</strong></p><p>{links}</p></div></article>''')
        rows.append(f"| {index} | {story['title']} | {story['date']} | {slot} | {expiry} | {md_video} |")
    reserve_html, reserve_md = [], []
    for index, item in enumerate(reserves, 1):
        expiry = (date.fromisoformat(item['date']) + timedelta(days=14)).isoformat()
        extra = ' Nashrdan oldin manevrning haqiqiy holatini yangidan tekshirish shart.' if item.get('requires_special_refresh') else ''
        reserve_html.append(f'''<details><summary>{index:02}. {escape(item['title'])}</summary><p>Voqea: {item['date']}; oxirgi sana: {expiry}. <a href="{escape(item['source'], quote=True)}">Asl manba</a></p><p>{escape(item['note'])}</p><p class="limit">{escape(item['limitation'] + extra)}</p></details>''')
        reserve_md.append(f"| {index} | [{item['title']}]({item['source']}) | {item['date']} | {expiry} |")
    (OUT / 'README.md').write_text(f'''# Mirabilis On: 7 video va 10 zaxira mavzu

**Texnik eksport va kadr ko‘rigi: {ready}/7. Zaxira: {len(reserves)} ta.**

{hold_note} [Amaldagi format yo‘nalishi](../../../INSTAGRAM_FORMATS.md).

[Video katalogi](index.html) · [Tanlov qaydi](selection.json) · [10 ta zaxira tafsiloti](reserve.json) · [Doimiy mavzular ro‘yxati](../../news-pool.json)

Asl manbalar 2026-11-07 kuni ochib tekshirildi. Muhimlik, dalil, kundalik hayotga
ta’sir va tushuntirish imkoniyati bo‘yicha tanlandi. Har bir mavzuda alohida original
konseptual 3D ishlatilgan; mahsulotning haqiqiy namoyishi emas.

| № | Mavzu | Voqea sanasi | Taklif etilgan kun | 14 kunlik oxirgi sana | Fayllar |
|---|---|---|---|---|---|
{chr(10).join(rows)}

Taklif etilgan sanalar **jadvalga yozilmagan**. Nashrdan oldin har bir asl manba
qayta tekshiriladi. Tuzatish, muhim yangi xabar yoki eskirish sabab reja almashishi
mumkin. 8-noyabrga avval rejalashtirilgan video saqlanadi, nusxa yaratilmaydi.
Mavjud tartib: bir kunda bittagacha, haftasiga beshtagacha; Metricool Free uchun
barcha tarmoqlar bo‘yicha oyiga 20 ta nashr chegarasi saqlanadi.

Yakuniy eksport: 18 soniya, H.264 1080×1920, 24 fps, AAC 48 kHz stereo.
Original instrumental bor, diktor ovozi yo‘q. Native 3D 432×768, 8 fps,
4 Cycles samples; OIDN tozalash va har sahnada alohida optical flow ishlatilgan.
Yozuvlar native 1080×1920. Audio mavjudligi va darajalari texnik tekshirildi;
subyektiv eshitib baholash bajarilgan deb da’vo qilinmaydi.

## Saqlangan 10 ta zaxira

| № | Mavzu va asl manba | Voqea sanasi | 14 kunlik oxirgi sana |
|---|---|---|---|
{chr(10).join(reserve_md)}

Bu o‘nta mavzu uchun video hozir buyurtma qilinmagan. Keyingi qidiruv natijalari
shu ro‘yxat bilan birlashtiriladi; muhim eski topilmalar yo‘qolmaydi. Muddati
o‘tgan mavzu tarixda saqlanadi, ammo nashrga yaroqli hisoblanmaydi. ESCAPADE
uchun 7/9-noyabr manevrlarining haqiqiy holati yangidan tekshirilishi shart.
Qisqa kundalik tekshiruv va taxminan 12-noyabrda chuqur qayta saralash ko‘zda tutilgan.

## Telegram holati

Yangilanish kodi va `upgrade-telegram-vps.sh` tayyor. VPS hosti va bu sessiyada
autentifikatsiyalangan ulanish mavjud emas; jonli serverga o‘rnatilmadi.
[Deploy ko‘rsatmasi](../../../TELEGRAM_EDITORIAL.md) · [Renderni davom ettirish](../../../batch_news/README.md).
''')
    (OUT / 'index.html').write_text(f'''<!doctype html><html lang="uz"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mirabilis On — 7 video / 10 g‘oya</title>
<style>:root{{color-scheme:dark;font-family:system-ui,sans-serif;color:#edf1ef;background:#0c1215}}body{{max-width:1180px;margin:auto;padding:28px}}a{{color:#ecc67d}}h1{{font-size:clamp(30px,5vw,56px)}}h2{{font-size:27px}}header{{padding:25px 0 40px}}.eyebrow{{color:#ecc67d;letter-spacing:.07em;font-size:13px}}.intro{{max-width:850px;color:#bec9ce;line-height:1.65}}article{{display:grid;grid-template-columns:270px 1fr;gap:35px;padding:30px 0;border-top:1px solid #344047}}video,.pending{{width:100%;aspect-ratio:9/16;display:block;background:#161e23;border-radius:12px}}.pending{{display:grid;place-content:center;color:#a6b4bb}}.copy{{line-height:1.7}}.limit{{color:#d6ba86}}details{{border-top:1px solid #344047;padding:20px 0;line-height:1.65}}summary{{font-size:19px;cursor:pointer}}footer{{margin-top:35px;border-top:1px solid #344047;color:#a6b4bb;padding-top:25px;line-height:1.7}}@media(max-width:700px){{body{{padding:18px}}article{{grid-template-columns:1fr}}video,.pending{{max-width:320px;margin:auto}}}}</style>
<header><p class="eyebrow">MIRABILIS ON / 2026-11-07</p><h1>7 video. 10 ta keyingi g‘oya.</h1><p class="intro"><strong>{ready}/7 texnik eksport ko‘rildi.</strong> {escape(hold_note)} <a href="../../../INSTAGRAM_FORMATS.md">Yangi format yo‘nalishi</a>. Texnologiyaning muhim yangiliklari: voqea, foyda, dalil va cheklov. Videolar draft; ko‘rsatilgan sanalar nashr taklifi.</p><p><a href="README.md">Umumiy hisobot</a> · <a href="reserve.json">10 g‘oya JSON</a> · <a href="../../news-pool.json">Saqlangan mavzular</a></p></header>
{''.join(cards)}<h2>Keyingi tanlov uchun 10 ta zaxira</h2><p class="intro">Oldingi natijalar keyingi qidiruvda yo‘qolmaydi. Nashrdan oldin manba va 14 kunlik muddat yana tekshiriladi. Bu mavzular uchun hozir video yaratilmagan.</p>{''.join(reserve_html)}
<footer>Har video: 18 soniya · 1080×1920 · H.264 / AAC · original instrumental · diktorsiz.<br>Native 3D: 432×768, 8 fps, 4 samples; denoise va 24 fps interpolatsiya. Yozuvlar native 1080×1920. Asl manbalar 7-noyabrda ochib tekshirildi.<br>Telegram yangilanishi kodda tayyor. Bu sessiyada VPS’ga ulanish yo‘q; serverga o‘rnatilgani tasdiqlanmadi.</footer></html>''')
    print(f'Catalogue: {ready}/7 visually reviewed, {len(reserves)} reserves')


if __name__ == '__main__':
    build()
