# ASSET-005 revision 2 — backdrop A

Tool: image_gen.imagegen. References: ASSET-005/v001/backdrop.png and ASSET-001/v003/variant-a-stepped-corners.png. Original output retained in raw/backdrop.png.

## Exact prompt

EDIT the first attached BACKDROP into revision2, using secondapprovedconcept only for deeperNETsky/gridmood. Keep ONEfullopaque3:2landscapebackground ONLY, no panels,HUDframes,fighters,attacks,motes,streams,text,logos. Native528x352 orinteger2x1056x704. TOPsky must show clearlyDISTINCT flatnavybands: #040c1c darkesttop, #071833 uppermiddle, #0b2550 lower sky, #103473 nearhorizon; don'tusealmostidenticalnavyshades. Pixelartflatcolorsteps, no smoothgradients. At nativey138..149 draw a VISIBLE12pixel-tallhorizonlightband with3–4discreteblue steps #103473→#144283→#1a4f9c, strongestjustabovehorizon y150. No blurredbloom. Gridfloorbegins exactlyy150 (=42.6%imageheight), perspective recedesinto horizon at x264 centered. Verydense gridlinesnearhorizon andwiderspacingdownward: gapy150..164shouldreadasFLOORDEPTH evenwhenbattlepanelscovery164..333. At leastfourthinperspective horizontalgridlinebands withinfirst14pixelsbelowhorizon, andclear convergingverticalgridrays. Grid brighternearhorizon (#1460b0) anddarkernarforeground (#083e86); extremelysubtleflatnavyfloorfill, NOspeckletexture. Nothingabove#1a4f9cexceptnearhorizongridlines, no cyanwhitepoints; futuregamepanelsmuststaybrightestandclearest. Exact1nativepixelgridlinesatnative528grid with crisp staircasepixels,noanti-aliasing,smoothmotionblur. Originalcalmdigitaldepthbackground, notflatpattern, no addedfranchisedeviceorextractedart. Atmost16palettecolors. Thefullimageextendsgridfloor tobottom withquietemptyspace,no bakedlighting onto futurepanels. No text or symbols. Static partAONLY.

## Processing

Run `python poc/assets/generated/ASSET-005/v002/cleanup.py` from repository root. Pillow and NumPy are required. See processing.json for source geometry, palette and horizon translation. Panel composite is a contrast review aid, not an integrated game screenshot.
