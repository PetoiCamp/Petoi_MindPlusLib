enum DIRECTION {
    //% block="+"
    "1",
    //% block="-"
    "-1",
}

enum NOTE {
    //% block="C1"
    10,
    //% block="D1"
    12,
    //% block="E1"
    14,
    //% block="F1"
    15,
    //% block="G1"
    17,
    //% block="A1"
    19,
    //% block="B1"
    21,
    //% block="C2"
    22,
    //% block="D2"
    24,
    //% block="E2"
    26,
    //% block="F2"
    27,
    //% block="G2"
    29,
    //% block="A2"
    31,
    //% block="B2"
    33
}

//% color="#1e90ff" iconWidth=50 iconHeight=40
namespace robot{
/*    
    //% block="import libraries" blockType="command"
    export function importLibraries(parameter: any, block: any) {
        Generator.addImport(`import binascii`);
        Generator.addImport(`import serial`);
		Generator.addImport(`import time`);
        Generator.addImport(`from PetoiRobot import *`);
    }
*/


    //% block="Auto open serial port" blockType="command"
    export function autoConnect(parameter: any, block: any) {
/*        
        let port=parameter.PORT.code;

        Generator.addImport(`import binascii`);
        Generator.addImport(`import serial`);

		Generator.addImport(`import time`);
        Generator.addImport(`from SerialCommunication import *`);
*/
        Generator.addImport(`from PetoiRobot import *`);

		Generator.addCode(`autoConnect()`);
    }


    //% block="Open serial port [PORT]" blockType="command"
    //% PORT.shadow="string" PORT.defl="COM3"
    export function openSerialPort(parameter: any, block: any) {
        let port=parameter.PORT.code;
/*
        Generator.addImport(`import binascii`);
        Generator.addImport(`import serial`);

		Generator.addImport(`import time`);
        Generator.addImport(`from SerialCommunication import *`);
*/
        Generator.addImport(`from PetoiRobot import *`);

		Generator.addCode(`openPort(${port})`);
    }


    //% block="Deactivate Gyro" blockType="command"
    export function deacGyro(parameter: any, block: any) {
    
        Generator.addCode(`deacGyro()`);
        
    }
	
	
	//% block="Perform skill [SKILL] and delay [TIME] seconds" blockType="command"
    //% SKILL.shadow="dropdown"  SKILL.options="SKILL"
    //% TIME.shadow="number" TIME.defl=0.2
    export function executeSkill(parameter: any, block: any) {
        var skill=parameter.SKILL.code;
        var t=parameter.TIME.code;

        Generator.addCode(`sendSkillStr('${skill}', ${t})`); 
    }

    //% block="Perform robot arm skill [ARMSKILL] and delay [TIME] seconds" blockType="command"
    //% ARMSKILL.shadow="dropdown"  ARMSKILL.options="ARMSKILL"
    //% TIME.shadow="number" TIME.defl=0.2
    export function executeArmSkill(parameter: any, block: any) {
        var skill=parameter.ARMSKILL.code;
        var t=parameter.TIME.code;

        Generator.addCode(`sendSkillStr('${skill}', ${t})`); 
    }


    //% block="Perform the last skill exported from Skill Composer and delay [TIME] seconds" blockType="command"
    //% TIME.shadow="number" TIME.defl=0.2
    export function callLastSkill(parameter: any, block: any) {
        var t=parameter.TIME.code;

        Generator.addCode(`sendCmdStr('T', ${t})`);
    } 
	

    //% block="Perform the skill in the file [FILENAME] and delay [TIME] seconds" blockType="command"
    //% FILENAME.shadow="string" FILENAME.defl="skillFileName"
    //% TIME.shadow="number" TIME.defl=0.2
    export function callExpSkill(parameter: any, block: any) {
        let fileName=parameter.FILENAME.code;
        var t=parameter.TIME.code;

        Generator.addCode(`# This block calls the skill stored in:`)
        Generator.addCode(`# Windows: C:\\Users\\{your user name}\\.config\\Petoi\\SkillLibrary\\{model}`)
        Generator.addCode(`# MacOS: /Users/{your user name}/.config/Petoi/SkillLibrary/{model}`)
        Generator.addCode(`# Linux: /home/{your user name}/.config/Petoi/SkillLibrary/{model}`)
        Generator.addCode(`# The model is Bittle or Nybble`)
        Generator.addCode(`# Please enter the skill filename in the block`)
        Generator.addCode(`loadSkill(${fileName}, ${t})`);
    } 
    

    //% block="Turn sequentially [LIST] and delay [TIME] seconds" blockType="command"
    //% LIST.shadow="normal"
    //% TIME.shadow="number" TIME.defl=0.2
	export function executeSeq(parameter: any, block: any) {
        var iaList=parameter.LIST.code;
        var t=parameter.TIME.code;

        Generator.addCode(`# The list format is [joint index, angle, joint index, angle...]`)
        Generator.addCode(`rotateJoints('M', ${iaList}, ${t})`);
	}
	
