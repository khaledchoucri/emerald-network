# Battle effect sprites taken from BN6 (bn6f). Each entry: NAME -> (category, index, animation).
# category/index address data/SpritePointersList.s (category = which pointer list, index = entry in it);
# the animation number is the sprite's own animation table. Chosen by looking at decoded frames
# (tools/gen_bn6_gfx.py --preview). The pixels are generated at build time from the user's
# upstream/bn6f checkout and never committed.
FX = [
    # name            cat  idx   anim   what it looks like
    ('HIT',             5, 0x04, 0),  # pink-white starburst
    ('HIT_SMALL',       5, 0x05, 0),  # small white spark
    ('HIT_STAR',        4, 0x26, 0),  # cream starburst
    ('EXPLODE',         5, 0x00, 0),  # big orange/grey cloud
    ('EXPLODE_SMALL',   5, 0x01, 0),
    ('SHOT',            3, 0x06, 0),  # energy shot
    ('CANNON',          3, 0x19, 1),  # cannon with blast
    ('MUZZLE',          5, 0x0f, 0),  # muzzle flash
    ('SLASH',           3, 0x14, 0),
    ('SLASH_WIDE',      3, 0x20, 0),
    ('SLASH_WIDE2',     4, 0x3c, 0),
    ('SLASH_ARC',       4, 0x3b, 0),
    ('LONGSWORD',       4, 0x2f, 5),
    ('BOMB',            3, 0x24, 0),
    ('FIRE_PANEL',      4, 0x02, 1),
    ('FIRE_BURST',      4, 0x48, 0),
    ('FIRE_TALL',       4, 0x24, 2),
    ('FLAME_JET',       4, 0x1b, 2),
    ('FIREBALL',        3, 0x0e, 0),
    ('BUBBLE',          4, 0x23, 0),
    ('BUBBLE_POP',      4, 0x23, 1),
    ('SPLASH',          5, 0x12, 0),
    ('WAVE',            4, 0x22, 0),
    ('ICE',             4, 0x03, 0),
    ('ICE_SPIKE',       4, 0x2c, 0),
    ('BOLT',            4, 0x13, 2),
    ('BOLT_ORANGE',     4, 0x12, 1),
    ('SPARK',           4, 0x32, 0),
    ('SPARKS',          4, 0x32, 1),
    ('TORNADO',         3, 0x17, 0),
    ('WIND',            4, 0x41, 0),
    ('ROCKS',           4, 0x30, 0),
    ('ROCK',            4, 0x05, 0),
    ('BOULDER',         4, 0x08, 0),
    ('POISON',          4, 0x4b, 0),
    ('POISON2',         5, 0x11, 0),
    ('SMOKE',           5, 0x02, 0),
    ('DUST',            3, 0x2e, 0),
    ('CHARGE',          5, 0x0d, 0),
    ('CHARGE_RINGS',    5, 0x1b, 0),
    ('HEAL',            4, 0x0f, 0),
    ('HEAL2',           5, 0x15, 0),
    ('LOCKON',          4, 0x45, 0),
    ('METEOR',          3, 0x31, 0),
    ('SPIKE',           4, 0x17, 0),
    ('VORTEX',          4, 0x0d, 0),
    ('BEAM',            4, 0x20, 1),
    ('CLAW',            4, 0x38, 0),
    ('FANG',            4, 0x10, 0),
    ('CONFUSE',         5, 0x0b, 0),
    ('PARALYZE',        5, 0x07, 0),
    ('LEAF',            3, 0x5c, 0),
    ('LOGS',            4, 0x34, 0),
    ('BARRIER',         4, 0x47, 1),
    ('CRACK',           5, 0x03, 0),
]
