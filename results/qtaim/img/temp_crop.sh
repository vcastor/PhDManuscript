#!/bin/bash

# Get width and height from nna_no.png
read w h < <(identify -format "%w %h" nna_no.png)

# Find new crop size for nna_yes.png based on the ratio from nna_no.png
read ww hh < <(identify -format "%w %h" nna_yes.png)

# Compute target crop size (in bash, needs 'bc')
aspect=$(echo "$w / $h" | bc -l)
target_w=$ww
target_h=$(echo "$target_w / $aspect" | bc)
if (( $(echo "$target_h > $hh" | bc -l) )); then
  target_h=$hh
  target_w=$(echo "$target_h * $aspect" | bc)
fi

# Crop (rounded to integer)
target_w=$(printf "%.0f" "$target_w")
target_h=$(printf "%.0f" "$target_h")

convert nna_yes.png -gravity Center -crop ${target_w}x${target_h}+0+0 +repage nna_yes_cropped.png