	//% block="Turn simultaneously [LIST] and delay [TIME] seconds" blockType="command"
    //% LIST.shadow="normal"
    //% TIME.shadow="number" TIME.defl=0.2
	export function executeSim(parameter: any, block: any) {
        var iaList=parameter.LIST.code;
        var t=parameter.TIME.code;

        Generator.addCode(`# The list format is [joint index, angle, joint index, angle...]`)
        Generator.addCode(`rotateJoints('I', ${iaList}, ${t})`);
	}

	
	//% block="[INDEX] to [ANGLE] degree" blockType="reporter"
	//% INDEX.shadow="dropdown"  INDEX.options="INDEX"
	//% ANGLE.shadow="range"  ANGLE.params.min=-125  ANGLE.params.max=125  ANGLE.defl=30
	export function jointAngle(parameter: any, block: any) {
        var index=parameter.INDEX.code;
        var angle=parameter.ANGLE.code;

		Generator.addCode(`absValList(${index}, ${angle})`);
	}


    //% block="[INDEX] [DIRECTION] [ANGLE] degree" blockType="reporter"
	//% INDEX.shadow="dropdown"  INDEX.options="INDEX"
    //% DIRECTION.shadow="dropdown"  DIRECTION.options="DIRECTION"  DIRECTION.defl="DIRECTION.+"
	//% ANGLE.shadow="range"  ANGLE.params.min=-125  ANGLE.params.max=125  ANGLE.defl=30
	export function jointRelativeAngle(parameter: any, block: any) {
        var index=parameter.INDEX.code;
        var symbol=parameter.DIRECTION.code;
        var angle=parameter.ANGLE.code;

		Generator.addCode(`relativeValList(${index}, ${symbol}, ${angle})`);
	}


    //% block="Get [INDEX] angle" blockType="reporter"
	//% INDEX.shadow="dropdown"  INDEX.options="INDEX"
	export function getJointAngle(parameter: any, block: any) {
        var index=parameter.INDEX.code;

		Generator.addCode(`getCurAng(${index})`);
	}
	

    //% block="Joint index and angle list [LIST]" blockType="reporter"
	//% LIST.shadow="list"  LIST.defl='8, 30, 9, 30, 10, 30, 11, 30'
	export function jointAngleList(parameter: any, block: any) {
        var listJointAngle=parameter.LIST.code;

		Generator.addCode(`${listJointAngle}`);
	}
	
	
    //% block="Transform to frame [LIST] and delay [TIME] seconds" blockType="command"
    //% LIST.shadow="normal"
    //% TIME.shadow="number" TIME.defl=0.2
	export function executeAllSim(parameter: any, block: any) {
        var iaList=parameter.LIST.code;
        var t=parameter.TIME.code;

        Generator.addCode(`# The length of list is 16. The list format is [angle, angle, angle...]`)
        Generator.addCode(`sendLongCmd('L', ${iaList}, ${t})`);
	}


    //% block="Action frame [ANGLE]" blockType="reporter"
	//% ANGLE.shadow="list"  ANGLE.defl='0, 0, 0, 0, 0, 0, 0, 0, 30, 30, 30, 30, 30, 30, 30, 30'
	export function angleList(parameter: any, block: any) {
        var angle=parameter.ANGLE.code;
        // return angle;
        Generator.addCode(`${angle}`)
	}


    //% block="Play melody [LIST] and delay [TIME] seconds" blockType="command"
    //% LIST.shadow="normal"
    //% TIME.shadow="number" TIME.defl=1
	export function playMelody(parameter: any, block: any) {
        var noteDurList=parameter.LIST.code;
        var t=parameter.TIME.code;

        Generator.addCode(`# The list format is [note, duration, note, duration...]`)
        Generator.addCode(`play('b', ${noteDurList}, ${t})`);
	}


    //% block="Tone [NOTE] Duration 1/[DUR]" blockType="reporter"
	//% NOTE.shadow="dropdown"  NOTE.options="NOTE"  NOTE.defl="NOTE.C1"
	//% DUR.shadow="range"  DUR.params.min=1  DUR.params.max=127  DUR.defl=2
	export function noteDur(parameter: any, block: any) {
        var note=parameter.NOTE.code;
        var dur=parameter.DUR.code;

		Generator.addCode(`absValList(${note}, ${dur})`);
	}


    //% block="Tone and duration list [LIST]" blockType="reporter"
	//% LIST.shadow="list"  LIST.defl='14,4,14,4,21,4,21,4,23,4,23,4,21,2'
	export function noteDurList(parameter: any, block: any) {
        var listNoteDur=parameter.LIST.code;

		Generator.addCode(`${listNoteDur}`);
	}


