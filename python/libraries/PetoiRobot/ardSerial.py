#!/usr/bin/python3
# -*- coding: utf-8 -*-

import struct
import sys
import time
import platform
import copy
import os 
import glob
import re

# Handle both relative imports (when used as a module) and absolute imports (when run directly)
# Try relative imports first (when used as a module), fall back to absolute imports (when run directly)
try:
    from .commonVar import *
    from .SerialCommunication import *  # module SerialCommunication.py
except (ImportError, ValueError):
    # When running directly as a script or relative import fails, use absolute imports
    from commonVar import *
    from SerialCommunication import *  # module SerialCommunication.py


def printH(head, value):
    print(head, end=' ')
    print(value)


if config.SHOW_GUI:
    import tkinter as tk
    import tkinter.messagebox
    # sys.path.append("../pyUI")
    sys.path.append("..")
    from translate import *
    language = languageList['English']

    def txt(key):
        return language.get(key, textEN[key])

ardSerialDate = "Dec. 16, 2025"
logger.info(f"ardSerial date: {ardSerialDate}")

def encode(in_str, encoding='utf-8'):
    if isinstance(in_str, bytes):
        return in_str
    else:
        return in_str.encode(encoding)

delayBetweenSlice = 0.001

def serialWriteNumToByte(port, token, var=None):  # Only to be used for c m u b I K L o within Python
    # print("Num Token "); print(token);print(" var ");print(var);print("\n\n");
    logger.debug(f'serialWriteNumToByte, token={token}, var={var}')
    in_str = ""
    if var is None:
        var = []
    if token == 'K':
        period = var[0]
        #        print(encode(in_str))
        if period > 0:
            skillHeader = 4
        else:
            skillHeader = 7
            
        # Determine frame size based on robot model
        if hasattr(config, 'model_') and config.model_ and 'Chero' in config.model_:
            maxJoints = 6
        else:
            maxJoints = 16
            
        if period > 1:
            frameSize = 8  # gait
        elif period == 1:
            frameSize = maxJoints  # posture
        else:
            frameSize = 20  # behavior
    # divide large angles by 2
        angleRatio = 1
        for row in range(abs(period)):
            for angle in var[skillHeader + row * frameSize:skillHeader + row * frameSize + min(maxJoints,frameSize)]:
                if angle > 125 or angle < -125:
                    angleRatio = 2
                    break
            if angleRatio ==2:
                break
        
        if angleRatio == 2:
            var[3] = 2
            for row in range(abs(period)):
                for i in range(skillHeader + row * frameSize,skillHeader + row * frameSize + min(maxJoints,frameSize)):
                    var[i] //=2
            printH('rescaled:\n',var)
            
        var = list(map(int, var))
        in_str = token.encode() + struct.pack('b' * len(var), *var) + '~'.encode()

    else:
        if token.isupper():# == 'L' or token == 'I' or token == 'B' or token == 'C':
