import re

class lineContents():
    def __init__(self, logline):
        self.src = logline
        self.valid, self.time, self.tid, self.log = self.parsing_log_lines(logline)

    def isValid(self) -> bool:
        return self.valid
    
    def isRegDump(self) -> bool:
        if self.log.startswith('ISP_FimcItpChainV1P10P0::Dump') == True :
            return True
        elif self.log.startswith('Dump') == True:
            return True
        elif self.log.find('[DUMP]') != -1:
            return True
        else :
            return False

    def parsing_log_lines(self, line : str) -> tuple:
        found = re.findall(r"\[(\s*\d+\.\d*)\]\s\[(\d)\](.*)", line)
        if len(found) == 0 or len(found[0]) < 3 :
            return False, float(0), '', ''
        elif found[0][0].strip() == '' :
            return False, float(0), '', ''
        else :
            return True, float(found[0][0]), found[0][1], found[0][2].lstrip()

if __name__ == "__main__":
    s = '[10566.086659] [0][#] ### is_resource_cdump dump start ###'
    found = re.findall(r"\[(\s*\d+\.\d*)\]\s\[(\d)\](.*)", s)
    print(found)
