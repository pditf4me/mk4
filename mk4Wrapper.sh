#!/bin/bash

#TODO Edit here for path to mk4.py file
workingDir="./"

# get the current working directory
curdir=$(pwd)

# make Test mkv file
firstMkv=$(ls *.mkv | head -n 1)
python "${workingDir}makeTest.py" "$firstMkv"

# create an array of mkv files
mkvfiles=()

# loop over mkv files in current directory
for file in "$curdir"/*.mkv; do
    # add absolute path of mkv file to the array
    mkvfiles+=("$file")
done

# change to your target directory
cd "$workingDir"

# initialize loop counter
loopcount=0
looptwo=0
# loop over the mkvfiles array
for mkv in "${mkvfiles[@]}"; do
    # increment loop counter
    ((loopcount++))

    # check if first loop
    if [ $loopcount -eq 1 ]; then
        echo "First loop"

        # run your python script with the mkv file as an argument
        python mk4.py "$mkv"

        # get the name of the old file
        old_file="${mkv}"

        # get the name of the new file
        baseName="${mkv%.*}"
        new_file="${baseName}-mk4.mp4"

        # while loop until sizes are equal
        while [ $looptwo -ne 1 ]; do
            # get the size of the new file
            new_file_size=$(stat -c%s "$new_file")

            # get the size of the old file
            old_file_size=$(stat -c%s "$old_file")

            # calculate percentage difference
            percent_diff=$(echo "
define abs(x) {
  if (x < 0) return (-x);
  return (x);
}
abs($new_file_size - $old_file_size) * 100 / (($new_file_size + $old_file_size) / 2)" | bc -l)


            # check if the new file is larger or smaller
            if [ $(echo "$percent_diff > 15" | bc) -eq 1 ]; then
                echo "Percent Difference greater than 15"
                echo "Percent: ${percent_diff}"

                # Check if the newfile is smaller or larger.
                # If newfile is smaller: 
                if [ $(echo "$new_file_size < $old_file_size" | bc) -eq 1 ]; then
                    # Edit the config.ini file : CRF = 22 to smaller value
                    # Run python file that changes config
                    echo "Original file smaller. Changing CRF value and rerunning."
                    python editConfig.py minus
                    rm $new_file
                    python mk4.py "$mkv"
                # If newfile larger:
                elif [ $(echo "$new_file_size > $old_file_size" | bc) -eq 1 ]; then
                    # Edit the config.ini file : CRF = 22 to larger value
                    # Run python file that changes config
                    echo "Original file larger. Changing CRF value and rerunning."
                    python editConfig.py plus
                    rm $new_file
                    python mk4.py "$mkv"
                fi
                
            elif [ $(echo "$percent_diff < 15" | bc) -eq 1 ]; then
                echo "Percent Difference less than 15"
                echo "Percent: ${percent_diff}"
                looptwo=1
                # remove the old mkv file
                rm "$mkv"
                # rename the new mp4 file to better
                python updateFilename.py "$new_file"
            fi

            # wait for a bit before next check
            sleep 2
        done
    else
        # get the name of the new file
        baseName="${mkv%.*}"
        new_file="${baseName}-mk4.mp4"

        # run your python script with the mkv file as an argument
        python mk4.py "$mkv"
        # remove the old mkv file
        rm "$mkv"
        python updateFilename.py "$new_file"
    fi
done


rm "${curdir}/00000test.mp4"
