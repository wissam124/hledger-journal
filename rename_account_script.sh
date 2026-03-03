#!/bin/bash
set -euo pipefail

# find ~/Syncthing/hledger/ -type f -name "*.journal" -print0 |
find -E ~/Syncthing/hledger/ -type f -regex ".*/[0-9]{6}\.journal" -print0 |
    while IFS= read -r -d '' file; do
        echo "Processing $file"
        awk -v OLD='Equity:Opening-Balances:GBP' -v NEW='Equity:Opening-Balances' '
    # Start of a transaction when we see a date line
    /^[0-9]{4}-[0-9]{2}-[0-9]{2}([[:space:]].*)?$/ { in_txn=1 }
    # Blank line ends a transaction
    /^[[:space:]]*$/                               { in_txn=0 }

    {
      line=$0
      if (in_txn && line ~ /^[[:space:]]+/) {
        patt = "^[[:space:]]+" OLD "([[:space:]]|$)"
        if (line ~ patt) sub(OLD, NEW, line)
      }
      print line
    }
  ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
    done
