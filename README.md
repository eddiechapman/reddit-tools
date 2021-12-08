# reddit-tools

> Scripts for scraping, cleaning, and analyzing Reddit comment data.

## Installation

Clone this repository onto your machine:

```
git clone https://www.github.com/eddiechapman/reddit-tools.git
```

Make a Python virtual environment and activate it:

```console
cd reddit-tools
python3 -m venv venv
source venv/bin/activate
```

Install the required Python packages into your virtual environment:

```console
pip install -r requirements.txt
```

Create a file called `.env` inside the `reddit-tools/` directory. Enter your Reddit API `CLIENT_ID`, `CLIENT_SECRET`, and `USER_AGENT` values.

*Example values shown below. See [OAuth2 Quick Start Example](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps) for more information.*

```
CLIENT_SECRET=axin3in20s
CLIENT_ID=ei98teube83
USER_AGENT="Scraping project"
```

