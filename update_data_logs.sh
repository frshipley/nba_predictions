#!/bin/bash

if [ ! -d "logs" ]; then
     mkdir logs
 fi

if [ ! -d "logs/models" ]; then
    mkdir logs/models
fi

if [ ! -d "logs/per_stat_lines" ]; then
    mkdir logs/per_stat_lines
fi

cd modules

# Run python scripts
# get eligible players
echo "Getting eligible players..."
python ./get_eligible_players.py
echo "Updated eligible players!"

# get gamelogs
echo "Getting gamelogs..."
python ./get_gamelogs.py
echo "Updates gamelogs!"

# scrape lines from DraftKings
echo "Scraping lines from DraftKings..."
python ./scrape_dk.py
echo "Updated lines!"

# assemble df
echo "Building dataframes..."
python ./assemble_df.py
echo "Built dataframes!"

#run predictions
echo "Making predictions... this could take 10-15 minutes"
python ./predict.py
echo "Predictions made!"

#Organize data for altair
echo "Organizing data for interactive charts..."
python ./organize_altair_data.py
echo "Data organized!"

echo "All data has been updated!"

