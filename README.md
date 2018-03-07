## Conversion of XML audio transcription files to data tables

### Contents

1. [README.md](https://github.com/BrianSanderson/transcription/blob/master/README.md) this file

2. [trsConvert.py](https://github.com/BrianSanderson/transcription/blob/master/trsConvert.py) Python 2.7 script that performs the conversion of Transcriber XML files to a data frame

3. [exampleTranscription.trs](https://github.com/BrianSanderson/transcription/blob/master/exampleTranscription.trs) An example of audio file transcription from Transcriber

4. [exampleLayout.txt](https://github.com/BrianSanderson/transcription/blob/master/exampleLayout.txt) An example of the exclosure layout file

5. [exampleOutput.tsv](https://github.com/BrianSanderson/transcription/blob/master/exampleOutput.tsv) An example of the output of the Python script

### Usage 

`python trsConvert.py --input inputTrsFile.trs --layout exclosureLayoutFile.txt --output outputDataFrame.tsv`

### Notes

In my dissertation research I recorded audio observations of pollinator 
behaviors, which resulted in a set of ~200 audio files. I used the program
[Transcriber](http://trans.sourceforge.net/en/presentation.php) to transcribe
the audio files. 

For this experiment I placed 24 plants in a square deer exclosure and 
narrated the behavior of insects as they moved among the plants. Every
ten minutes the observer would move to a different corner of the exclosure
(A, B, C, or D) to minimize observation bias of the plants closest to where
the observer was standing.

I used the following codes when transcribing the audio files:

* The first record is a metadata line that includes the following information in brackets, separated by semicolons:
    * [observer; date; time; exclosure; corner; weather notes]

* The first observation for an insect is a record of the form "i1: hover fly", which is a unique index of the insect as well as a coarse observation of the type of insect

* The following observations for that insect contain involved an ethogram of behaviors 
    * "search" refers to when the insect was moving around the exclosure, but not near any particular plant
    * "scan" refers to when the insect was close to, but not touching, the flowers of a specific plant. These records include the plant number (e.g. p18 for the plant in position 18).
    * "land" refers to when the insect actually landed on a flower. These records also include the plant number
    * "exit" refers to when the insect left the exclosure

* Records of the form "!C" refer to the time when the observer moved to a different corner of the exclosure

Each record has a time stamp associated with it in the output .trs XML file.
These files are convenient because they are linked to the source MP3 and so
you can refer to the annotations later and easily play the audio to ensure
that the transcription was accurate.

Transcription resulted in a set of ~200 XML files, which was not an
especially useful format for data analysis.
I wrote this Python script to convert the XML output from Transcriber
into a data frame that would be useful for downstream analysis. The 
script uses the [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) XML parser for Python. 

The script requires an XML .trs file from Transcriber, as well as an exclosure
layout file that describes which plants were in which position in the
exclosures during the observation period. I've included examples with this
repository from my research project. The script uses the layout file to 
convert the plant positions into the ID of the plant, as well as the number
of flowers that were in the male or female reproductive phase during the
observation period which is convenient for downstream analysis.

These data will be part of a forthcoming manuscript. It's not clear to me
that the script will be useful to anyone other than myself, but I share it
here in the interest of reproducibility and transparency.
