This is my TDI capstone project involving predicting NBA stats, and comparing with gambling odds from DraftKings.

Open `interactive_charts.ipynb` to get started. Run all cells in the notebook to get logs, models, and predictions.

The first cell in `interactive_charts.ipynb` runs a batch file, `update_data_logs.bat`, that runs the following modules in order:
- `get_eligible_players.py`
- `get_gamelogs.py`
- `scrape_dk.py`
- `assemble_df.py`
- `predict.py`
- `organize_altair_data.py`

**warning**: updating the data logs can take quite a while. It takes ~15 minutes on my local machine, and ~1+ hr on Binder

After the logs are all created, you can use the rest of the cells in `interactive_charts.ipynb`

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/frshipley/nba_predictions/HEAD?labpath=interactive_charts.ipynb)