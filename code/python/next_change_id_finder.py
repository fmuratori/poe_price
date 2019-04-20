import os
import sys
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.join(os.path.realpath(__file__), os.pardir), os.pardir)))


import requests

import constants
import utilities as utils

def buildFullNextChangeId(index, partialNextChangeId):
    return '-'.join([str(partialNextChangeId) if i == index else '0' for i in range(5)])

def searchLeague(leagueName, index, partialNextChangeId, stepSize):
    print('Started recursive search with params: {} {} {} {}'.format(leagueName, index, partialNextChangeId, stepSize))
    if stepSize < 10:
        return partialNextChangeId

    while True:
        nextChangeId, stashes = utils.getStashBatch(constants.DEFAULT_URL + buildFullNextChangeId(index, partialNextChangeId))
        for stash in stashes:
            if utils.isHealthyStash(stash) and leagueName in stash['league']:
                return searchLeague(leagueName, index, int(partialNextChangeId - stepSize), int(stepSize/10))
            if nextChangeId.split('-')[index] == str(partialNextChangeId):
                return partialNextChangeId
        partialNextChangeId += stepSize

def findOptimalNextChangeId(leagueName):
    results = []
    for i in range(5):
        bestPartialIndex = searchLeague(leagueName, i, 0, 10000000)
        results.append(bestPartialIndex)
        print('Best: {} {}'.format(i, bestPartialIndex))
    print('Best nextChangeId for league {}: {}'. format(leagueName, results))

if __name__ == "__main__":
    findOptimalNextChangeId('Synthesis')

# 348573430-360714130-340379780-391277850-368564540