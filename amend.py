import sys
from pathlib import Path
from os import path
from lineContents import lineContents
from draw_diagram import analyze_log
from draw_diagram import draw_gantt

#########################################################################
def print_version(log) :
    i = log.find('DDK revision:')
    if i != -1 :
        return log[i:i+23] # 'DDK revision: x.x.x'
    return ""

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

def write_output_file(input_path : Path, log_db : list, sfr_db : list, ddk_version : str) :
    out_path = input_path.parent / "ddk"
    out_filename = input_path.stem

    Path(out_path).mkdir(parents=True, exist_ok=True)

    file_ddk_log_path = out_path / Path(out_filename + "_ddk.log")
    file_summary_path = out_path / Path(out_filename + "_ddk.summary")
    file_sfr_path  = out_path / Path(out_filename + "_ddk.sfr")

    # print("--- Parsing Kernel log file: " + str(file_path))
    print("--- Output DDK log file: " + str(file_ddk_log_path))
    print("--- Output DDK summary file: " + str(file_summary_path))
    print("--- Output DDK SFR file: " + str(file_sfr_path))

    with open(file_ddk_log_path, 'w') as f :
        f.writelines( [ l.src + '\n' for l in log_db ] )

    if len(sfr_db) > 0 :
        with open(file_sfr_path, 'w') as f :
            f.writelines('\n'.join(sfr_db))

    with open(file_summary_path, 'w') as f :
        f.write(ddk_version)

#########################################################################
def main() :
    if len(sys.argv) != 2 :
        print("amend.py <kernel log file>")
        sys.exit()

    file_path = Path(sys.argv[1])
    if not file_path.exists() :
        print(sys.argv[1] + " is not found.")
        sys.exit()

    ddk_version = ""
    log_db = []
    sfr_db = []

    print("--- Parsing Kernel log file: " + str(file_path))
    in_log = extract_ascii_from_binary(file_path)
    for line_no, line in enumerate(in_log, 1) :

        line = line.rstrip().rstrip()
        if len(line) == 0 :
            continue
        
        data = lineContents(line)
        if not data.isValid() :
            continue
        if data.isRegDump() :
            sfr_db.append(data.log)
            continue

        # save
        log_db.append(data)

        if len(ddk_version) == 0 :
            ddk_version = print_version(data.log)

    if len(log_db) == 0 :
        return

    # Sorting by time
    log_db.sort(key = lambda x : x.time) # x는 lineContents 데이터
    print(f"--- log time: {log_db[0].time}s - {log_db[-1].time}s")

    write_output_file(file_path, log_db, sfr_db, ddk_version)


    analyze_log(log_db)

    out_path = file_path.parent / "ddk" / (file_path.stem + ".png")
    draw_gantt(out_path)

#########################################################################


if __name__ == "__main__":
    main()
