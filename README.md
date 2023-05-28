This is the same thing as the original with a few tweaks.


Function:
The main file to run in this fork is mk4Wrapper.sh.
It should be added to your system path.
Run the mk4Wrapper.sh inside the directory you want to convert.


EX:
|Season 01
|-file1.mkv
|-file2.mkv
|-file3.mkv
Run mk4Wrapper.sh inside Season 01.
I recommend linking mk4Wrapper.sh to an Evironment path such as /usr/bin with a filename like mk4
>>chmod ugo+x mk4Wrapper.sh
>>sudo ln mk4Wrapper.sh /usr/bin/mk4



Major changes:
1. The mk4.py file is fed a single file at a time by the bash script.
2. I edited the mk4.py app to save the options for subtitles and audio that is selected for the first file against the working directory. 
#If you want to change the selected audio and subtitle tracks for the directory you're working in delete the audioData.pkl and subData.pkl files in the mk4.py directory.
#That way as long as the other files have the same tracks you don't have to babysit the program while it runs.
3. The mk4Wrapper makes a sample of the first mkv file using moviepy. This is to quickly convert the sample mkv file and get an optimal CRF value. The sample will be converted until the file size is within 15% difference of original. Then the CRF value is used for every mkv file in the directory.
4. After the first file settings are set, no more user input is needed for the working directory.



Notes:
1. Was made with linux in mind. Not sure if it'll work other os.

Required installs:
1. ffmpeg (with libass configured during install)
How I installed it:
>>sudo apt-get install git
>>/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
>>(echo; echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"') >> /home/username/.profile
>>eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
>>sudo apt-get install build-essential
>>brew install gcc
>># Removed ffmpeg if already installed
>>sudo apt remove ffmpeg
>>brew install ffmpeg
>># I had to run it twice
>># After it was installed I rebooted system so ffmpeg was in path

2. moviepy
>>python -m pip install moviepy

