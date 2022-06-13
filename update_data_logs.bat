@ECHO OFF
:: Make the log directories if they don't exist
if not exist ".\logs\models\" mkdir .\logs\models\;
if not exist ".\logs\per_stat_lines\" mkdir .\logs\per_stat_lines\

cd .\modules\

:: Run python scripts
::get eligible players
ECHO Getting eligible players...
python .\get_eligible_players.py
ECHO Updated eligible players!

::get gamelogs
ECHO Getting gamelogs...
python .\get_gamelogs.py
ECHO Updates gamelogs!

::scrape lines from DraftKings
ECHO Scraping lines from DraftKings...
python .\scrape_dk.py
ECHO Updated lines!

::assemble df
ECHO Building dataframes...
python .\assemble_df.py
ECHO Built dataframes!

::run predictions
ECHO Making predictions... (this could take 10-15 minutes)
python .\predict.py
ECHO Predictions made!

::Organize data for altair
ECHO Organizing data for interactive charts...
python .\organize_altair_data.py
ECHO Data organized!

ECHO All data has been updated!
PAUSE