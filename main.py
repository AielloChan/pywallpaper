# -*- coding: utf-8 -*-
import re
import os
import sys
import json
import time
import random
import urllib2
import win32gui
import win32con
import win32api

# Current path
ROOT = ""
# Log path
LOG_PATH = "log.txt"
# Replace special chars to this char in file name
NAME_FILL_CHAR = "-"
# Access random index separate
INDEX_FILL_CHAR = "~"
# config path
CONFIG_PATH = "config.json"
# system encode type
SYS_ENCODE = sys.getfilesystemencoding()
# default config
DEFAULT_CONFIG = ('{\n'
                  '    "api_url": "http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8",\n'
                  '    "picture_url_locat": "images [0] url",\n'
                  '    "name_type": "url",\n'
                  '    "wallpaper_fill_type": "fill",\n'
                  '    "picture_store_path": "pics/",\n'
                  '    "picture_postfix": ""\n'
                  '}')


# CurrentDir can get current path
# Because the path is different between run this script and run pyinstaller file
# this func can return the right path
def CurrentDir():
    path = sys.argv[0]
    if path.endswith('.exe'):
        return path[:path.rindex('\\')]
    else:
        return sys.path[0]


# ConcatURL can concat two url
# when the rightURL is a absolute url (such as "http://xxx.com"), it will return the rightURL directly.
def ConcatURL(leftURL, rightURL):
    if rightURL.startswith('http'):
        return rightURL
    host = leftURL[:leftURL.find('/', 7)]
    if rightURL.startswith('/'):
        return host + rightURL
    else:
        return host + "/" + rightURL


# SlashToBacklash as its name
# This func will replace slash("/") to backlash("\") in pathStr
def SlashToBacklash(pathStr):
    return pathStr.replace('/', '\\')


# ConcatPath can concatenate two path
# when the rightURL is a absolute path (such as "C:\Windows"), it will return the rightPath directly.
def ConcatPath(leftPath, rightPath):
    if rightPath.find(':') != -1:
        return rightPath
    if leftPath.endswith('\\'):
        return leftPath + rightPath.strip('\\')
    else:
        return leftPath + '\\' + rightPath.strip('\\')


# MultipleReplace will replace chars, which defined in "excludeStr", to NAME_FILL_CHAR in baseStr
# Example:
#   NAME_FILL_CHAR = "-"
#   > MultipleReplace("123#45*6","#*")
#   "123-45-6"
#
def MultipleReplace(baseStr, excludeStr):
    for char in excludeStr:
        baseStr = baseStr.replace(char, NAME_FILL_CHAR)
    return baseStr


# LegalizeStr can delete some special chars in "baseStr"
def LegalizeStr(baseStr):
    excludeStr = "/:*?<>|\""
    return MultipleReplace(baseStr, excludeStr)


# ReadFile will return file content
def ReadFile(path):
    if not os.path.exists(path):
        Log("%s dosn't exists!" % path, 3, True)
    else:
        if not os.access(path, os.R_OK):
            Log("Can't read %s" % path, 2, True)
    handler = open(path, 'r')
    data = handler.read()
    handler.close()
    return data


# WriteFile will write data to a file
def WriteFile(path, fileName, mode, data):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except:
            Log("Can't write %s to %s" % (fileName, path), 2, True)
    else:
        if not os.access(path, os.W_OK):
            Log("Can't write %s to %s" % (fileName, path), 2, True)
    fullPath = ConcatPath(path, fileName)
    handler = open(fullPath, mode)
    handler.write(data)
    handler.close()
    return fullPath


# ReadJSON is a pack of read json
# If important is True, get item failed will lead program to exit
# If important is False, get item failed will return '' and would not lead program to exit
def ReadJSON(jsonObj, key, important=True):
    if isinstance(jsonObj, dict):
        if jsonObj.has_key(key):
            return jsonObj[key]
        else:
            if important:
                Log("Can't get %s in JSON object %s!" % (key, json), 1, True)
            else:
                return ''
    else:
        if not isinstance(key, int):
            Log("Can't use a string key to access array item.key: %s,json: %s" % (key, json), 1, True)
        if key > len(jsonObj) - 1:
            if important:
                Log("The index is to large.key: %s,json: %s" % (key, json), 1, True)
            else:
                return ''
        else:
            return jsonObj[key]

# Log is record a log
# When doExit is True, the program will exit after log
def Log(message, code=0, doExit=False):
    errDict = {
        0: "Internal error: ",
        1: "Config file error: ",
        2: "Permission error: ",
        3: "File system error: "
    }
    log = time.ctime() + " " + errDict[code] + message
    WriteFile(ROOT, LOG_PATH, 'a', log + '\n')
    if doExit:
        sys.exit()

