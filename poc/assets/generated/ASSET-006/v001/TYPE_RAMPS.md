# Proposed type ramps

Type order matches ASSET-006. These are original numeric palette proposals; Fire is fixed by STYLE.md. `type_ramps.json` is the machine-readable record and `type_ramps.png` renders exact 16×16 swatches (80×272 total).

+| Type | Outline | Shade | Base | Light | Highlight |
| --- | --- | --- | --- | --- | --- |
| Normal | `#302c25` | `#6d6553` | `#b4a68e` | `#ded1b4` | `#fff2dc` |
| Fighting | `#39131b` | `#7d2434` | `#c94250` | `#ef8b87` | `#ffe2d6` |
| Flying | `#1e2b45` | `#53688f` | `#91aacf` | `#c5d8f0` | `#f0f7ff` |
| Poison | `#2c123e` | `#5c2877` | `#9744b5` | `#cb87df` | `#f2d6fa` |
| Ground | `#302014` | `#68442a` | `#ad7945` | `#dca563` | `#fbe2b6` |
| Rock | `#302922` | `#665542` | `#a48d68` | `#d3bd91` | `#f4e4c5` |
| Bug | `#1f3014` | `#4b6420` | `#8fa83c` | `#c8db75` | `#edf7c9` |
| Ghost | `#15132f` | `#39345f` | `#65568f` | `#9c89c2` | `#ddd1f2` |
| Steel | `#172b34` | `#47636c` | `#819aa4` | `#b5d0d8` | `#edf9fc` |
| Fire | `#9d220f` | `#dc4b24` | `#fc871f` | `#fef237` | `#fefdf2` |
| Water | `#092b46` | `#125786` | `#248fc4` | `#75c8ea` | `#d6f3ff` |
| Grass | `#103019` | `#245f31` | `#45a64a` | `#8cd979` | `#dff7cb` |
| Electric | `#3c2c06` | `#826011` | `#d5a21b` | `#f6da57` | `#fff4b5` |
| Psychic | `#3e1634` | `#81245f` | `#c84c98` | `#ed97cb` | `#ffe0f3` |
| Ice | `#163b43` | `#33747d` | `#77c3cc` | `#b7e9ed` | `#eaffff` |
| Dragon | `#1c164c` | `#44318b` | `#745bd0` | `#aa97f0` | `#e4dcff` |
| Dark | `#141722` | `#34394b` | `#5b6377` | `#919bb0` | `#d6dfec` |

All five tones increase in linear relative luminance within each ramp. This is a monotonicity check, not a claim of perfectly equal perceptual steps. Review `hit_types_side_by_side_review_4x.png` for type distinction; all 17 previews use identical HIT geometry with direct grey-index replacement. No shader/runtime validation is implied.
