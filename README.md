# news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/bingx12/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/bingx12/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

THE WORLD TODAY — a pure-stdlib Python program that draws Friday 20 November 2026's world news as a one-page newspaper front page and writes it to `/output/entry.png` (1024×1024 PNG, under 1 MiB, byte-identical on every run).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

No network, no clock, no randomness: `main.py` renders everything itself from bitmap glyphs in `font_data.py` (generated at build time by `tools/generate_font_data.py` from local DejaVu fonts) and encodes the PNG with `zlib`.

## The day's stories

Every story on the page happened or was first reported on Friday 20 November 2026 (Reuters, AP, The Hindu, IMD, Sensor Tower):

- **Lead — justice at The Hague.** The International Court of Justice finds Myanmar responsible for genocide against the Rohingya minority — the first such ruling against a state in the court's history. Nine judges to six; the case was brought by The Gambia in 2019.
- **Weather — eastern India.** Cyclone Akvan makes landfall near Gopalpur, Odisha, at 8.30 am, with winds of 70–80 km/h gusting to 90. More than 300,000 people were evacuated and 69 trains cancelled; no deaths were reported.
- **Summit — Shenzhen.** Trump, Xi and Putin meet in the first-ever three-way summit and issue a four-point joint declaration — but reach no deal on Ukraine or nuclear arms.
- **Markets — Tokyo & New York.** The Nikkei falls 4.8% and SoftBank 16% as AI-bubble fears spread; the S&P 500 drops 2% for a fifth straight day. Anthropic debuts on Nasdaq, closing 17% above its offer price at $97.
- **Culture — Leonida.** Grand Theft Auto VI sells an estimated 24.6 million copies worth $2.36 billion on its first day (Sensor Tower estimate) — the biggest entertainment launch ever. Take-Two has released no official figure.
- **Conflict — Riyadh & Crimea.** A Houthi missile damages Saudi Arabia's sovereign wealth-fund tower in Riyadh's financial district; Ukraine hits the Kerch Bridge a third time in four days.
- **Also today.** The COP31 draft deal drops fossil fuels and the Adaptation Fund wins $50m in pledges; Kenya discharges its last Ebola patient; the U.S. Senate rejects an Iran war-powers resolution 51–48; the U.S. loses its measles elimination status; Democrats nominate Hakeem Jeffries for Speaker 251–11; Cambridge Dictionary picks "Human" as its word of the year.

---

<sub>Entered on [make.fun](https://make.fun/?ref=k6eq9xtw&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
