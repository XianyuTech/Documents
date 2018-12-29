#!/usr/bin/env python
#-*-coding:utf-8-*-
import argparse,os,sys,errno,json,time,tempfile,shutil

# Colors for print
CEND      = '\33[0m'
CRED    = '\33[31m'
CREDBG    = '\33[41m'
CWHITE  = '\33[37m'
CGREEN  = '\33[32m'
CBOLD     = '\33[1m'

def check_command_output(command):
    import subprocess
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (result, err) = p.communicate()
    # Wait for date to terminate. Get return returncode
    p_status = p.wait()
    return result,err,p.returncode

def exit_on_msg(msg):
    print(CBOLD+CRED+"Error occurs with message:\n"+msg.rstrip()+"\n"+CEND)
    sys.exit(errno.EACCES)

def symbolicate_address_with_entry(addr2line_path,sopath,entry_point_address,symbol_address):
    entry_point_address_dec=int(entry_point_address,16)
    symbol_address_dec=int(symbol_address,16)
    real_address_dec=entry_point_address_dec+symbol_address_dec
    result,err,returncode=check_command_output(addr2line_path+" -e "+sopath+" "+hex(real_address_dec))
    if returncode != 0:
        exit_on_msg("Invalid libflutter.so "+sopath)
    return result

def read_entry_address(readelf_path,sopath):
    result,err,returncode=check_command_output(readelf_path+" -h "+sopath)
    if returncode != 0:
        exit_on_msg("Invalid libflutter.so "+sopath)
    expected_prefix="Entry point address:"
    for line in result.split("\n"):
        line=line.strip()
        if line.startswith(expected_prefix):
            return line[len(expected_prefix):].strip()
    exit_on_msg(expected_prefix+" not found.")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    file_name=os.path.basename(__file__)
    parser.add_argument('-h','--help',action='help',default=argparse.SUPPRESS,help=file_name+' -c crashreport-file-path -a addr2line-command-full-path -s libflutter.so-with-symbols-full-path')
    parser.add_argument("-c", "--crash", help="crashreport file")
    parser.add_argument("-a","--addr2line", help="addr2line command full-path")
    parser.add_argument("-s","--so_with_symbols_path", help="libflutter.so with symbols full path")
    parser.add_argument("-v", "--verbose", help="print verbose logging",dest='verbose')
    parser.set_defaults(verbose=False)
    args = parser.parse_args()
    crash_path = args.crash
    addr2line_path=args.addr2line
    symbols_so_path=args.so_with_symbols_path
    prior_cwd=os.getcwd()
    
    script_dir=os.path.dirname(os.path.abspath(__file__))
    
    if crash_path is None or os.path.exists(crash_path) is False or  addr2line_path is None or os.path.exists(addr2line_path) is False or symbols_so_path is None or os.path.exists(symbols_so_path) is False :
        exit_on_msg("Use -h to see how to use this script")
    
    if os.path.basename(os.path.normpath(addr2line_path)).endswith("addr2line") is False or  os.path.basename(os.path.normpath(symbols_so_path))=="libflutter.so" is False :
        exit_on_msg("Use -h to see how to use this script")

    addr2line_folder=os.path.dirname(addr2line_path)
    addr2line_basename=os.path.basename(os.path.normpath(addr2line_path))
    readelf_command_fullpath=os.path.join(addr2line_folder,addr2line_basename.replace("-addr2line","-readelf"))

    if os.path.exists(readelf_command_fullpath) is False:
        exit_on_msg(readelf_command_fullpath+" not exists.")

    entry_point_address=read_entry_address(readelf_command_fullpath,symbols_so_path)

    with open(crash_path, 'r') as crashfile:
        lines=crashfile.read().split("\n")
        for line in lines:
            compos=line.strip().split(" ")
            if len(compos)!=4 or compos[3]!="libflutter.so":
                continue
            symbolicated_info=symbolicate_address_with_entry(addr2line_path,symbols_so_path,entry_point_address,compos[2])
            print(line.strip()+"--->"+symbolicated_info.strip())

    os.chdir(prior_cwd)

if __name__ == '__main__':
    main()