#            if token == 'C':
#                packType = 'B'
#            else:
#                packType = 'b'
#            port.Send_data(token.encode())
            if len(var)>0:
                message = list(map(int, var))
                if token == 'B':
                    for l in range(len(message)//2):
                        message[l*2+1]*= 8  #change 1 to 8 to save time for tests
                        # print(message[l*2],end=",")
                        # print(message[l*2+1],end=",")
                        logger.debug(f"{message[l*2]},{message[l*2+1]}")
            if token == 'W' or token == 'C':
                in_str = struct.pack('B' * len(message), *message)    # B - unsigned char, e.g. 'B'*3 means 'BBB'
            else:
                in_str = struct.pack('b' * len(message), *message)    # b - signed char, e.g. 'b'*3 means 'bbb'
            in_str = token.encode() + in_str + '~'.encode()

        else:#if token == 'c' or token == 'm' or token == 'i' or token == 'b' or token == 'u' or token == 't':
            message = ""
            for element in var:
                message +=  (str(round(element))+" ")
            in_str = token.encode()+encode(message) +'\n'.encode()

    # 添加超时机制，防止在错误的串口上阻塞
    try:
        # 设置写超时为 2 秒
        if port.main_engine:
            original_write_timeout = port.main_engine.write_timeout
            port.main_engine.write_timeout = 2  # 2秒写超时
        
        slice = 0
        while len(in_str) > slice:
            if len(in_str) - slice >= 20:
                port.Send_data(in_str[slice:slice+20])
            else:
                port.Send_data(in_str[slice:])
            slice+=20
            time.sleep(delayBetweenSlice)
        
        # 恢复原始写超时设置
        if port.main_engine:
            port.main_engine.write_timeout = original_write_timeout
            
    except serial.SerialTimeoutException:
        logger.error("Serial write timeout! Port may be invalid or disconnected.")
        if port.main_engine:
            port.main_engine.write_timeout = original_write_timeout
        raise Exception("Serial write timeout")
    except Exception as e:
        logger.error(f"Error writing to serial port: {e}")
        if port.main_engine:
            port.main_engine.write_timeout = original_write_timeout
        raise
    
    logger.debug(f"!!!! {in_str}")
    # print(encode(in_str))
    # port.Send_data(encode(message))


def serialWriteByte(port, var=None):
    logger.debug(f'serial_write_byte, var={var}')
    if var is None:
        var = []
    token = var[0][0]
    # printH("token:",token)
    # print var
    if (token == 'c' or token == 'm' or token == 'i' or token == 'b' or token == 'u' or token == 't') and len(var) >= 2:
        in_str = ""
        for element in var:
            in_str = in_str + element + " "
        in_str += '\n'
    elif token == 'L' or token == 'I':
        if len(var[0]) > 1:
            var.insert(1, var[0][1:])
        var[1:] = list(map(int, var[1:]))
        in_str = token.encode() + struct.pack('b' * (len(var) - 1), *var[1:]) + '~'.encode()
    elif token == 'w' or token == 'k' or token == 'X' or token == 'g':
        in_str = var[0] + '\n'
    else:
        in_str = token + '\n'
    logger.debug(f"!!!!!!! {in_str}")
    # printH("in_str:", in_str)
    
    # 添加超时机制，防止在错误的串口上阻塞
    try:
        # 设置写超时为 2 秒
        if port.main_engine:
            original_write_timeout = port.main_engine.write_timeout
            port.main_engine.write_timeout = 2  # 2秒写超时
            port.Send_data(encode(in_str))
            port.main_engine.write_timeout = original_write_timeout
        else:
            port.Send_data(encode(in_str))
    except serial.SerialTimeoutException:
        logger.error("Serial write timeout! Port may be invalid or disconnected.")
        raise Exception("Serial write timeout")
    except Exception as e:
        logger.error(f"Error writing to serial port: {e}")
        raise
    
    time.sleep(0.01)


def printSerialMessage(port, token, timeout=0):
    if 'X' in token:
        token = 'X'

    if token == 'k' or token == 'K' or token == 'X':
        threshold = 8
    else:
        threshold = 3
    startTime = time.time()
    allPrints = ''
    while True:
        time.sleep(0.001)
        if port:
            response = port.main_engine.readline().decode('ISO-8859-1')
            if response != '':
                logger.debug(f"response is: {response}")
                responseTrim = response.split('\r')[0]
                logger.debug(f"responseTrim is: {responseTrim}")
                if responseTrim.lower() == token.lower(): 
                    return [response, allPrints]
                elif token == 'p' and responseTrim == 'k':
                    return [response, allPrints]
                else:
                    # print(response, flush=True)
                    allPrints += response
        now = time.time()
        timePassed = now - startTime
        logger.debug(f"time passed is: {timePassed}")
        if timePassed > threshold:
            # print('Elapsed time: ', end='')
            # print(threshold, end=' seconds\n', flush=True)
            logger.debug(f"Elapsed time: {threshold} seconds")
            threshold += 2
            if threshold > 5:
                return -1
        if 0 < timeout < now - startTime:
            return -1


def sendTask(PortList, port, task, timeout=0):  # task Structure is [token, var=[], time]
    logger.debug(f"{task}")
    # printH("task:",task)
    global returnValue
    #    global sync
    #    print(task)
    if port:
        try:
            previousBuffer = port.main_engine.read_all().decode('ISO-8859-1')
            if previousBuffer:
                logger.debug(f"Previous buffer: {previousBuffer}")
                pass
            if len(task) == 2:
                # print('a')
                # print(task[0])
                # printH("port is:", port)
                serialWriteByte(port, [task[0]])
            elif isinstance(task[1][0], int):
                # print('b')
                serialWriteNumToByte(port, task[0], task[1])
            else:
                # print('c') #which case
                serialWriteByte(port, task[1])
            token = task[0][0]
            # printH("token is:",token)
            if token == 'I' or token =='L':
                timeout = 1 # in case the UI gets stuck
            lastMessage = printSerialMessage(port, token, timeout)
            time.sleep(task[-1])
        #    with lock:
        #        sync += 1
        #        printH('sync',sync)
        #    if initialized:
        #        printH('thread',portDictionary[port])
        except Exception as e:
            # printH('Fail to send to port',PortList[port])
            if port in PortList:
                PortList.pop(port)
            lastMessage = -1
    else:
        lastMessage = -1
    returnValue = lastMessage
    return lastMessage


def sendTaskParallel(ports, task, timeout=0):
    global returnValue
    #    global sync
    #    sync = 0
    threads = list()
    for p in ports:
        t = threading.Thread(target=sendTask, args=(goodPorts, p, task, timeout))
        threads.append(t)
        t.daemon = True
        t.start()
    for t in threads:
        if t.is_alive():
            t.join()
    return returnValue


def splitTaskForLargeAngles(task):
    token = task[0]
    queue = list()
    if len(task)>2 and (token == 'L' or token == 'I'):
        var = task[1]
        indexedList = list()
        if token == 'L':
            # Determine grid size based on robot model
            if hasattr(config, 'model_') and config.model_ and 'Chero' in config.model_:
                gridSize = 2  # 2x3 grid for Chero
                maxJoints = 6
            else:
                gridSize = 4  # 4x4 grid for other robots
                maxJoints = 16
                
            for i in range(gridSize):
                for j in range(gridSize):
                    angle = var[gridSize * j + i]
                    if angle < -125 or angle > 125:
                        indexedList += [gridSize * j + i, angle]
                        var[gridSize * j + i] = max(min(angle, 125), -125)
            if len(var):
                queue.append(['L', var, task[-1]])
            if len(indexedList):
                queue[0][-1] = 0.01
                queue.append(['i', indexedList, task[-1]])
        #                print(queue)
        elif token == 'I':
            if min(var) < -125 or max(var) > 125:
                task[0] = 'i'
            queue.append(task)
    else:
        queue.append(task)
    return queue


def send(port, task, timeout=0):
#    printH('*** @@@ open port ',port) #debug
    if isinstance(port, dict):
        # print("port is dict.")
        p = list(port.keys())
    elif isinstance(port, list):
        # print("port is list.")
        p = port
    queue = splitTaskForLargeAngles(task)
    for task in queue:
        # printH("task",task)
        if len(port) > 1:
            returnResult = sendTaskParallel(p, task, timeout)
        elif len(port) == 1:
            # print("port len is 1.")
            returnResult = sendTask(goodPorts, p[0], task, timeout)
        else:
            # print('no ports')
            return -1
    return returnResult


def keepReadingInput(ports):
    while True and len(ports):
        time.sleep(0.001)
        x = input()  # blocked waiting for the user's input
        if x != "":
            if x == "q" or x == "quit":
                break
            else:
                token = x[0]
                task = x[1:].split()  # white space
                if len(task) <= 1:
                    send(ports, [x, 1])
                else:
                    send(ports, [token, list(map(int, task)), 1])


def closeSerialBehavior(port):
    try:
        port.Close_Engine()
    except Exception as e:
        port.Close_Engine()
        raise e
    logger.info("close the serial port.")


def closeAllSerial(ports, clearPorts=True):
    if clearPorts is True:
        send(ports, ['d', 0], 1)

    for p in ports:
        t = threading.Thread(target=closeSerialBehavior, args=(p,))
        t.daemon = True
        t.start()
        t.join()

    if clearPorts is True:
        ports.clear()


balance = [
    1, 0, 0, 1,
    0, 0, 0, 0, 0, 0, 0, 0, 30, 30, 30, 30, 30, 30, 30, 30]
buttUp = [
    1, 0, 15, 1,
    20, 40, 0, 0, 5, 5, 3, 3, 90, 90, 45, 45, -60, -60, 5, 5]
calib = [
    1, 0, 0, 1,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
dropped = [
    1, 0, -75, 1,
    0, 30, 0, 0, -5, -5, 15, 15, -75, -75, 45, 45, 60, 60, -30, -30]
lifted = [
    1, 0, 75, 1,
    0, -20, 0, 0, 0, 0, 0, 0, 60, 60, 75, 75, 45, 45, 75, 75]
rest = [
    1, 0, 0, 1,
    -30, -80, -45, 0, -3, -3, 3, 3, 70, 70, 70, 70, -55, -55, -55, -55]
sit = [
    1, 0, -30, 1,
    0, 0, -45, 0, -5, -5, 20, 20, 45, 45, 105, 105, 45, 45, -45, -45]
stretch = [
    1, 0, 20, 1,
    0, 30, 0, 0, -5, -5, 0, 0, -75, -75, 30, 30, 60, 60, 0, 0]
zero = [
    1, 0, 0, 1,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

balanceNybble = [
    1, 0, 0, 1,
    0, 0, 0, 0, 0, 0, 0, 0, 30, 30, -30, -30, 30, 30, -30, -30, ]
buttUpNybble = [
    1, 0, 15, 1,
    20, 40, 0, 0, 5, 5, 3, 3, 90, 90, -45, -45, -60, -60, -5, -5, ]
droppedNybble = [
    1, 0, 75, 1,
    0, 30, 0, 0, -5, -5, 15, 15, -75, -75, -60, -60, 60, 60, 30, 30, ]
liftedNybble = [
    1, 0, -75, 1,
    0, -70, 0, 0, 0, 0, 0, 0, 55, 55, 20, 20, 45, 45, 0, 0, ]
restNybble = [
    1, 0, 0, 1,
    -30, -80, -45, 0, -3, -3, 3, 3, 60, 60, -60, -60, -45, -45, 45, 45, ]
sitNybble = [
    1, 0, -20, 1,
    10, -20, -60, 0, -5, -5, 20, 20, 30, 30, -90, -90, 60, 60, 45, 45, ]
strNybble = [
    1, 0, 15, 1,
    10, 70, -30, 0, -5, -5, 0, 0, -75, -75, -45, -45, 60, 60, -45, -45, ]
zeroNybble = [
    1, 0, 0, 1,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ]

# DoF6 posture data - independent arrays for fine-tuning
balanceDoF6 = [
    1, 0, 0, 1,
    0, 0, 0, 0, 0, 0]
buttUpDoF6 = [
    1, 0, 15, 1,
    0, 0, -70, -70, -20, -20]
restDoF6 = [
    1, 0, 0, 1,
    30, 0, 60, 60, -60, -60]
sitDoF6 = [
    1, 0, -20, 1,
    60, 50, 30, 30, -50, -50]
strDoF6 = [
    1, 0, 0, 1,
    10, 70, -75, -75, 75, 75]
zeroDoF6 = [
    1, 0, 0, 1,
    0, 0, 0, 0, 0, 0]

postureTableBittle = {
    "balance": balance,
    "buttUp": buttUp,
    # "dropped": dropped,
    # "lifted": lifted,
    # 'flat': flat,
    # 'table': table,
    "rest": rest,
    "sit": sit,
    "str": stretch,
    "zero": zero
}

postureTableBittleR = {
    "balance": balance,
    "buttUp": buttUp,
    # "dropped": dropped,
    # "lifted": lifted,
    # 'flat': flat,
    # 'table': table,
    "rest": rest,
    "sit": sit,
    "str": stretch,
    "zero": zero
}

postureTableNybble = {
    "balance": balanceNybble,
    "buttUp": buttUpNybble,
    # "dropped": droppedNybble,
    # "lifted": liftedNybble,
    # 'flat': flatNybble,
    # 'table': tableNybble,
    "rest": restNybble,
    "sit": sitNybble,
    "str": strNybble,
    "zero": zeroNybble
}
postureTableDoF16 = {
    "balance": balance,
    "buttUp": buttUp,
    # "dropped": dropped,
    # "lifted": lifted,
    # 'flat': flat,
    # 'table': table,
    "rest": rest,
    "sit": sit,
    "str": stretch,
    "zero": zero
}

# DoF6 posture data - independent arrays for fine-tuning
postureTableDoF6 = {
    "balance": balanceDoF6,
    "buttUp": buttUpDoF6,
    "rest": restDoF6,
    "sit": sitDoF6,
    "str": strDoF6,
    "zero": zeroDoF6
}

postureDict = {
    'Nybble': postureTableNybble,
    'Bittle': postureTableBittle,
    'BittleX+Arm': postureTableBittleR,
    'DoF16': postureTableDoF16,
    'Chero': postureTableDoF6
}

skillFullName = {
        'balance': 'balance',
        'buttUp': 'buttUp',
        'dropped': 'dropped',
        'lifted': 'lifted',
        'lnd': 'landing',
        'rest': 'rest',
        'sit': 'sit',
        'up': 'up',
        'str': 'stretch',
        'calib': 'calib',
        'zero': 'zero',
        'ang':'angry',
         'bf': 'backFlip',
         'bx': 'boxing',
         'ck': 'check',
         'cmh': 'comeHere',
         'dg': 'dig',
         'ff': 'frontFlip',
         'fiv': 'highFive',
         'gdb': 'goodboy',
         'hds': 'handStand',
         'hi': 'hi',
         'hg': 'hug',
         'hsk': 'handShake',
         'hu': 'handsUp',
         'jmp': 'jump',
         'chr': 'cheers',
         'kc': 'kick',
         'mw': 'moonWalk',
         'nd': 'nod',
         'pd': 'playDead',
         'pee': 'pee',
         'pu': 'pushUp',
         'pu1': 'pushUpSingleArm',
         'rc': 'recover',
         'rl': 'roll',
         'scrh': 'scratch',
         'snf': 'sniff',
         'tbl': 'table',
         'ts': 'testServo',
         'wh': 'waveHead',
         'zz': 'zz',
         }
             
model = 'Bittle'
postureTable = postureDict[model]


def schedulerToSkill(ports, testSchedule):
    compactSkillData = []
    newSkill = []
    outputStr = ""

    # Determine the correct posture table and number of joints based on model
    global postureTable
    if hasattr(config, 'model_') and config.model_:
        if 'Chero' in config.model_:
            currentPostureTable = postureDict['Chero']
            numJoints = 6
        elif 'Nybble' in config.model_:
            currentPostureTable = postureDict['Nybble']
            numJoints = 16
        elif 'DoF16' in config.model_:
            currentPostureTable = postureDict['DoF16']
            numJoints = 16
        else:  # Bittle or BittleX+Arm
            currentPostureTable = postureDict['Bittle']
            numJoints = 16
    else:
        currentPostureTable = postureTable
        numJoints = 16

    for task in testSchedule:  # execute the tasks in the testSchedule
        print(task)
        token = task[0][0]
        if token == 'k' and task[0][1:] in currentPostureTable:
            currentRow = currentPostureTable[task[0][1:]][-numJoints:]
            skillRow = copy.deepcopy(currentRow)
            compactSkillData.append(skillRow + [8, int(task[1] * 1000 / 500), 0, 0])
            newSkill = newSkill + skillRow + [8, int(task[1] * 1000 / 500), 0, 0]

        elif token == 'i' or token == 'I':
            currentRow = copy.deepcopy(skillRow)
            for e in range(0, len(task[1]), 2):
                #                    print(task[1][e],task[1][e+1])
                currentRow[task[1][e]] = task[1][e + 1]
            skillRow = copy.deepcopy(currentRow)
            compactSkillData.append(skillRow + [8, int(task[2] * 1000 / 500), 0, 0])
            newSkill = newSkill + skillRow + [8, int(task[2] * 1000 / 500), 0, 0]
        elif token == 'L':
            skillRow = copy.deepcopy(task[1][:numJoints])
            compactSkillData.append(skillRow + [8, int(task[2] * 1000 / 500), 0, 0])
            newSkill = newSkill + skillRow + [8, int(task[2] * 1000 / 500), 0, 0]

        elif token == 'm':
            currentRow = copy.deepcopy(skillRow)
            for e in range(0, len(task[1]), 2):
                currentRow[task[1][e]] = task[1][e + 1]
                skillRow = copy.deepcopy(currentRow)
                compactSkillData.append(skillRow + [8, int(task[2] * 1000 / 500), 0, 0])
                newSkill = newSkill + skillRow + [8, int(task[2] * 1000 / 500), 0, 0]
    if len(compactSkillData) > 0:
        print('{')
        print('{:>4},{:>4},{:>4},{:>4},'.format(*[-len(compactSkillData), 0, 0, 1]))
        print('{:>4},{:>4},{:>4},'.format(*[0, 0, 0]))
    else:
        return
    angleRatio = 1
    for row in compactSkillData:
        if min(row) < -125 or max(row) > 125:
            angleRatio = 2
        print(('{:>4},' * (numJoints + 4)).format(*row))
    print('};')
    newSkill = list(map(lambda x: x // angleRatio, newSkill))
    newSkill = [-len(compactSkillData), 0, 0, angleRatio, 0, 0, 0] + newSkill
    print(newSkill)
    #    sendTaskParallel(['K', newSkill, 1])
    send(ports, ['K', newSkill, 1])

def getModelAndVersion(result):
    if result != -1:
        parse = result[1].replace('\r','').split('\n')
        for l in range(len(parse)):
            if 'Nybble' in parse[l] or 'Bittle' in parse[l] or 'DoF16' in parse[l] or 'Chero' in parse[l]:
                config.model_ = parse[l]
                config.version_ = parse [l+1]
                config.modelList += [config.model_]
                print(config.model_)
                print(config.version_)
                updatePostureTable()
                return
    config.model_ = 'Bittle'
    config.version_ = 'Unknown'
    # printH("@aaa config.version_:", config.version_)
    
def updatePostureTable():
    global postureTable
    if hasattr(config, 'model_') and config.model_:
        if 'Chero' in config.model_:
            postureTable = postureDict['Chero']
        elif 'Nybble' in config.model_:
            postureTable = postureDict['Nybble']
        elif 'DoF16' in config.model_:
            postureTable = postureDict['DoF16']
        else:  # Bittle or BittleX+Arm
            postureTable = postureDict['Bittle']
    
def deleteDuplicatedUsbSerial(list):
    if platform.system() != "Windows":
        for item in list:
            if 'modem' in item: # prefer the USB modem device because it can restart the NyBoard
                serialNumber = item[item.index('modem')+5:]
                for name in list:
                    if serialNumber in name and 'modem' not in name:    # remove the "wch" device
                        list.remove(name)
            elif 'serial-' in item: # prefer the "serial-" device 
                serialNumber = item[item.index('serial-')+7:]
                for name in list:
                    if serialNumber in name and 'wch' in name:    # remove the "wch" device
                        list.remove(name)
            elif 'cu.SLAB_USBtoUART' in item:
                list.remove(item)
    return list
    
def testPort(PortList, serialObject, p):
    global goodPortCount
    #    global sync
    try:
        time.sleep(3)
        waitTime = 0
        result = serialObject.main_engine
        if result != None:
            result = result.read_all().decode('ISO-8859-1')
            if result != '':
                print('Waiting for the robot to boot up')
                t = 2
                logger.debug(f"time delay: {t}s.")
                time.sleep(t)
                
                waitTime = 3
            else:
                waitTime = 2
            result = sendTask(PortList, serialObject, ['?', 0], waitTime)
            if result != -1:
                logger.debug(f"Adding in testPort: {p}")
                PortList.update({serialObject: p})
                goodPortCount += 1
                getModelAndVersion(result)
            else:
                serialObject.Close_Engine()
                print('* Port ' + p + ' is not connected to a Petoi device!')
    #    sync +=1
    except Exception as e:
        print('* Port ' + p + ' cannot be opened!')
        raise e

def checkPortList(PortList, allPorts, needTesting=True):
    threads = list()
    global goodPortCount

    for p in reversed(allPorts):  # assuming the last one is the most possible port
        # if p == '/dev/ttyAMA0':
        #     continue
        serialObject = Communication(p, 115200, 1)
        if needTesting is True:
            t = threading.Thread(target=testPort,
                                 args=(PortList, serialObject, p.split('/')[-1]))    # remove '/dev/' in the port name
            threads.append(t)
            t.daemon = True
            t.start()
        else:
            logger.debug(f"Adding in checkPortList: {p}")
            PortList.update({serialObject: p.split('/')[-1]})    # remove '/dev/' in the port name
            goodPortCount += 1
            logger.info(f"Connected to serial port: {p}")
    if needTesting is True:
        for t in threads:
            if t.is_alive():
                # print("t is alive")
                t.join(timeout=8)


def keepCheckingPort(portList, cond1=None, check=True, updateFunc = lambda:None):
    # portList is a dictionary, the structure is {SerialPort Object(<class 'SerialCommunication.Communication'>): portName(string), ...}
    # allPorts is a string list which delete the duplicated port(Reserve the name of the serial port that contains the usbmodem)
    # portStrList is the serial port string list
    global portStrList
    allPorts = Communication.Print_Used_Com()
    logger.debug(f"allPorts is {allPorts}")
    if cond1 is None:
        cond1 = lambda: len(portList) > 0

    while cond1():
        time.sleep(0.5)
        currentPorts = Communication.Print_Used_Com()    # string list
        # logger.debug(f"currentPorts is {currentPorts}")
        
        if set(currentPorts) - set(allPorts):
            time.sleep(1) #usbmodem is slower in detection
            currentPorts = Communication.Print_Used_Com()
            newPort = deleteDuplicatedUsbSerial(list(set(currentPorts) - set(allPorts)))
            # newPort = list(set(currentPorts) - set(allPorts))
            if check:
                time.sleep(0.5)
                checkPortList(portList, newPort)
            else:
                for p in newPort:
                    logger.debug(f"Adding serial port: {p}")
                    portName = p.split('/')[-1]
                    portStrList.insert(0, portName)  # remove '/dev/' in the port name
                    # Note: Do NOT show messagebox here as this runs in a background thread
            updateFunc()
        elif set(allPorts) - set(currentPorts):
            time.sleep(1) #usbmodem is slower in detection
            currentPorts = Communication.Print_Used_Com()
            closedPort = list(set(allPorts) - set(currentPorts))
            if check:
                inv_dict = {v: k for k, v in portList.items()}
                for p in closedPort:
                    if inv_dict.get(p.split('/')[-1], -1) != -1:
                        logger.info(f"Removing {p.split('/')[-1]}")
                        portList.pop(inv_dict[p.split('/')[-1]])
            else:
                for p in reversed(closedPort):
                    portName = p.split('/')[-1]
                    if portName in portStrList:
                        logger.info(f"Removing serial port:{portName}")
                        portStrList.remove(portName)
            updateFunc()
        allPorts = copy.deepcopy(currentPorts)

def get_raspberry_pi_model():
    """Detects the Raspberry pi model."""
    try :
        with open('/proc/cpuinfo','r')as cpuinfo:
            for line in cpuinfo:
                if "Model" in line:
                    model_info = line.split(':')[1].strip()
                    if "Raspberry Pi 3" in model_info:
                        return "Raspberry Pi 3"
                    elif "Raspberry Pi 4" in model_info:
                        return "Raspberry pi 4"
                    elif "Raspberry Pi 5" in model_info:
                        return "Raspberry Pi 5"
                    else:
                        #if not 3,4,or 5,attempt to get revision code
                        with open('/proc/cpuinfo','r')as cpuinfo2:
                            for line2 in cpuinfo2:
                                if"Revision" in line2:
                                    revision_code =line2.split(':')[1].strip()
                                    #basic check for revision codes that indicate pi5
                                    if re.match(r'^d[0-3]8', revision_code):
                                        return "Raspberry Pi 5"
                                    else:
                                        return "Raspberry Pi(Unknown Model)"
        return "Not a Raspberry pi"
    except FileNotFoundError:
        return "Not a Raspberry Pi"

def showSerialPorts(allPorts):
    # currently an issue in pyserial where for newer raspiberry pi os
    # (Kernel version: 6.1, Debian version: 12 (bookworm)) or ubuntus (22.04)
    # it classifies the /dev/ttyS0 port as a platform port and therefore won't be queried
    # https://github.com/pyserial/pyserial/issues/489
    if os.name == 'posix' and sys.platform.lower()[:5] == 'linux':
        raspPiModelName = get_raspberry_pi_model()
        if raspPiModelName != "Raspberry Pi 5":
            extra_ports = glob.glob('/dev/ttyS*')
        else:
            extra_ports = glob.glob('/dev/ttyAMA*')

        for port in extra_ports:
            if port not in allPorts:
                allPorts.append(port)
        # printH("allPorts:", allPorts)

    if not config.SHOW_GUI:
        allPorts = deleteDuplicatedUsbSerial(allPorts)

    for index in range(len(allPorts)):
        logger.debug(f"port[{index}] is {allPorts[index]} ")
    logger.info(f"*** Available serial ports: ***")
    # print(*allPorts, sep = "\n")
    for index in range(len(allPorts)):
        logger.info(f"{allPorts[index]} ")

    if platform.system() != "Windows":
        for p in allPorts:
             if 'cu.usb' in p:
                print('\n* Manually connect to the following port if it fail to connect automatically\n')
                if not config.SHOW_GUI:
                    print(p.replace('/dev/',''),end='\n\n')
                else:
                    print(p, end='\n\n')
    return allPorts


# get the path of configuration file
def getConfigFilePath(configDir, separation):
    """获取配置文件的完整路径"""
    return configDir + separation + 'defaultConfig.txt'


# read all ports from configuration file line 9
def readAllPortsFromConfig():
    """
    从配置文件第9行读取上次运行时的系统串口列表
    格式: All ports: COM3, COM5
    返回: 串口名称列表（不含 /dev/ 前缀）
    """
    configPath = defaultConfPath    # 在commonVar.py中定义
    if not os.path.exists(configPath):
        return []
    
    try:
        with open(configPath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) >= 9:
                line9 = lines[8].strip()
                if line9.startswith('All ports: '):
                    # 去掉前缀 "All ports: "
                    portsStr = line9[len('All ports: '):]
                    if portsStr:
                        ports = [p.strip() for p in portsStr.split(',') if p.strip()]
                        return ports
    except Exception as e:
        print(f'* Error reading config file: {e}')
    
    return []


# read valid ports from configuration file line 10
def readValidPortsFromConfig():
    """
    从配置文件第10行读取上次运行时可以打开的串口列表
    格式: Valid ports: COM3, COM5
    返回: 串口名称列表（不含 /dev/ 前缀）
    """
    configPath = defaultConfPath    # 在commonVar.py中定义
    if not os.path.exists(configPath):
        return []
    
    try:
        with open(configPath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) >= 10:
                line10 = lines[9].strip()
                if line10.startswith('Valid ports: '):
                    # 去掉前缀 "Valid ports: "
                    portsStr = line10[len('Valid ports: '):]
                    if portsStr:
                        ports = [p.strip() for p in portsStr.split(',') if p.strip()]
                        return ports
    except Exception as e:
        print(f'* Error reading config file: {e}')
    
    return []


# save all ports and valid ports to configuration file
def savePortsToConfig(allPortsList, validPortsList):
    """
    将串口列表保存到配置文件第9行和第10行
    参数: 
        configDir - 配置目录路径，在commonVar.py中定义
        separation - 路径分隔符，在commonVar.py中定义
        allPortsList - 系统所有串口列表（不含 /dev/ 前缀）
        validPortsList - 可以打开的串口列表（不含 /dev/ 前缀）
    """
    # 确保配置目录存在
    if not os.path.exists(configDir):
        os.makedirs(configDir)

    configPath = defaultConfPath    # 在commonVar.py中定义
    
    # 读取现有内容
    lines = []
    if os.path.exists(configPath):
        try:
            with open(configPath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f'* Error reading config file: {e}')
    
    # 确保现有的每一行都以换行符结尾（修复文件格式问题）
    for i in range(len(lines)):
        if not lines[i].endswith('\n'):
            lines[i] += '\n'
    
    # 确保至少有10行
    while len(lines) < 10:
        lines.append('\n')
    
    # 更新第9行（索引为8）- 保存系统所有串口
    allPortsStr = 'All ports: ' + ', '.join(allPortsList)
    lines[8] = allPortsStr + '\n'
    
    # 更新第10行（索引为9）- 保存可以打开的串口
    validPortsStr = 'Valid ports: ' + ', '.join(validPortsList)
    lines[9] = validPortsStr + '\n'
    
    # 写回文件
    try:
        with open(configPath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        logger.debug(f'Saved to config - All ports: {allPortsStr}')
        logger.debug(f'Saved to config - Valid ports: {validPortsStr}')
    except Exception as e:
        print(f'* Error writing config file: {e}')


# smart connect serial ports with smart configuration
def smartConnectPorts():
    """
    智能自动连接串口，支持配置文件持久化
    按照优化的逻辑：只检查有效串口和新增串口，避免重复检查已知无效的串口
    
    参数:
        configDir - 配置目录路径
        separation - 路径分隔符
    
    返回:
        newValidPorts - 成功连接的串口名称列表
    """
    # 创建空列表
    CheckList = []
    newValidPorts = []
    
    # 获取当前系统中检测到的串口组成的列表
    allPortsRaw = Communication.Print_Used_Com()
    allPorts = showSerialPorts(allPortsRaw)

    # 检查系统是否有串口设备
    if len(allPorts) == 0:
        if not config.SHOW_GUI:
            print('No port found! Please make sure the serial port can be recognized by the computer first.')
            sys.exit(1)
    
    # 提取串口名称列表（不含 /dev/ 前缀）
    allPortNames = [port.split('/')[-1] for port in allPorts]
    
    # Remove duplicate ports from the same device (prefer wchusbserial over usbmodem)
    # Convert back to full paths for deleteDuplicatedUsbSerial, then extract names again
    allPortsFiltered = deleteDuplicatedUsbSerial(allPorts.copy())
    allPortNames = [port.split('/')[-1] for port in allPortsFiltered]
    
    # 读取配置文件
    # 第9行：上次运行时的系统串口列表
    previousPorts = readAllPortsFromConfig()
    logger.debug(f'Previous ports from config: {previousPorts}')
    
    # 第10行：上次运行时可以打开的串口列表
    validPorts = readValidPortsFromConfig()
    logger.debug(f'Valid ports from config: {validPorts}')
    
    # 计算差异：在 allPortNames 中但不在 previousPorts 中的元素（新增的串口）
    diffPorts = [port for port in allPortNames if port not in previousPorts]
    logger.debug(f'Diff ports (new ports): {diffPorts}')
    
    # 删除 validPorts 中不在当前系统串口列表 allPortNames 中的元素
    validPorts = [port for port in validPorts if port in allPortNames]
    logger.debug(f'Valid ports after filtering: {validPorts}')
    
    # 确定检查列表 CheckList
    if len(validPorts) == 0:
        # 如果没有有效串口，检查所有系统串口
        CheckList = allPortNames
        print('No valid ports found in config. Trying all available ports...')
    else:
        # 有有效串口，只检查有效串口和新增串口
        CheckList = validPorts + diffPorts
        print(f'Trying to connect to valid ports and new ports...')
    
    logger.debug(f'CheckList: {CheckList}')
    
    # 使用多线程方式对 CheckList 中每一个串口设备尝试打开
    threads = list()
    
    for portName in CheckList:
        # 构造完整的串口路径
        if platform.system() == "Windows":
            fullPort = portName
        else:
            fullPort = '/dev/' + portName
        
        try:
            print(f'Trying port: {portName}...')
            serialObject = Communication(fullPort, 115200, 1)
            # 创建线程来测试串口
            t = threading.Thread(target=testPort, args=(goodPorts, serialObject, portName))
            threads.append(t)
            t.daemon = True
            t.start()
        except Exception as e:
            print(f'* Port {portName} cannot be opened!')
            logger.debug(f'Error opening port {portName}: {e}')
    
    # 等待所有线程完成（最多等待 8 秒）
    for t in threads:
        if t.is_alive():
            t.join(timeout=8)
    
    # 从 goodPorts 中提取成功连接的串口名称
    for serialObj, portName in goodPorts.items():
        if portName in CheckList:
            newValidPorts.append(portName)
            print(f'Successfully connected to port: {portName}')
    
    # 检查是否有成功打开的串口
    if len(newValidPorts) == 0:
        print('No port found! Please make sure the serial port can be recognized by the computer first.')
        if not config.SHOW_GUI:
            sys.exit(1)
        else:
            print('Replug mode')
            replug(goodPorts)
            if goodPorts:
                # 从 goodPorts 中提取成功连接的串口名称
                for serialObj, portName in goodPorts.items():
                    if portName in CheckList:
                        newValidPorts.append(portName)
                        allPortNames.append(portName)
                        print(f'Successfully connected to port: {portName}')
    
    # 更新配置文件
    # 第9行：保存此次运行程序时的系统串口列表
    # 第10行：保存此次运行程序得到的可以打开的串口列表
    savePortsToConfig(allPortNames, newValidPorts)
    
    return newValidPorts

                
def connectPort(PortList, needTesting=True, needSendTask=True, needOpenPort=True):
    global initialized
    global goodPortCount
    allPorts = Communication.Print_Used_Com()
    showSerialPorts(allPorts)

    if len(allPorts) > 0:
        goodPortCount = 0
        if needOpenPort is True:
            checkPortList(PortList, allPorts, needTesting)
    initialized = True
    if needOpenPort is True:
        if len(PortList) == 0:
            print('No port found! Please make sure the serial port can be recognized by the computer first.')
            print('Replug mode')
            replug(PortList, needSendTask, needOpenPort)
        else:
            logger.info(f"Connect to serial port list:")
            for p in PortList:
                logger.debug(f"datatype of p : {type(p)}")
                logger.info(f"{PortList[p]}")
                portStrList.append(PortList[p])
    else:
        if len(allPorts) == 0 or len(allPorts) > 1:
            print('Replug mode')
            replug(PortList, needSendTask, needOpenPort)
        else:   # len(allPorts) == 1
            portName = allPorts[0].split('/')[-1]
            portStrList.insert(0, portName)    # remove '/dev/' in the port name

                                
def replug(PortList, needSendTask=True, needOpenPort=True):
    global timePassed
    print('Please disconnect and reconnect the device from the COMPUTER side')
    
    window = tk.Tk()
    window.geometry('+800+500')
    def on_closing():
        window.destroy()
        os._exit(0)
    window.protocol('WM_DELETE_WINDOW', on_closing)
    window.title(txt('Replug mode'))

    thres = 10 # time out for the manual plug and unplug
    print('Counting down to manual mode:')
    
    def bCallback():
        labelC.destroy()
        buttonC.destroy()
        
        labelT['text']= txt('Counting down to manual mode: ')
        labelT.grid(row=0,column=0)
        
        label.grid(row=1,column=0)
        label['text']="{} s".format(thres)
        countdown(time.time(),copy.deepcopy(Communication.Print_Used_Com()))
        
    labelC = tk.Label(window, font='sans 14 bold', justify='left')
    labelC['text'] = txt('Replug prompt')
    labelC.grid(row=0, column=0)
    buttonC = tk.Button(window, text=txt('Confirm'), command=bCallback)
    buttonC.grid(row=1, column=0, pady=10)
    labelT = tk.Label(window, font='sans 14 bold')
    label = tk.Label(window, font='sans 14 bold')
    def countdown(start,ap):
        global goodPortCount
        global timePassed
        curPorts = copy.deepcopy(Communication.Print_Used_Com())

        if len(curPorts) != len(ap):
            time.sleep(0.5)    # USB modem serial takes longer time to get ready
            curPorts = copy.deepcopy(Communication.Print_Used_Com())
            print(ap)
            print('---')
            print(curPorts)
            if len(curPorts) < len(ap):
                ap = curPorts
                start = time.time()
                timePassed = 0
            else:
                dif = list(set(curPorts)-set(ap))
                if needSendTask and needOpenPort:
                    # Remove duplicate ports from the same device (prefer wchusbserial over usbmodem)
                    dif = deleteDuplicatedUsbSerial(dif)
                printH("diff:", dif)

                success = False
                connected_serial_numbers = set()  # Track connected devices to avoid duplicates
                for p in dif:
                    try:
                        portName = p.split('/')[-1]
                        serialNumber = None

                        if needOpenPort is True:
                            # Extract serial number to check if this device is already connected
                            if 'wchusbserial' in portName:
                                serialNumber = portName[portName.index('wchusbserial') + len('wchusbserial'):]
                            elif 'usbmodem' in portName:
                                serialNumber = portName[portName.index('usbmodem') + len('usbmodem'):]
                            
                            # Skip if this device is already connected
                            if serialNumber and serialNumber in connected_serial_numbers:
                                logger.info(f"Skipping duplicate port {portName} (device {serialNumber} already connected)")
                                continue
                        
                            logger.info(f"Connected to serial port: {p}")
                            serialObject = Communication(p, 115200, 1)
                            PortList.update({serialObject: portName})
                            
                            # Mark this device as connected before sendTask to avoid blocking
                            if serialNumber:
                                connected_serial_numbers.add(serialNumber)
                            
                            # Perform sendTask to verify it's a Petoi device
                            if needSendTask is True:
                                # Use threading.Event to synchronize with background thread
                                device_info_event = threading.Event()
                                device_info_success = [False]  # Use list to allow modification in nested function
                                
                                def get_device_info():
                                    try:
                                        time.sleep(2)
                                        result = sendTask(PortList, serialObject, ['?', 0])
                                        # printH("@aaa result:", result)
                                        getModelAndVersion(result)
                                        # Check if device info was successfully retrieved
                                        if config.version_ != '' and config.version_ != 'Unknown':
                                            device_info_success[0] = True
                                    except Exception as e:
                                        logger.error(f"Error getting device info: {e}")
                                    finally:
                                        # Signal that device info check is complete
                                        device_info_event.set()
                                
                                # Run in background thread
                                info_thread = threading.Thread(target=get_device_info, daemon=True)
                                info_thread.start()
                                
                                # Wait for device info check to complete (with timeout)
                                # Use a reasonable timeout (e.g., 10 seconds) to avoid hanging forever
                                device_info_event.wait(timeout=10)
                                
                                # Check result after thread completes
                                if device_info_success[0]:
                                    # Device info check successful, add to lists
                                    portStrList.insert(0, portName)  # remove '/dev/' in the port name
                                    goodPortCount += 1
                                    tk.messagebox.showinfo(title=txt('Info'), message=txt('New port prompt') + portName)
                                    logger.info(f"Successfully connected to port: {portName}")
                                    success = True
                                else:
                                    # Device info check failed or timed out
                                    logger.warning(f"Device info check failed or timed out for port {portName}")
                                    # Close the port since it's not a Petoi device
                                    try:
                                        serialObject.Close_Engine()
                                        PortList.pop(serialObject, None)
                                    except:
                                        pass
                            else:
                                # No need to check device info, add to lists directly
                                portStrList.insert(0, portName)  # remove '/dev/' in the port name
                                goodPortCount += 1
                                tk.messagebox.showinfo(title=txt('Info'), message=txt('New port prompt') + portName)
                                logger.info(f"Successfully connected to port: {portName}")
                                success = True
                        else:
                            # needOpenPort is False, just add to portStrList
                            portStrList.insert(0, portName)  # remove '/dev/' in the port name
                            goodPortCount += 1
                            success = True
                    except Exception as e:
                        # Log error but continue trying other ports
                        logger.error(f"Cannot open {p}: {e}")
                        print("Cannot open {}".format(p))
                for p in ap:
                    # logger.debug(f"datatype of p : {type(p)}")
                    # logger.info(f"{PortList[p]}")
                    portStrList.append(p)

                if success:
                    # Quit mainloop first, then destroy window
                    # This ensures replug() function returns immediately
                    window.quit()
                    window.destroy()
                    return
                else:
                    labelT.destroy()
                    label.destroy()
                    manualSelect(PortList, window, needSendTask, needOpenPort)
                return

        if time.time() - start > thres:
            labelT.destroy()
            label.destroy()
            manualSelect(PortList, window, needSendTask, needOpenPort)
            return
        elif (time.time() - start) % 1 < 0.1:
            print(thres - round(time.time() - start) // 1)
            label['text'] = "{} s".format((thres - round(time.time() - start) // 1))
        window.after(100, lambda: countdown(start, ap))

    window.focus_force()  # new window gets focus
    window.mainloop()
    
def selectList(PortList,ls,win, portMap, needSendTask=True, needOpenPort=True):
    
    global goodPortCount, manuallySelectedPort
    success = False
    error_msg = None
    
    # Mark that port was manually selected by user
    manuallySelectedPort = True
    
    for i in ls.curselection():
        displayName = ls.get(i)
        p = portMap.get(displayName, displayName)
        try:
            print(p)
            print(p.split('/')[-1])
            if needOpenPort is True:
                serialObject = Communication(p, 115200, 1)
                PortList.update({serialObject: p.split('/')[-1]})
            portStrList.append(p.split('/')[-1])
            goodPortCount += 1
            logger.info(f"Connected to serial port: {p}")
            
            if (needOpenPort is True) and (needSendTask is True):
                time.sleep(2)
                result = sendTask(PortList, serialObject, ['?', 0])
                getModelAndVersion(result)
            success = True

        except Exception as e:
            error_msg = txt('* Port ') + p + txt(' cannot be opened')
            logger.error(f"Cannot open {p}: {e}")
            print("Cannot open {}".format(p))
    
    # Close window first, then show any error messages
    win.destroy()
    
    if error_msg and not success:
        tk.messagebox.showwarning(title=txt('Warning'), message=error_msg)

def manualSelect(PortList, window, needSendTask=True, needOpenPort=True):
    # allPorts = deleteDuplicatedUsbSerial(Communication.Print_Used_Com())
    allPorts = Communication.Print_Used_Com()
    
    # Clear previous widgets to avoid conflicts
    for widget in window.winfo_children():
        widget.destroy()
    
    window.title(txt('Manual mode'))
    # Make window reasonably sized and resizable
    try:
        window.geometry('720x420+700+400')
    except Exception:
        pass
    window.resizable(True, True)
    window.grid_columnconfigure(0, weight=1)
    window.grid_rowconfigure(2, weight=1)
    l1 = tk.Label(window, font = 'sans 14 bold')
    l1['text'] = txt('Manual mode')
    l1.grid(row=0,column = 0, sticky='w', padx=5, pady=5)
    l2 = tk.Label(window, font='sans 14 bold')
    l2["text"]=txt('Please select the port from the list')
    l2.grid(row=1,column=0, sticky='w', padx=5)
    ls = tk.Listbox(window, selectmode="browse")
    ls.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)

    # Map display names to full paths (hide parent directories)
    portMap = {}
    def populate_listbox(ports):
        ls.delete(0, tk.END)
        portMap.clear()
        nameCount = {}
        for p in ports:
            base = p.split('/')[-1]
            # Ensure uniqueness if duplicates
            disp = base
            if base in nameCount:
                nameCount[base] += 1
                disp = f"{base} ({nameCount[base]})"
            else:
                nameCount[base] = 1
            portMap[disp] = p
            ls.insert(tk.END, disp)

    populate_listbox(allPorts)

    def refreshBox(ls):
        # allPorts = deleteDuplicatedUsbSerial(Communication.Print_Used_Com())
        ports = Communication.Print_Used_Com()
        populate_listbox(ports)

    bu = tk.Button(window, text=txt('OK'), command=lambda:selectList(PortList, ls, window, portMap, needSendTask, needOpenPort))
    bu.grid(row=2, column=1, sticky='n', padx=5, pady=5)
    bu2 = tk.Button(window, text=txt('Refresh'), command=lambda:refreshBox(ls))
    bu2.grid(row=1, column=1, sticky='n', padx=5)
    
    # Show info message after window is ready, using after to avoid blocking
    window.after(100, lambda: tk.messagebox.showinfo(title=txt('Info'), message=txt('Manual mode')))
    
    # Note: Do NOT call mainloop() here as the parent window already has one running

def monitoringVoltage(ports, VoltagePin, timer, callback):
    while True and len(ports):
        time.sleep(timer)
        voltage = send(ports, ["R", [97, VoltagePin], 0])
        if callback is not None:
            callback(voltage)
        else:
            print("Current Voltage:" + str(voltage))

def monitoringDistance(ports, trigerPin, echoPin, timer, callback):
    while True and len(ports):
        time.sleep(timer)
        distance = send(ports, ["XU", [trigerPin, echoPin], 0])
        if callback is not None:
            callback(distance)
        else:
            print("Current Distance:" + str(distance))   

def monitoringJoint(ports, jointIndex, timer, callback):
    while True and len(ports):
        time.sleep(timer)
        if jointIndex == 0:
          angel = send(ports, ["j", jointIndex])
        else:
          angel = send(ports, ["j", [jointIndex], 0])
        if callback is not None:
            callback(angel)
        else:
            print("Current Angel:" + str(angel))
            
def read_MCU_loop(PortList, callback=None):
    result = send(PortList, ['gP', 0])
    print("send results " + str(result))
    p = list(PortList.keys())
    serialObject = p[0]
    while True:
        try:
            if PortList:
                data = serialObject.main_engine.readline()
                if data:
                    try:
                        decoded_data = data.decode('ISO-8859-1').strip()
                        if callback is not None:
                            callback(decoded_data)
                        else:
                            print(str(decoded_data))
                    except Exception as e:
                        logger.error(f"Error decoding serial port data: {e}")
            time.sleep(0.005)  # avoid high CPU usage
        except Exception as e:
            logger.error(f"Error reading serial port data: {e}")
            break

#if need to open serial port, use objects goodPorts
goodPorts = {}      # goodPorts is a dictionary, the structure is {SerialPort Object(<class 'SerialCommunication.Communication'>): portName(string), ...}

portStrList = []    # portStrList is the serial port string list
initialized = False
goodPortCount = 0
sync = 0

# Flag to track if port was manually selected by user
manuallySelectedPort = False
lock = threading.Lock()
returnValue = ''
timePassed = 0

'''
# Monitor callback usage sample
def voltageHanle(voltage):
    if  voltage <0.5:
        print("Low Power Warning")    # do something to handle low power
        
def distanceHanle(distance):
    if  distance <0.5:
        print("Small Distance Warning")    # do something to handle small distance
'''


if __name__ == '__main__':
    try:
        # connectPort(goodPorts)
        smartConnectPorts()
        t = threading.Thread(target=keepCheckingPort, args=(goodPorts,))
        t.daemon = True
        t.start()
        # t1=threading.Thread(target=read_MCU_loop, args=(goodPorts, None))
        # t1.daemon = True
        # t1.start()
        ### Monitor Threads
        # t_monitor_voltage = threading.Thread(target=monitoringVoltage, args=(goodPorts, 0xA7, 60, voltageHanle))
        # t_monitor_voltage.daemon = True
        # t_monitor_voltage.start()
        # t_monitor_distance = threading.Thread(target=monitoringDistance, args=(goodPorts, 16, 17, 0.5, distanceHanle))
        # t_monitor_distance.daemon = True
        # t_monitor_distance.start()
        # t_monitor_joint = threading.Thread(target=monitoringJoint, args=(goodPorts, 0 , 0.5, None))
        # t_monitor_joint.daemon = True
        # t_monitor_joint.start()

        if len(sys.argv) >= 2:
            if len(sys.argv) == 2:
                cmd = sys.argv[1]
                token = cmd[0][0]
            else:
                token = sys.argv[1][0]
            #                sendTaskParallel([sys.argv[1][0], sys.argv[1:], 1])
            send(goodPorts, [sys.argv[1][0], sys.argv[1:], 1])
        printH('Model list',config.modelList)
        print("You can type 'quit' or 'q' to exit.")

        keepReadingInput(goodPorts)

        closeAllSerial(goodPorts)
        logger.info("finish!")
        os._exit(0)

    except Exception as e:
        logger.info("Exception")
        closeAllSerial(goodPorts)
        raise e
