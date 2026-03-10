#!/bin/bash

# Check if a year was provided
if [ -z "$1" ]; then
    echo "Usage: ./close_year.sh <YYYY>"
    exit 1
fi

YEAR=$1
NEXT_YEAR=$((YEAR + 1))
FILE="./${YEAR}/${YEAR}.journal"
CLOSE_FILE="./${YEAR}/${YEAR}-close.test.journal"
CLOSE_FILENAME="${YEAR}-close.test.journal"
CLOSED_FILE="./${YEAR}/${YEAR}-closed.test.journal"
OPEN_FILE="./${NEXT_YEAR}/${NEXT_YEAR}-open.test.journal"

# Check if the source journal exists
if [ ! -f "$FILE" ]; then
    echo "Error: $FILE not found."
    exit 1
fi

echo "--- Closing Year $YEAR and preparing $NEXT_YEAR ---"

# 1. Verification
if ! hledger -f "$FILE" check; then
    echo "CRITICAL: $FILE contains unbalanced transactions!"
    exit 1
fi


# 0. Add equivalent equity postings to ensure accounting equation is verified
# for any multi-commodity transactions
echo "Step 0: Infer equity postings"
hledger -f "$FILE" print tag:clopen -x > "$CLOSED_FILE"
hledger -f "$FILE" print not:tag:clopen -x --infer-equity >> "$CLOSED_FILE"

# 1. Retain earnings: Append to the current year file
# This clears Income/Expenses to Equity:Retained-Earnings
echo "Step 1: Retaining earnings in $FILE..."
hledger -f "$FILE" close --retain --close-acct=Equity:Retained-Earnings -e "$NEXT_YEAR" -x > "$CLOSE_FILE"
hledger -f "$FILE" close --retain --close-acct=Equity:Retained-Earnings -e "$NEXT_YEAR" -x >> "$CLOSED_FILE"
echo "include $CLOSE_FILENAME" >> "$FILE"

# 2. Compute Opening Balances for the next year
# We create the new file (or append if it exists)
echo "Step 2: Generating opening balances for $OPEN_FILE..."
echo "; Opening balances from $YEAR" > "$OPEN_FILE"
hledger -f "$FILE" close --open type:ALE --close-acct=Equity:Opening-Balances -e "$NEXT_YEAR" -x --show-costs --interleaved  >> "$OPEN_FILE"

# # 3. Compute Closing Balances for the current year
# # This zeros out Assets/Liabilities in the old file
# echo "Step 3: Recording closing balances in $FILE..."
hledger -f "$FILE" close --close type:ALE --close-acct=Equity:Opening-Balances -e "$NEXT_YEAR" -x --show-costs --interleaved >> "$CLOSE_FILE"

echo "Success! $FILE is closed and $OPEN_FILE has been initialized."
