import os
import sys
import matplotlib.pyplot as plt
import os.path
from os import path
import re
from lineContents import lineContents

begin_time = 0.0
end_time = 0.0

object_taa = []
object_isp = []

#########################################################################
def print_version(file, log) :
    i = log.find('DDK revision:')
    if i != -1 :
        ver = log[i:i+23]
        file.write(ver)
        return ver
    return ""
#########################################################################
def check_end(log) :
    i = log.find('is_resource_cdump dump start')
    if i != -1 :
        return True
    else :
        return False
#########################################################################
def check_parameter(param) :
    
    if path.exists(param) == False:
        print(param + " is not exist")
        return False

    if path.isfile(param) :
        print("file: " + param)
    elif path.isdir(param) :
        print("folder: " + param)

    return True
#########################################################################
def main() :
    if len(sys.argv) != 2:
        print("amend.py <kernel log file>")
        sys.exit()

    input_file_path = sys.argv[1]
    if check_parameter(input_file_path) == False :
        sys.exit()

    path = input_file_path.rsplit('.', maxsplit=1)
    out_file_sfr  = path[0] + ".ddk.sfr"

    # print("File path : " + file_path)
    # print("File path : " + out_file_path)

    file_ddk_log_in = open(input_file_path, 'r')
    file_ddk_log_out = open(path[0] + ".ddk.log", 'w')
    file_ddk_sfr = open(out_file_sfr, 'w')
    file_summary = open(path[0] + ".ddk.summary", 'w')

    ddk_version = ""

    log_db = []

    # for line in file_ddk_log_in:
    line_no = 0
    lines = file_ddk_log_in.readlines()
    for line in lines :
        line_no = line_no + 1

        found = re.findall("\[([\d|\.|\s]*)\]\s\[(\d)\]\s(.*)", line)
        # print(found)

        if len(found[0]) < 3 :
            print(f"[W]irregular format {line_no} line")
            print(line)
            continue

        time = found[0][0]
        task = found[0][1]
        body = found[0][2]

        data = lineContents(time, task, line)

        if check_end(body) :
            print("[I]log end on {} lines".format(line_no))
            break

        # save
        if body.startswith('ISP_FimcItpChainV1P10P0::Dump') == True :
            file_ddk_sfr.write(body + '\n')
        elif body.startswith('Dump') == True:
            file_ddk_sfr.write(body[5:] + '\n')        # 'Dump'를 제거하고 저장.
        else:
            item = [time, task, body, data]
            log_db.append(item)

        if len(ddk_version) == 0 :
            ddk_version = print_version(file_summary, body)

    # Closing input file
    file_ddk_log_in.close()

    # Sorting by time
    log_db.sort(key = lambda x : x[3].time) # x[3]는 lineContents 데이터

    print("--- log time: {} - {}".format(log_db[0][0], log_db[len(log_db)-1][0]))

    # Finding
    global object_taa
    global object_isp
    global begin_time
    global end_time

    state_taa = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    state_isp = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    if log_db[0][0] != '' :
        begin_time = float(log_db[0][0])
    if log_db[-1][0] != '' :
        end_time = float(log_db[-1][0])

    for i in range(1, 10) :
        object_taa.append([[0.0, 0.0]])
        object_isp.append([[0.0, 0.0]])
        state_taa.append(0)
        state_isp.append(0)
    # print(object_taa)

    if len(log_db) == 0 :
        return

    for l in log_db :
        # file_ddk_log_out.write(l[0] + " " + l[1] + " " + l[2])
        file_ddk_log_out.write(l[3].log)

        if l[2].find("DICO_Object_3aa") >= 0 :
            # print(l[0] + ":" + l[2].strip('\n'))
            # print(l[0] + ":" + l[2], end='')
            streamId = l[2][ l[2].find("[S")+2 ]
            sId = int(streamId)
            cnt = state_taa[sId]
            # print("S{} state({})".format(sId, cnt))
            if l[2].find("Create") >= 0 and l[2].find("[E]") >= 0 :
                object_taa[sId][cnt][0] = float(l[0])
                object_taa[sId][cnt][1] = end_time - float(l[0])

            if l[2].find("Destroy") >= 0 :
                if object_taa[sId][cnt][0] == 0.0 :
                    object_taa[sId][cnt][0] = begin_time
                object_taa[sId][cnt][1] = float(l[0]) - object_taa[sId][cnt][0]
                object_taa[sId].append([0.0, 0.0])
                state_taa[sId] = cnt + 1

        if l[2].find("DICO_Object_Isp") >= 0 :
            # print(l[0] + ":" + l[2].strip('\n'))
            # print(l[0] + ":" + l[2], end='')
            streamId = l[2][ l[2].find("[S")+2 ]
            sId = int(streamId)
            cnt = state_isp[sId]
            if l[2].find("Create") >= 0 and l[2].find("[E]") >= 0 :
                object_isp[sId][cnt][0] = float(l[0])
                object_isp[sId][cnt][1] = end_time - float(l[0])

            if l[2].find("Destroy") >= 0 :
                if object_isp[sId][cnt][0] == 0.0 :
                    object_isp[sId][cnt][0] = begin_time
                object_isp[sId][cnt][1] = float(l[0]) - object_isp[sId][cnt][0]
                object_isp[sId].append([0.0, 0.0])
                state_isp[sId] = cnt + 1

    file_ddk_log_out.close()
    file_ddk_sfr.close()
    file_summary.close()

    # 파일 내용이 비어 있으면 지운다.
    if os.path.getsize(out_file_sfr) == 0:
        os.remove(out_file_sfr)

    # print(log_db)
    # print("3aa gantt input")
    # for info in object_taa :
    #     print(info)
    # print("isp gantt input")
    # for info in object_isp :
    #     print(info)

    # draw_gantt(begin_time, end_time, path[0] + ".png")

#########################################################################

def draw_gantt(start, end, out_filename) :

    global object_taa
    global object_isp

    # Declaring a figure "gnt" 
    fig, gnt = plt.subplots() 

    # Setting Y-axis limits 
    gnt.set_ylim(0, 80) 

    # Setting X-axis limits 
    gnt.set_xlim(start, end) 

    # Setting labels for x-axis and y-axis 
    gnt.set_xlabel('seconds since start') 
    gnt.set_ylabel('Objects') 

    # Setting ticks on y-axis 
    gnt.set_yticks([15, 25, 35, 45, 55, 65, 75, 85, 95, 105]) 
    # Labelling tickes of y-axis 
    gnt.set_yticklabels(['0', '1', '2', '3', '4', '5', '6', '7', '8']) 

    # Setting graph attribute 
    gnt.grid(True) 

    # Declaring a bar in schedule 
    # Declaring multiple bars in at same level and same width 
    
    for i in range(0, 9) :
        if object_taa[i][0][0] != 0.0 :
            print("[{}] {}".format(i, object_taa[i]))
            gnt.broken_barh(object_taa[i], (10 * i + 15, 3), facecolors ='tab:blue')

    for i in range(0, 9) :
        if object_isp[i][0][0] != 0.0 :
            print("[{}] {}".format(i, object_isp[i]))
            gnt.broken_barh(object_isp[i], (10 * i + 12, 3), facecolors ='tab:orange')

    plt.savefig(out_filename) 

if __name__ == "__main__":
    main()
