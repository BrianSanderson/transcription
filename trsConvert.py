#!/usr/bin/python2.7

from bs4 import BeautifulSoup
import argparse
import csv
import re

def main():
    '''
    Read in the XML output of Transcriber for processed audio files,
    iterate through the XML tags looking for a series of defined codes
    and ultimately write out a tab-delimited long-form data frame that
    summarizes the landing and transition behaviors for insects in
    the audio observations.
    '''
    soup = BeautifulSoup(open(args.input))
    metaDict = {}
    insectDict = {}
    ofile = open(args.output, 'wb')
    writer = csv.writer(ofile,delimiter='\t')

    headerLine = ['observer', 'date', 'time', 'exclosure', 'corner',
                  'insectType', 'insectGroup', 'timeStamp', 'behavior',
                  'plant', 'position', 'maleFlowers', 'femaleFlowers', 'notes']
    writer.writerow(headerLine)

    ex1, ex2, ex3 = process_layout(args.layout)
    
    for Sync in soup.find_all(name = 'sync'):
        # If the line contains metadata, extract it
        if re.search(r'\[*\]', Sync.next_element):
            if re.search(r'\[end\]', Sync.next_element):
                a = 1
            elif re.search(r'\[END\]', Sync.next_element):
                a = 1
            else:
                metaDict = meta_data(Sync.next_element)
        # If the line begins with !, update corner
        elif re.search(r'!', Sync.next_element):
            corner = meta_data_update(Sync.next_element)
            metaDict['corner'] = corner
        # If the line begins with i, extract insect data
        elif re.search(r'i*:', Sync.next_element):
            currentIndex, currentPol, polComment = insect_data(
                Sync.next_element)
            insectDict[currentIndex] = currentPol
        # If the line begins with search, print out the search data
        elif re.search(r'search', Sync.next_element):
            insectType, insectGroup, commentSearch = find_search(
                Sync.next_element, insectDict)
            writer.writerow([metaDict['observer'], metaDict['date'],
                             metaDict['time'], metaDict['exclosure'],
                             metaDict['corner'], insectType, insectGroup,
                             Sync['time'], 'search', 'NA', 'NA', 'NA', 'NA',
                             commentSearch])

        # If the line contains exit, print out a terminal line
        elif re.search(r'exit', Sync.next_element):
            insectType, insectGroup, commentSearch = find_search(
                Sync.next_element, insectDict)
            writer.writerow([metaDict['observer'], metaDict['date'],
                             metaDict['time'], metaDict['exclosure'],
                             metaDict['corner'], insectType, insectGroup,
                             Sync['time'], 'exit', 'NA', 'NA', 'NA', 'NA',
                             commentSearch])

        # If the line contains exit, print out a terminal line
        elif re.search(r'lost', Sync.next_element):
            insectType, insectGroup, commentSearch = find_search(
                Sync.next_element, insectDict)
            writer.writerow([metaDict['observer'], metaDict['date'],
                             metaDict['time'], metaDict['exclosure'],
                             metaDict['corner'], insectType, insectGroup,
                             Sync['time'], 'exit', 'NA', 'NA', 'NA', 'NA',
                             commentSearch])
            
        # If the line begins with scan, print out the scan data
        elif re.search(r'scan\s', Sync.next_element):
            commentLine, pos, plant, insectType, insectGroup, males, females = find_behavior(
                Sync.next_element, metaDict, insectDict, ex1, ex2, ex3)
            writer.writerow([metaDict['observer'], metaDict['date'],
                             metaDict['time'], metaDict['exclosure'],
                             metaDict['corner'], insectType, insectGroup,
                             Sync['time'], 'scan', plant, pos, males, females,
                             commentLine])
        # If the line begins with land, print out the land data
        elif re.search(r'land\s', Sync.next_element):
            commentLine, pos, plant, insectType, insectGroup, males, females = find_behavior(
                Sync.next_element, metaDict, insectDict, ex1, ex2, ex3)
            writer.writerow([metaDict['observer'], metaDict['date'],
                             metaDict['time'], metaDict['exclosure'],
                             metaDict['corner'], insectType, insectGroup,
                             Sync['time'], 'land', plant, pos, males, females,
                             commentLine])            
        # Otherwise, wtf?
        else:
            continue
        

