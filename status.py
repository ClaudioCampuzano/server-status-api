import requests
import argparse
import pytz

from datetime import datetime, timedelta

def sendApiGo(cc_name,dsStatus,faustStatus,timestamp):
    payload = {"Ds_status":dsStatus,"Faust_status": faustStatus,"Timestamp": timestamp}
    res = requests.put('http://107.20.91.241:2711/omia/alerts/%s' % cc_name, json=payload)
    if res.status_code == 200:
        print('Ok')
    else:
        print('Error %s'% res)
    print(res.text)

def getStatusDs(filename, analyticalType, thresholdMinutes):
    try:
        gatillo = False
        for line in reversed(list(open(filename))):
            if gatillo:
                Ds_process = line.rstrip()
                break
            if line.split(" ")[0].rstrip() == '**PERF:':
                gatillo = True
        if len(Ds_process.split(" ")) != 5:
            Ds_process=''
    except:
        Ds_process=''
        print('Problemas al abrir el archivo '+analyticalType+' Ds Log')

    if Ds_process:
        ecuadorTime =  datetime.strptime(datetime.now(pytz.timezone('America/Guayaquil')).strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")
        DsDate = datetime.strptime(Ds_process,"%a %b %d	%H:%M:%S %Y")
        if ecuadorTime-DsDate > timedelta(minutes = thresholdMinutes):
            return True
        else:
            return False
    else:
        return False

def getStatusFaust(filename, analyticalType, thresholdMinutes):
    try:
        for index, line in enumerate(reversed(list(open(filename)))):
            faust_process_SPLIT = line.rstrip().replace('[', '').replace(']','').split(' ')
            if len(faust_process_SPLIT) >= 3 and faust_process_SPLIT[3]=="WARNING":
                Faust_process = faust_process_SPLIT[0]+' '+faust_process_SPLIT[1].split(",")[0]
                break
    except:
        Faust_process = ''
        print('Problemas al abrir el archivo '+analyticalType+' Faust Log')
    if Faust_process:
        ecuadorTime =  datetime.strptime(datetime.now(pytz.timezone('America/Guayaquil')).strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")
        faustDate = datetime.strptime(Faust_process,"%Y-%m-%d %H:%M:%S")

        if ecuadorTime-faustDate > timedelta(minutes = thresholdMinutes):
            return True
        else:
            return False
    else:
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Program that reports metrics from the computer to Slack')
    parser.add_argument('-t', '--thresholdMinutes', type=int, default=10, help='threshold minutes required to raise an alarm')
    parser.add_argument('-n', '--mallName', type=str, required=True, help='name of the mall to report')
    parser.add_argument('-a', '--logFlujoFaust', type=str, required=True, help='Absolute address of the flujo Faust log')
    parser.add_argument('-b', '--logFlujoDs', type=str, required=True, help='Absolute address of the flujo Ds log')
    parser.add_argument('-c', '--logAforoFaust', type=str, required=True, help='Absolute address of the Aforo Faust log')
    parser.add_argument('-d', '--logAforoDs', type=str, required=True, help='Absolute address of the Aforo Ds log')

    args = parser.parse_args()

    flujoFaust = getStatusFaust(args.logFlujoFaust,'#--Flujo--#',args.thresholdMinutes)
    aforoFaust = getStatusFaust(args.logAforoFaust,'#--Aforo--#',args.thresholdMinutes)
    flujoDs = getStatusDs(args.logFlujoDs,'#--Flujo--#',args.thresholdMinutes)
    aforoDs = getStatusDs(args.logAforoDs,'#--Aforo--#',args.thresholdMinutes)

    faustStatus = '0'
    dsStatus = '0'

    if flujoFaust or aforoFaust:
        faustStatus = '1'
    if flujoDs or aforoDs:
        dsStatus = '1'

    chile_now = datetime.now(pytz.timezone('America/Santiago')).replace(microsecond = 0).strftime("%Y-%m-%d %H:%M:%S")
    sendApiGo(args.mallName,dsStatus,faustStatus,chile_now)