# LoadConfig can load a json config file
# and return an object
def LoadConfig(configFilePath):
    if not os.path.exists(configFilePath):
        Log("Config dose not exist!Creating a new config file.", 1)
        WriteFile(ROOT, CONFIG_PATH, 'w', DEFAULT_CONFIG)
    data = ReadFile(configFilePath)
    try:
        obj = json.loads(data)
    except:
        Log("Config file syntax error.",1,True)
    return obj

# Fetch can get data from url
def Fetch(url):
    handler = urllib2.urlopen(url)
    data = handler.read()
    handler.close()
    return data

# FindInJson can get item from json by a special way
# "location" is a new way to access json
# more detail see the README.md file
def FindInJson(json, location):
    steps = location.split(' ')
    restObj = json
    for step in steps:
        if step.startswith('[') and step.endswith(']'):
            index = step.strip("[").rstrip("]")
            if index.find(INDEX_FILL_CHAR) != -1:
                indexList = index.split(INDEX_FILL_CHAR)
                minIndex = 0
                maxIndex = 0
                try:
                    if indexList[0] != '':
                        minIndex = int(indexList[0])
                    maxIndex = int(indexList[1])
                    step = random.randrange(minIndex, maxIndex)
                except:
                    Log('locat [] in config file are error.', 1)
                    step = 0
            else:
                step = int(index)
        restObj = ReadJSON(restObj, step)
    return restObj

# set wallpaper at windows
def SetWallpaper(imagePath, fillType='fill'):
    fillDict = {
        "fill": 10,
        "fit": 6,
        "Stretch": 2,
        "tile": 0,
        "center": 0,
        "span": 22
    }
    style = fillDict[fillType]
    key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER,
                                r"Control Panel\Desktop", 0,
                                win32con.KEY_SET_VALUE)
    win32api.RegSetValueEx(key, "WallpaperStyle", 0, win32con.REG_SZ, '10')
    win32api.RegSetValueEx(key, "TileWallpaper", 0, win32con.REG_SZ, "0")
    win32gui.SystemParametersInfo(
        win32con.SPI_SETDESKWALLPAPER, imagePath, 1 + 2)

# main script
if __name__ == "__main__":
    # Init root path
    ROOT = CurrentDir() + "\\"

    # Load config
    config = LoadConfig(CONFIG_PATH)

    # If 'name_fill_char' dose not exist in config file it will use the default 'NAME_FILL_CHAR'
    if ReadJSON(config, 'name_fill_char', important=False) != '':
        NAME_FILL_CHAR = ReadJSON(config, 'name_fill_char', important=False)

    # Get api url from config
    api = ReadJSON(config, 'api_url')
    # Get data from url
    data = Fetch(api)

    # load api content to json obj
    try:
        obj = json.loads(data)
    except:
        Log("The API content is not recognised to be a json type.")

#   # Get picture url from json with the special syntax
    picURL = FindInJson(obj, ReadJSON(config, 'picture_url_locat'))
    # Concat url can avoid the different between "http://xxx.com/xx.jpg" and "/xx.jpg"
    pic_host = ReadJSON(config, 'picture_url_locat', important=False)
    if pic_host != "":
        picURL = ConcatURL(pic_host, picURL)
    else:
        picURL = ConcatURL(api, picURL)

    picName = ""
    # get nameType from config
    nameType = ReadJSON(config, 'name_type')
    # process different nameType
    if ReadJSON(config, 'picture_url_locat').find(INDEX_FILL_CHAR) != -1:
        if nameType != 'url':
            nameType = 'time'
    if nameType == "url":
        if picURL.find("?") == -1:
            picName = picURL[picURL.rindex("/") + 1:]
        else:
            picName = picURL[picURL.rindex("/") + 1:picURL.index("?")]
    elif nameType == "json":
        picName = FindInJson(obj, ReadJSON(config, 'name_locat'))
        picName = MultipleReplace(picName, ReadJSON(config, 'name_exclude_char'))
        try:
            picName.encode(SYS_ENCODE)
        except:
            Log(('The name has special charactor, '
                 'you should use "name_exclude_char" in the config'
                 ' to exclude it.'), 1, True)
    elif nameType == 'time':
        picName = str(int(time.time() * 1000))
    else:
        Log("Don't support this name_type.", 1, True)
    picName = LegalizeStr(picName)

    # Get picture data
    picData = Fetch(picURL)
    fullPath = WriteFile(
        ConcatPath(ROOT, SlashToBacklash(ReadJSON(config, 'picture_store_path'))),
        picName + ReadJSON(config, 'picture_postfix'), 'wb', picData)
    # Set wallpaper
    SetWallpaper(fullPath, ReadJSON(config, 'wallpaper_fill_type'))