    //% block="Execute the command [CMD] and delay [TIME] seconds" blockType="command"
    //% CMD.shadow="string" CMD.defl="m0 -60 0 60 0 0"
    //% TIME.shadow="number" TIME.defl=0.2
    export function executeCmd(parameter: any, block: any) {
        let cmd=parameter.CMD.code;
        var t=parameter.TIME.code;

        Generator.addCode(`sendCmdStr(${cmd}, ${t})`);

    }


    //% block="Analog write [AVAL] to [AWPIN]" blockType="command"
	//% AWPIN.shadow="dropdown"  AWPIN.options="AWPIN"
    //% AVAL.shadow="range"  AVAL.params.min=0  AVAL.params.max=255  AVAL.defl=120
	export function writeAnalogValue(parameter: any, block: any) {
        var pin=parameter.AWPIN.code;
        var val=parameter.AVAL.code;

		if (pin == "16" || pin == "17")
        {
            Generator.addCode(`# Pleae dial the switch on the extension hat to Uart2.`)
            Generator.addCode(`writeAnalogValue(${pin}, ${val})`);
        }
        else
        {
            Generator.addCode(`writeAnalogValue(${pin}, ${val})`);
        }
	}


    //% block="Analog read [ARPIN]" blockType="reporter"
	//% ARPIN.shadow="dropdown"  ARPIN.options="ARPIN"
	export function readAnalogValue(parameter: any, block: any) {
        var pin=parameter.ARPIN.code;

		Generator.addCode(`readAnalogValue(${pin})`);
	}


    //% block="Digital write [DVAL] to [DWPIN]" blockType="command"
	//% DWPIN.shadow="dropdown"  DWPIN.options="DWPIN"
    //% DVAL.shadow="dropdown"  DVAL.options="DVAL"
	export function writeDigitalValue(parameter: any, block: any) {
        var pin=parameter.DWPIN.code;
        var val=parameter.DVAL.code;

		if (pin == "16." || pin == "17.")
        {
            Generator.addCode(`# Pleae dial the switch on the extension hat to Uart2.`)
            Generator.addCode(`writeDigitalValue(${pin}, ${val})`);
        }
        else
        {
            Generator.addCode(`writeDigitalValue(${pin}, ${val})`);
        }
	}


    //% block="Digital read [DRPIN]" blockType="reporter"
	//% DRPIN.shadow="dropdown"  DRPIN.options="DRPIN"  DRPIN.defl="DRPIN.6"
	export function readDigitalValue(parameter: any, block: any) {
        var pin=parameter.DRPIN.code;
        if (pin == "16." || pin == "17.")
        {
            Generator.addCode(`# Pleae dial the switch on the extension hat to Uart2.`)
            Generator.addCode(`readDigitalValue(${pin})`);
        }
        else
        {
            Generator.addCode(`readDigitalValue(${pin})`);
        }
	}


    //% block="Ultrasonic sensor distance(cm): Trigger [TRPIN] Echo [ECPIN]" blockType="reporter"
    //% TRPIN.shadow="dropdown"  TRPIN.options="TRPIN"  TRPIN.defl="TRPIN.6"
    //% ECPIN.shadow="dropdown"  ECPIN.options="ECPIN"  ECPIN.defl="ECPIN.-1"
    export function readUltrasonicDistance(parameter: any, block: any) {
        var trigPin = parameter.TRPIN.code;
        var echoPin = parameter.ECPIN.code;
              
        if (trigPin == "16" || trigPin == "17")
        {
            Generator.addCode(`# Pleae dial the switch on the extension hat to Uart2.`)
            Generator.addCode(`readUltrasonicDistance(${trigPin}, ${echoPin})`);
        }
        else
        {
            Generator.addCode(`readUltrasonicDistance(${trigPin}, ${echoPin})`);
        }
    }


    //% block="Coordinates of the identified target (x,y,width,height)" blockType="reporter"
    export function readCameraCoordinate(parameter: any, block: any) {
        Generator.addCode(`readCameraCoordinate()`);
    }

    //% block="Get gesture value" blockType="reporter"
    export function readGestureVal(parameter: any, block: any) {
        Generator.addCode(`# 0: Up; 1: Down; 2:Left; 3:Right`)
        Generator.addCode(`readGestureVal()`);
    }

    
    //% block="Close serial port and quit" blockType="command"
    export function closeSerialPort(parameter: any, block: any) {
    
        Generator.addCode(`closePort()`);
        
    }


/*
    function replaceQuotationMarks(str:string){
            str=str.replace(/"/g, ""); //去除所有引号
            return str
    }
*/   
}
