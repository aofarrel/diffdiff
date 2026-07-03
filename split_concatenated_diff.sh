#!/bin/bash
#
# Split a concatenated diff file into multiple sample-level diff files

STRIP_DASH=false
INPUT_FILE="tree_combined.diff"

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--strip-dash)
            STRIP_DASH=true
            shift
            ;;
        *)
            INPUT_FILE="$1"
            shift
            ;;
    esac
done

if [ -z "$INPUT_FILE" ]; then
    echo "Usage: $0 [-d] <filename>"
    exit 1
fi

if [ ! -f "$INPUT_FILE" ]; then
    echo "Can't find input '$INPUT_FILE'"
    exit 1
fi

if [ "$STRIP_DASH" = true ]; then
    echo "Reading $INPUT_FILE, stripping lines starting with '-', and splitting..."
else
    echo "Reading $INPUT_FILE and splitting..."
fi

current_out=""
count=0
PATH_FILE="new_diff_paths.txt"

# Clear the path file if it already exists from a previous run
> "$PATH_FILE"

WORKDIR=$(pwd)

while IFS= read -r line || [ -n "$line" ]; do
    line="${line%$'\r'}"

    # If the line starts with '>', it is a new sample name
    if [[ "$line" == ">"* ]]; then
        sample_name="${line#>}"
        current_out="${sample_name}.diff"
        
        # Create/overwrite the file with the header line
        echo "$line" > "$current_out"
        ((count++))
        
        echo "${WORKDIR}/${current_out}" >> "$PATH_FILE"
    else
        # If we have an active file to write to
        if [ -n "$current_out" ]; then
            if [ "$STRIP_DASH" = true ] && [[ "$line" == "-"* ]]; then
                continue
            fi
            echo "$line" >> "$current_out"
        fi
    fi
done < "$INPUT_FILE"

echo "Split '$INPUT_FILE' into $count diff files"
echo "Paths: ${WORKDIR}/${PATH_FILE}"
