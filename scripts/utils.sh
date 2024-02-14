HEADER_PATTERN="^#[[:space:]]*"

# trims all leading and trailing whitespace from stdout
trim(){
    tac | sed '/./,$!d' | tac | sed '/./,$!d'
}

# obtains the lines in stdout between two regex patterns,
# including the first and excluding the second
extract(){
    sed "0,/$1/b; /$2/Q" | tac | sed "/$1/Q" | tac
}

# obtains the first line in stdout that matches a pattern
line(){
    sed "0,/$1/b; Q" | tail -n 1
}