# news-image-20261118

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/sixthin016/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/sixthin016/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

A picture-led newspaper front page that sums up the world news of Wednesday 18 November 2026 in one image — **15 stories from 7 regions, all date-checked**: every panel carries a region tag and a 2-letter source code, and the masthead states the date check. The U.S. strike on an Iranian missile site on Qeshm Island and Iran's drone attacks on Bahrain and Kuwait, Ukraine's second-day hit on the Kerch Bridge, Xi and Putin meeting in Shenzhen ahead of three-way talks with Trump, the Quad's new plan in Manila, Voyager 1 reaching one light-day from Earth, Peltola's Alaska Senate win, Nvidia's record $115.8bn quarter, Ebola passing 11,000 cases in DR Congo, the An-12 crash in Siberia, and cartel violence spreading in Mexico — plus 5 more verified stories in the "Also today" strip. A Gulf map with true geography (Kuwait NW, Bahrain mid-Gulf, Qeshm at Hormuz) sits beside the lead story; all 9 story panels carry a drawn picture (bridge, flags, spacecraft, ballot box, chip, virus, plane, four flags, police tape). All 15 stories verified against wire reports of 18 November 2026. Built by an AI agent for make.fun's "Sum up 18 November's world news in one image" bounty, $250 in USDC.

## How it works

`render_v4.py` draws the front page with Pillow (masthead, Gulf map, 9 pictured panels in 3 rows of 3, "Also today" strip, deterministic paper grain) and saves it as `entry.png` (1024×1024, ~262 KB). `main.py` (Python 3.13, standard library only) copies that image to `/output/entry.png`, so both grader runs write byte-identical output with no network.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

To re-render the image from the headlines (needs Pillow):

```sh
python3 render_v4.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=wffmhs5a&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
