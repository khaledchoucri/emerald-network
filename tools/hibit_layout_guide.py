# Draws docs/asset-workflow/references/hibit_battle_layout_528x352.png: the grid battle's layout at 2x
# (hi-bit), from the constants in include/pkbn/grid_internal.h and src/pkbn/grid_draw.c. Our own drawing; no game art.
from PIL import Image, ImageDraw, ImageFont
S = 2
CW, CH = 264, 176                     # PKBN_CANVAS_W/H (include/pkbn/render.h)
PW, PH, GX, GY, ROWS, LIP = 44, 26, 0, 82, 3, 6   # PANEL_W/H, GRID_X/Y, GRID_ROWS, PANEL_LIP (grid_internal.h)
im = Image.new('RGB', (CW*S, CH*S), (20, 24, 36))
d = ImageDraw.Draw(im)
try:
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 11)
except Exception:
    f = ImageFont.load_default()
def box(x, y, w, h, col, label):
    d.rectangle([x*S, y*S, (x+w)*S-1, (y+h)*S-1], outline=col, width=2)
    d.text((x*S+4, y*S+3), label, fill=col, font=f)
for r in range(ROWS):
    for c in range(6):
        x, y = GX + c*PW, GY + r*PH
        col = (220, 70, 70) if c < 3 else (70, 120, 230)
        d.rectangle([x*S, y*S, (x+PW)*S-1, (y+PH)*S-1], fill=tuple(v//4 for v in col), outline=col, width=2)
        d.text((x*S+4, y*S+3), f'{c},{r}', fill=col, font=f)
d.rectangle([GX*S, (GY+ROWS*PH)*S, (GX+6*PW)*S-1, (GY+ROWS*PH+LIP)*S-1], fill=(60, 60, 70), outline=(150, 150, 160))

box(2, 2, 48, 17, (240, 240, 120), 'player HP')
box(CW-70, 2, 68, 17, (240, 240, 120), 'foe name/HP')
box(76, 25, 112, 8, (120, 240, 160), 'Custom gauge')
box(0, GY+ROWS*PH+LIP-3, CW, CH-(GY+ROWS*PH+LIP-3), (200, 200, 200), 'bottom line: queued chip / PA name')
d.text((8, 120), 'Backdrop / Net sky: visible above the grid (y 0-163)', fill=(170, 180, 200), font=f)
d.text((8, 136), 'Fighters stand on panel centres; 64x64 native sprites overlap upward', fill=(170, 180, 200), font=f)
d.text((8, 152), 'Canvas 528x352 = 2x of 264x176. Panel cell 88x52, front edge 12 px. Red = player, blue = foe.', fill=(170, 180, 200), font=f)
im.save('hibit_battle_layout_528x352.png')
print(im.size)
