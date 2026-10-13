# Concept mockup only: image processing on one real frame (Fallarbor Town), not engine output.
import sys
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont
src = Image.open(sys.argv[1]).convert('RGB').crop((12, 8, 252, 168))
S = 4
base = src.resize((240*S, 160*S), Image.NEAREST)
a = np.asarray(base).astype(np.float32) / 255.0
H, W = a.shape[:2]
yy, xx = np.mgrid[0:H, 0:W]
# --- modern light: dusk grade + warm light pools + bloom + tilt-shift
night = a * np.array([0.38, 0.45, 0.72])
lights = [(55, 30, 20), (160, 32, 20), (172, 150, 20), (22, 50, 12), (87, 98, 12), (122, 80, 16)]   # (x, y, radius) in GBA pixels
L = np.zeros((H, W), np.float32)
for lx, ly, r in lights:
    d2 = ((xx - lx*S)**2 + (yy - ly*S)**2) / float((r*S)**2)
    L += np.exp(-d2 * 2.2)
L = np.clip(L, 0, 1.0)[..., None]
lit = night + a * L * np.array([1.05, 0.82, 0.5]) * 1.15
lit = np.clip(lit, 0, 1)
img = Image.fromarray((lit*255).astype(np.uint8))
glow = img.filter(ImageFilter.GaussianBlur(14))
g = np.asarray(glow).astype(np.float32)/255.0
lum = g.mean(axis=2, keepdims=True)
lit2 = np.clip(lit + np.clip(lum-0.45, 0, 1)*g*1.2, 0, 1)
img = Image.fromarray((lit2*255).astype(np.uint8))
blur = img.filter(ImageFilter.GaussianBlur(5))
m = np.clip((np.abs(yy - H*0.5) / (H*0.5) - 0.45) / 0.45, 0, 1)[..., None]
out = np.asarray(img).astype(np.float32)*(1-m) + np.asarray(blur).astype(np.float32)*m
vig = 1 - 0.45*(((xx/W-0.5)**2 + (yy/H-0.5)**2)*2.2)[..., None]
modern = Image.fromarray(np.clip(out*vig, 0, 255).astype(np.uint8))
# --- PET Lens: the Net layer over the same street
gray = src.convert('L').filter(ImageFilter.FIND_EDGES)
e = np.asarray(gray.resize((240*S, 160*S), Image.NEAREST)).astype(np.float32)/255.0
e = np.clip(e*1.6-0.15, 0, 1)[..., None]
net = np.ones((H, W, 3), np.float32) * np.array([0.02, 0.05, 0.12])
net += a.mean(axis=2, keepdims=True) * np.array([0.05, 0.12, 0.22])
gridm = ((xx % (16*S) < 2) | (yy % (16*S) < 2))[..., None]
net += gridm * np.array([0.0, 0.18, 0.28])
net += e * np.array([0.15, 0.7, 0.85])
netimg = Image.fromarray((np.clip(net, 0, 1)*255).astype(np.uint8))
gl = netimg.filter(ImageFilter.GaussianBlur(6))
netimg = Image.fromarray(np.clip(np.asarray(netimg).astype(np.int32) + np.asarray(gl).astype(np.int32)*0.5, 0, 255).astype(np.uint8))
d = ImageDraw.Draw(netimg)
for (x, y, col) in [(160, 30, (255, 210, 60)), (172, 147, (255, 210, 60)), (87, 95, (120, 255, 160)), (40, 140, (255, 80, 200))]:
    for r in (10, 16, 22):
        d.ellipse([x*S-r, y*S-r, x*S+r, y*S+r], outline=col, width=2)
# --- triptych with labels
try:
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
except Exception:
    f = ImageFont.load_default()
panels = [(base, 'TODAY: the GBA frame'), (modern, 'MODERN LIGHT: dusk and lamps'), (netimg, 'PET LENS: the Net layer')]
pw, ph = 240*S//2, 160*S//2
canvas = Image.new('RGB', (pw*3 + 40, ph + 60), (11, 18, 32))
for k, (im, label) in enumerate(panels):
    canvas.paste(im.resize((pw, ph), Image.LANCZOS if k else Image.NEAREST), (10 + k*(pw+10), 50))
    ImageDraw.Draw(canvas).text((14 + k*(pw+10), 10), label, fill=(230, 237, 247), font=f)
canvas.save(sys.argv[2])
print(canvas.size)
