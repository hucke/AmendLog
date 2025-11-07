import os
import sys
import matplotlib.pyplot as plt
import os.path
from pathlib import Path
from os import path
import re
from lineContents import lineContents

begin_time = 0.0
end_time = 0.0

object_taa = []
object_isp = []

#########################################################################
def print_version(log) :
    i = log.find('DDK revision:')
    if i != -1 :
        return log[i:i+23] # 'DDK revision: x.x.x'
    return ""
#########################################################################
def check_end(log) :
    i = log.find('is_resource_cdump dump start')
    if i != -1 :
        return True
    else :
        return False
#########################################################################
def check_parameter(param : str) -> bool :
    if path.exists(param) and path.isfile(param) :
        return True
    return True

def extract_ascii_from_binary(file_path : str) -> list:
    with open(file_path, 'rb') as f:
        data = f.read()
    
    ascii_chars = [chr(b) for b in data if 0 <= b <= 127 ]
    ascii_text = ''.join(ascii_chars)
    return ascii_text.splitlines()

def parsing_log_lines(line : str) -> tuple:
    found = re.findall(r"\[([\d|\.|\s]*)\]\s\[(\d)\]\s(.*)", line)
    if len(found) == 0 or len(found[0]) < 3 :
        return False, "", "", ""
    else :
        return True, found[0][0], found[0][1], found[0][2]

#########################################################################
def main() :
    if len(sys.argv) != 2 :
        print("amend.py <kernel log file>")
        sys.exit()
    elif not check_parameter(sys.argv[1]) :
        print(sys.argv[1] + " is not found.")
        sys.exit()

    file_path = Path(sys.argv[1])

    ddk_version = ""
    log_db = []
    sfr_db = []

    in_log = extract_ascii_from_binary(file_path)
    for line_no, line in enumerate(in_log, 1) :

        if len(line) == 0 :
            continue

        ok, time, task, body = parsing_log_lines(line)
        if not ok :
            print(f"[W]irregular format {line_no} line")
            print(line)
            continue

        data = lineContents(time, task, body, line)

        if check_end(body) :
            print("[I]log end on {} lines".format(line_no))
            break

        # save
        if body.startswith('ISP_FimcItpChainV1P10P0::Dump') == True :
            sfr_db.append(body + '\n')
        elif body.startswith('Dump') == True:
            sfr_db.append(body[5:] + '\n')        # 'Dump'를 제거하고 저장.
        else:
            log_db.append(data)

        if len(ddk_version) == 0 :
            ddk_version = print_version(body)

    if len(log_db) > 0 :
        # Sorting by time
        log_db.sort(key = lambda x : x.time) # x는 lineContents 데이터
        print("--- log time: {} - {}".format(float(log_db[0].time), float(log_db[-1].time)))

    # Finding
    global object_taa
    global object_isp
    global begin_time
    global end_time

    state_taa = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    state_isp = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    if len(log_db) > 0 :
        begin_time = float(log_db[0].time)
        end_time = float(log_db[-1].time)
    else :
        begin_time = float(0)
        end_time = float(0)

    for i in range(1, 10) :
        object_taa.append([[0.0, 0.0]])
        object_isp.append([[0.0, 0.0]])
        state_taa.append(0)
        state_isp.append(0)
    # print(object_taa)

    for l in log_db :
        log = l.log
        time = l.time

        if log.find("DICO_Object_3aa") >= 0 :
            # print(log + ":" + l[2].strip('\n'))
            # print(log + ":" + l[2], end='')
            streamId = log[ log.find("[S")+2 ]
            sId = int(streamId)
            cnt = state_taa[sId]
            # print("S{} state({})".format(sId, cnt))
            if log.find("Create") >= 0 and log.find("[E]") >= 0 :
                object_taa[sId][cnt][0] = float(time)
                object_taa[sId][cnt][1] = end_time - float(time)

            if log.find("Destroy") >= 0 :
                if object_taa[sId][cnt][0] == 0.0 :
                    object_taa[sId][cnt][0] = begin_time
                object_taa[sId][cnt][1] = float(time) - object_taa[sId][cnt][0]
                object_taa[sId].append([0.0, 0.0])
                state_taa[sId] = cnt + 1

        if log.find("DICO_Object_Isp") >= 0 :
            # print(log + ":" + l[2].strip('\n'))
            # print(log + ":" + l[2], end='')
            streamId = log[ log.find("[S")+2 ]
            sId = int(streamId)
            cnt = state_isp[sId]
            if log.find("Create") >= 0 and log.find("[E]") >= 0 :
                object_isp[sId][cnt][0] = float(time)
                object_isp[sId][cnt][1] = end_time - float(time)

            if log.find("Destroy") >= 0 :
                if object_isp[sId][cnt][0] == 0.0 :
                    object_isp[sId][cnt][0] = begin_time
                object_isp[sId][cnt][1] = float(time) - object_isp[sId][cnt][0]
                object_isp[sId].append([0.0, 0.0])
                state_isp[sId] = cnt + 1

    out_path = file_path.parent / "ddk"
    out_filename = file_path.stem

    Path(out_path).mkdir(parents=True, exist_ok=True)

    file_ddk_log_path = out_path / Path(out_filename + "_ddk.log")
    file_summary_path = out_path / Path(out_filename + "_ddk.summary")
    file_sfr_path  = out_path / Path(out_filename + "_ddk.sfr")

    print("--- Parsing Kernel log file: " + str(file_path))
    print("--- Output DDK log file: " + str(file_ddk_log_path))
    print("--- Output DDK summary file: " + str(file_summary_path))
    print("--- Output DDK SFR file: " + str(file_sfr_path))

    with open(file_ddk_log_path, 'w') as f :
        f.writelines( [ l.src + '\n' for l in log_db ] )

    if (sfr_db is not None) and (len(sfr_db) > 0) :
        with open(file_sfr_path, 'w') as f :
            f.writelines(sfr_db)

    with open(file_summary_path, 'w') as f :
        f.write(ddk_version)


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
