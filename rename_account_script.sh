#!/bin/bash
set -euo pipefail

DIR_PTA="./"
OLD_ACCTNAME="Expenses:Misc:Unclassified"
NEW_ACCTNAME="Expenses:Misc:Test"

find -E $DIR_PTA -type f -regex ".*/[0-9]{4}/[0-9]{6}\.journal" -print0 |
    while IFS= read -r -d '' file; do
        echo "Processing $file"
        awk -v OLD=$OLD_ACCTNAME -v NEW=$NEW_ACCTNAME '
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
