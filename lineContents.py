import re

def parsing_log_lines(line : str) -> tuple:
    found = re.findall(r"\[(\s+\d+\.\d*)\]\s\[(\d)\]\s(.*)", line)
    if len(found) == 0 or len(found[0]) < 3 :
        return False, float(0), '', ''
    elif found[0][0].strip() == '' :
        return False, float(0), '', ''
    else :
        return True, float(found[0][0]), found[0][1], found[0][2]

class lineContents():
    def __init__(self, time, tid, log, src):
        self.time = time
        self.tid = tid
        self.log = log
        self.src = src

    def __init__(self, logline):
        ok, time, task, body = parsing_log_lines(logline)
        if ok :
            self.time = time
            self.tid = task
            self.log = body
            self.src = logline
        else :
            self.time = float(0)
            self.tid = ""
            self.log = ""
            self.src = logline

    def isValid(self) -> bool:
        return self.log != ""
    
    def isRegDump(self) -> bool:
        if self.log.startswith('ISP_FimcItpChainV1P10P0::Dump') == True :
            return True
        elif self.log.startswith('Dump') == True:
            return True
        else :
            return False
