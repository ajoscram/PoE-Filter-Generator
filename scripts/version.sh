source scripts/utils.sh

cat changelog.md | line $HEADER_PATTERN | sed s/$HEADER_PATTERN//