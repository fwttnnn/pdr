#!/bin/sh

models=("sbert" "st5" "ft" "w2v")

for m in "${models[@]}"; do
    # NOTE: change the filename accordingly
    filename="@10-${m}"
    
    ./pdr.py -tvHm "$m" > "$filename"
    cp data/plot/scatter.png "${filename}.png"
    cp data/plot/scatter-debug.png "${filename}-debug.png"
done