def process_layout(layoutFile):
    '''
    Reads in the tab-delimited file describing which plant was at which
    position during the observation period, and return three dictionaries
    to be used for translation of positions from the audio observations.
    '''
    ex1 = {}
    ex2 = {}
    ex3 = {}

    with open(layoutFile) as f:
        for line in f:
            splitLine = line.split()
            if splitLine[2] == "1":
                ex1[splitLine[3]] = [splitLine[0], splitLine[4], splitLine[5]]
            elif splitLine[2] == "2":
                ex2[splitLine[3]] = [splitLine[0], splitLine[4], splitLine[5]]
            elif splitLine[2] == "3":
                ex3[splitLine[3]] = [splitLine[0], splitLine[4], splitLine[5]]
            elif splitLine[2] == 'x':
                continue
            else:
                raise ValueError("incorrect format of layout file")
    return ex1, ex2, ex3


def meta_data(soupLine):
    '''
    Read in metadata line, return dictionary of metadata
    '''
    metaList = re.split(r';', soupLine.strip('\[\n\s+\]'))
    metaDict = {}
    metaDict['observer'] = metaList[0].strip()
    metaDict['date'] = metaList[1].strip()
    metaDict['time'] = metaList[2].strip()
    metaDict['exclosure'] = metaList[3].strip()
    metaDict['corner'] = metaList[4].strip()
    return metaDict


def meta_data_update(soupLine):
    '''
    Read in line where observation corner was change, return
    new corner
    '''
    line = re.split(r'!', soupLine.strip('\n'))
    return line[1]


def insect_data(soupLine):
    '''
    Read in metadata for the currently observed insect, return
    the insect index and the insect ID
    '''
    currentIndex = re.search(r'i[0-9]+:',
                             soupLine).group(0).strip(':\n')
    currentPol = re.sub(r'i[0-9]+:\s', '',
                        soupLine).strip('\n')
    try:
        polComment = re.search(r'\((.+?)\)',
                               soupLine).group(1).strip('\n')
    except AttributeError:
        polComment = ''

    return currentIndex, currentPol, polComment


def find_search(soupLine, insectDict):
    '''
    Read in line containing searching behavior, return the
    insect type, group, and any comments
    '''
    behaviorLine = re.sub(r'\(.*?\)', '', soupLine).strip('\n')
    insectType = insectDict[re.search(r'i[0-9]+',
                                      soupLine).group(0).strip('\n')]
    insectGroup = re.search(r'i[0-9]+',
                            soupLine).group(0).strip('i\n')
    try:
        commentSearch = re.search(r'\((.+?)\)',
                                  soupLine).group(1).strip('\n')
    except AttributeError:
        commentSearch = ''

    return insectType, insectGroup, commentSearch


def find_behavior(soupLine, metaDict, insectDict, ex1, ex2, ex3):
    '''
    Read in line containing positional behavior, return
    any comment, plant position, insect type, and insect group 
    '''
    try:
        commentLine = re.search(r'\((.+?)\)',
                                soupLine).group(1).strip('\n')
    except AttributeError:
        commentLine = ''
    pos = re.search(r'p[0-9]+', soupLine).group(0).strip('p\n')

    if metaDict['exclosure'] == 'ex1':
        plant = ex1[pos][0]
        males = ex1[pos][1]
        females = ex1[pos][2]

    elif metaDict['exclosure'] == 'ex2':
        plant = ex2[pos][0]
        males = ex2[pos][1]
        females = ex2[pos][2]

    elif metaDict['exclosure'] == 'ex3':
        plant = ex3[pos][0]
        males = ex3[pos][1]
        females = ex3[pos][2]

    else:
        raise AttributeError('problem with input')

    insectType = insectDict[re.search(r'i[0-9]+',
                                      soupLine).group(0).strip('\n')]
    insectGroup = re.search(r'i[0-9]+',
                            soupLine).group(0).strip('i\n')
    return commentLine, pos, plant, insectType, insectGroup, males, females


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'a script to convert the '
                                     'audio transcriptions of pollinator '
                                     'behavior into long form data frame')
    parser.add_argument('-i', dest = 'input', metavar = 'example.trs',
                        help = '.trs input file', required = True)
    parser.add_argument('-o', dest = 'output', metavar = 'example.csv',
                        help = '.csv output file', required = True)
    parser.add_argument('-l', dest = 'layout', metavar = 'layout.txt',
                        help = 'tab-delimited exclosoure layout file',
                        required = True)
    args = parser.parse_args()
    main()
