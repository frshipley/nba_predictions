This is my TDI capstone project involving predicting NBA stats, and comparing with gambling odds from DraftKings.

To build or update logs, lines, and predictions, please run `update_data_logs.bat`

`update_data_logs.bat` runs the following modules in order:
- `get_eligible_players.py`
- `get_gamelogs.py`
- `scrape_dk.py`
- `assemble_df.py`
- `predict.py`
- `organize_altair_data.py`

After the logs are all created, you can use the interactive charts in `interactive_charts.ipynb`

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/frshipley/nba_predictions/HEAD)