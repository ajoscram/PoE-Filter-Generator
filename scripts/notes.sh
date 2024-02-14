source scripts/utils.sh

cat changelog.md | extract $HEADER_PATTERN $HEADER_PATTERN | trim