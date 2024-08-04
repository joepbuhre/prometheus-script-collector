# Check if a file exists
file_exists() {
    local file_path="$1"
    
    if [ -e "$file_path" ]; then
        return 0  # File exists
    else
        return 1  # File does not exist
    fi
}

main() {
    if file_exists "requirements.txt"; then
        pip install -r requirements.txt && echo "Custom requirements succesfully installed" || echo "Something went wrong with installing requirements"
    fi

    ## All done serve the file
    waitress-serve --listen=*:5000 app:app
    
}

main
