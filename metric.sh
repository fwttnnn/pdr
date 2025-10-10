#!/bin/sh

models=("sbert" "ft" "w2v")

for m in "${models[@]}"; do
    # NOTE: change the filename accordingly
    filename="@10-${m}"
    
    ./risperidone.py -tvHm "$m" > "$filename"
    cp data/plot/scatter.png "${filename}.png"
done
