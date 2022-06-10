This is my TDI capstone project involving predicting NBA stats, and comparing with gambling odds from DraftKings.

The order of operations is as follows:

- `get_eligible_players.py`
- `get_gamelogs.py`
- `scrape_dk.py`
- `assemble_df.py`
- `predict.py`
- `assemble_df_long.py`

The above should all be run as a `cron` job (as soon as I figure out how)

After the logs are all created, you can see past performances by player plotted in `past_performances.ipynb`