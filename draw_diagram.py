import matplotlib.pyplot as plt

object_taa = []
object_isp = []
begin_time = 0.0
end_time = 0.0

def analyze_log(log_db : list) -> bool:
    if len(log_db) == 0 :
        return False

    # Finding
    global object_taa
    global object_isp
    global begin_time
    global end_time

    state_taa = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    state_isp = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    begin_time = float(log_db[0].time)
    end_time = float(log_db[-1].time)

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


def draw_gantt(out_filename) :

    global object_taa
    global object_isp
    global begin_time
    global end_time

    # Declaring a figure "gnt" 
    fig, gnt = plt.subplots() 

    # Setting Y-axis limits 
    gnt.set_ylim(0, 80) 

    # Setting X-axis limits 
    gnt.set_xlim(begin_time, end_time) 

    # Setting labels for x-axis and y-axis 
    gnt.set_xlabel('seconds') 
    gnt.set_ylabel('Objects') 

    # Setting ticks on y-axis 
    gnt.set_yticks([15, 25, 35, 45, 55, 65, 75, 85, 95, 105]) 
    # Labelling tickes of y-axis 
    gnt.set_yticklabels(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']) 

    # Setting graph attribute 
    gnt.grid(True) 

    # Declaring a bar in schedule 
    # Declaring multiple bars in at same level and same width 
    
    for i, obj in enumerate(object_taa) :
        if obj[0][0] != 0.0 :
            print("[{}] {}".format(i, obj))
            gnt.broken_barh(obj, (10 * i + 15, 3), facecolors ='tab:blue')

    for i, obj in enumerate(object_isp) :
        if obj[0][0] != 0.0 :
            print("[{}] {}".format(i, obj))
            gnt.broken_barh(obj, (10 * i + 12, 3), facecolors ='tab:orange')

    plt.savefig(out_filename)

