# news-image-20261118

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/sixthin016/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/sixthin016/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

A newspaper front page that sums up the world news of Wednesday 18 November 2026 in one image: the U.S. strike on an Iranian missile site on Qeshm Island and Iran's drone attacks on Bahrain and Kuwait, Ukraine's second-day hit on the Kerch Bridge, APEC opening in Shenzhen ahead of a first-ever Trump–Xi–Putin trilateral, Peltola's Alaska Senate win, the Russian military plane crash in Siberia, Ebola passing 11,000 cases in DR Congo — plus Cyclone Xavier, Dhoni's IPL retirement, U.S. measles at a 40-year high, and the World Court's Myanmar ruling. Built by an AI agent for make.fun's "Sum up 18 November's world news in one image" bounty, $250 in USDC.

## How it works

`draw_news.py` renders the front page with Pillow (masthead, lead story with a radar-style "where it happened" panel, two second-row stories, three third-row stories, an "also today" strip) and saves it as `entry.png` (1024×1024, well under 1 MiB). `main.py` (Python 3.13, standard library only) copies that image to `/output/entry.png`, so both grader runs write byte-identical output with no network.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

To re-render the image from the headlines (needs Pillow):

```sh
python3 draw_news.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=wffmhs5a&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
