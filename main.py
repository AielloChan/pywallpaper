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

ROOT = ""
LOG_PATH = "log.txt"
NAME_FILL_CHAR = "-"
INDEX_FILL_CHAR = "~"
CONFIG_PATH = "config.json"
SYS_ENCODE = sys.getfilesystemencoding()
DEFAULT_CONFIG = ('{\n'
                  '    "api_url": "http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8",\n'
                  '    "picture_url_locat": "images [0] url",\n'
                  '    "name_type": "url",\n'
                  '    "wallpaper_fill_type": "fill",\n'
                  '    "picture_store_path": "pics/",\n'
                  '    "picture_postfix": ""\n'
                  '}')


def CurrentDir():
    path = sys.argv[0]
    if path.endswith('.exe'):
        return path[:path.rindex('\\')]
    else:
        return sys.path[0]


def ConcatURL(leftURL, rightURL):
    if rightURL.startswith('http'):
        return rightURL
    host = leftURL[:leftURL.find('/', 7)]
    if rightURL.startswith('/'):
        return host + rightURL
    else:
        return host + "/" + rightURL


def TidyPath(pathStr):
    return pathStr.replace('/', '\\')


def ConcatPath(leftPath, rightPath):
    if rightPath.find(':') != -1:
        return rightPath
    if leftPath.endswith('\\'):
        return leftPath + rightPath.strip('\\')
    else:
        return leftPath + '\\' + rightPath.strip('\\')


def Strip(baseStr, excludeStr):
    for char in excludeStr:
        baseStr = baseStr.replace(char, NAME_FILL_CHAR)
    return baseStr


def LegalizeStr(baseStr):
    excludeStr = "/:*?<>|\""
    return Strip(baseStr, excludeStr)


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


def ReadJSON(json, key, important=True):
    try:
        obj = json[key]
    except:
        if important:
            Log("Can't get %s in JSON object %s!" % (key, json), 1, True)
        else:
            return ''
    else:
        return obj


def Log(message, code=0, exitNow=False):
    errDict = {
        0: "Internal error: ",
        1: "Config file error: ",
        2: "Permission error: ",
        3: "File system error: "
    }
    log = time.ctime() + " " + errDict[code] + message
    WriteFile(ROOT, LOG_PATH, 'a', log + '\n')
    if exitNow:
        sys.exit()


def LoadConfig(configFilePath):
    if not os.path.exists(configFilePath):
        Log("Config dosen't exist!", 1)
        Log("Initting config file.", 1)
        WriteFile(ROOT, CONFIG_PATH, 'w', DEFAULT_CONFIG)
    data = ReadFile(configFilePath)
    obj = json.loads(data)
    return obj


def Fetch(url):
    handler = urllib2.urlopen(url)
    data = handler.read()
    handler.close()
    return data


def FindInJson(json, locat):
    steps = locat.split(' ')
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

if __name__ == "__main__":
    ROOT = CurrentDir() + "\\"

    config = LoadConfig(CONFIG_PATH)

    if ReadJSON(config, 'name_fill_char', important=False) != '':
        NAME_FILL_CHAR = ReadJSON(config, 'name_fill_char', important=False)

    api = ReadJSON(config, 'api_url')
    data = Fetch(api)

    obj = json.loads(data)

    picURL = FindInJson(obj, ReadJSON(config, 'picture_url_locat'))
    picURL = ConcatURL(api, picURL)

    picName = ""
    nameType = ReadJSON(config, 'name_type')
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
        picName = Strip(picName, ReadJSON(config, 'name_exclude_char'))
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

    picData = Fetch(picURL)
    fullPath = WriteFile(
        ConcatPath(ROOT, TidyPath(ReadJSON(config, 'picture_store_path'))),
        picName + ReadJSON(config, 'picture_postfix'), 'wb', picData)

    SetWallpaper(fullPath, ReadJSON(config, 'wallpaper_fill_type'))
