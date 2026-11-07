"""Original procedural motion study. Optional: pip install pillow numpy; FFmpeg required.

No model calls, stock footage, product UI or real-person likenesses. This is a
concept sample, not a replacement for verified product demonstration footage.
"""
import argparse
import math
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from reel_audio import synthesize_music

W, H, FPS = 720, 1280, 24


def font(size):
    for path in ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'C:/Windows/Fonts/arial.ttf']:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    raise RuntimeError('A Unicode font is required')


def perspective(image, quad):
    source = [(0, 0), (image.width, 0), (image.width, image.height), (0, image.height)]
    rows, rhs = [], []
    for (x, y), (u, v) in zip(quad, source):
        rows.extend([[x, y, 1, 0, 0, 0, -u*x, -u*y], [0, 0, 0, x, y, 1, -v*x, -v*y]])
        rhs.extend([u, v])
    coefficients = np.linalg.solve(np.array(rows), np.array(rhs))
    return image.transform((W, H), Image.Transform.PERSPECTIVE, coefficients,
                           Image.Resampling.BICUBIC)


def create_frame(t, background, stars, fonts):
    frame = background.copy()
    d = ImageDraw.Draw(frame)
    for x, y, z, phase in stars:
        px = (x + math.sin(t * .25 + phase) * 9 * z) % W
        py = (y - t * (10 + z * 20)) % H
        bright = int(85 + 70 * math.sin(t * .9 + phase)**2)
        r = .6 + z * 1.2
        d.ellipse((px-r, py-r, px+r, py+r), fill=(bright//2, bright, min(255, bright+35)))
    glow = Image.new('RGBA', (W, H))
    gd = ImageDraw.Draw(glow)
    cx = 360 + math.sin(t * .5) * 16
    cy = 570 + math.sin(t * 1.1) * 13
    radius = 91 + math.sin(t * 1.3) * 5
    gd.ellipse((cx-125, cy-125, cx+125, cy+125), fill=(60, 30, 230, 80))
    gd.ellipse((160, 980, 570, 1060), fill=(20, 190, 230, 70))
    frame = Image.alpha_composite(frame, glow.filter(ImageFilter.GaussianBlur(42)))

    # A fictional device, projected in 3D; its screen contains only abstract waves.
    phone = Image.new('RGBA', (300, 550))
    pd = ImageDraw.Draw(phone)
    pd.rounded_rectangle((0, 0, 299, 549), radius=42, fill=(20, 26, 48), outline=(100, 122, 165), width=3)
    pd.rounded_rectangle((12, 12, 287, 537), radius=34, fill=(8, 15, 34), outline=(40, 75, 112), width=2)
    pd.rounded_rectangle((112, 24, 188, 40), radius=8, fill=(0, 3, 12))
    for i in range(36):
        x = 35 + i * 6.5
        amplitude = 8 + 45 * math.sin(i*.45-t*3)**2 * math.sin(math.pi*i/36)
        pd.rounded_rectangle((x, 272-amplitude, x+3, 272+amplitude), radius=2,
                             fill=(60, int(150+i*2), 235, 220))
    pd.ellipse((122, 414, 178, 470), fill=(32, 44, 77), outline=(70, 140, 190), width=2)
    pd.line((144, 437, 150, 447, 157, 435), fill=(160, 230, 255), width=3)
    pd.rounded_rectangle((105, 512, 195, 516), radius=2, fill=(100, 125, 155))
    yaw = -.15 + math.sin(t*.45) * .12
    tilt = .35 + math.sin(t*.6) * .04
    roll = -.12 + math.sin(t*.3) * .04
    zoom = .91 + .09 * min(t/6, 1)
    quad = []
    for x, y in [(-150,-275),(150,-275),(150,275),(-150,275)]:
        x1, z1 = x*math.cos(yaw), -x*math.sin(yaw)
        y1, z2 = y*math.cos(tilt)-z1*math.sin(tilt), y*math.sin(tilt)+z1*math.cos(tilt)
        scale = 900/(900+z2)*zoom
        quad.append((360+(x1*math.cos(roll)-y1*math.sin(roll))*scale,
                     865+(x1*math.sin(roll)+y1*math.cos(roll))*scale))
    frame = Image.alpha_composite(frame, perspective(phone, quad))

    # A synthetic, deliberately stylized avatar, with a sphere shader and soft glow.
    n = 210
    yy, xx = np.mgrid[-1:1:complex(n), -1:1:complex(n)]
    disk = xx*xx+yy*yy
    zz = np.sqrt(np.clip(1-disk, 0, 1))
    light = np.clip(.25+.65*zz-.22*xx-.17*yy, 0, 1)
    bands = .5+.5*np.sin(xx*7+zz*8+t*1.5)
    pixels = np.zeros((n,n,4), dtype=np.uint8)
    pixels[:,:,0] = np.clip(30+light*65+bands*30, 0, 255)
    pixels[:,:,1] = np.clip(60+light*135+bands*20, 0, 255)
    pixels[:,:,2] = np.clip(130+light*125, 0, 255)
    pixels[:,:,3] = np.where(disk<1, np.minimum(255,(1-disk)*5000), 0).astype(np.uint8)
    orb = Image.fromarray(pixels)
    od = ImageDraw.Draw(orb)
    blink = .18 if math.sin(t*1.4)>.985 else 1
    for x in [75, 135]:
        od.ellipse((x-7, 94-10*blink, x+7, 94+10*blink), fill=(230, 255, 255, 235))
    od.arc((87, 112, 123, 133), 5, 175, fill=(210, 255, 255), width=3)
    diameter = round(radius*2)
    frame.alpha_composite(orb.resize((diameter,diameter), Image.Resampling.LANCZOS),
                          (round(cx-radius), round(cy-radius)))
    d = ImageDraw.Draw(frame)
    d.ellipse((cx-125, cy+90, cx+125, cy+128), outline=(65, 176, 224, 200), width=2)
    for i in range(20):
        p = (i/20+t*.2)%1
        px = cx + math.sin(p*math.pi*4+t)*30
        py = 830-p*180
        d.ellipse((px-2,py-2,px+2,py+2), fill=(90, 200, 255, 150))
    d.text((55, 100), 'MIRABILIS ON', font=fonts[0], fill=(112, 225, 236))
    d.text((55, 140), 'KONSEPTUAL ANIMATSIYA', font=fonts[1], fill=(133, 148, 179))
    headline = 'AI siz bilan\ngaplashsa-chi?' if t < 4 else 'Raqamli yordamchi.\nJonli taassurot.'
    d.multiline_text((55, 220), headline, font=fonts[2], fill=(240, 246, 255), spacing=12)
    d.text((55, 1150), '@mirabilis_on', font=fonts[0], fill=(112, 225, 236))
    d.line((55, 1210, 55+610*min(t/8,1), 1210), fill=(82, 180, 213), width=3)
    # Fade in/out creates clean edit points; no prerecorded material is used.
    fade = min(1, t/.5, (8-t)/.6)
    if fade < 1:
        frame = Image.blend(Image.new('RGBA',(W,H),(4,8,20,255)),frame,max(0,fade))
    return frame.convert('RGB')


def render_concept(output):
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError('Choose a new output path')
    output.parent.mkdir(parents=True, exist_ok=True)
    y, x = np.mgrid[0:H, 0:W]
    haze = np.exp(-(((x-360)/420)**2+((y-690)/500)**2))
    pixels = np.zeros((H,W,4), dtype=np.uint8)
    for channel, base, strength in [(0,5,10),(1,9,14),(2,24,29)]:
        pixels[:,:,channel] = base+haze*strength
    pixels[:,:,3] = 255
    background = Image.fromarray(pixels)
    rng = np.random.default_rng(42)
    stars = list(zip(rng.uniform(0,W,85),rng.uniform(180,H,85),rng.uniform(.2,1,85),rng.uniform(0,6.28,85)))
    fonts = [font(22),font(14),font(47)]
    with tempfile.TemporaryDirectory() as tmp:
        music = synthesize_music(Path(tmp)/'music.wav',8,'calm')
        cmd = ['ffmpeg','-hide_banner','-loglevel','error','-n','-f','rawvideo','-pix_fmt','rgb24',
               '-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(music),'-vf','scale=1080:1920:flags=lanczos',
               '-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',
               '-c:a','aac','-ar','48000','-b:a','128k','-t','8','-movflags','+faststart',str(output)]
        process = subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            for i in range(FPS*8):
                process.stdin.write(create_frame(i/FPS,background,stars,fonts).tobytes())
        finally:
            process.stdin.close()
        error = process.stderr.read()
        if process.wait(timeout=60):
            raise RuntimeError('FFmpeg encoding failed: '+error.decode(errors='replace')[:200])
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    print(render_concept(parser.parse_args().output))
