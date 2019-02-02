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

#base64 encoding for "This is the dart environment."
unique_folder_name="VGhpcyBpcyB0aGUgZGFydCBlbnZpcm9ubWVudC4="

def check_command_output(command):
    import subprocess
    print("Command:"+command)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (result, err) = p.communicate()
    # Wait for date to terminate. Get return returncode
    p_status = p.wait()
    print("Result:"+result.strip()+";error:"+err.strip()+";returnCode:"+str(p.returncode))
    return result,err,p.returncode

def read_dart_gitsha(depth_file):
    import re
    with open(depth_file, 'r') as myfile:
        deps_content=myfile.read().replace('\n', '')
    m = re.search('\'dart_revision\': \'[0-9a-z]+\'',deps_content)
    gitsha=(m.group(0).split(':')[1]).strip()
    return gitsha[1:len(gitsha)-2]

def exit_on_msg(msg):
    print(CBOLD+CRED+"Error occurs with message:\n"+msg.rstrip()+"\n"+CEND)
    sys.exit(errno.EACCES)

def sparse_checkout_engine_deps(engine_version):
    cwd=os.getcwd()
    result,err,returncode = check_command_output("which gclient")
    if returncode != 0:
        exit_on_msg("Please make sure that gclient is installed and configured in your PATH environment.")
    if os.path.exists("engine") is False:
        check_command_output("mkdir engine && cd engine && git init && git remote add origin -f git@github.com:flutter/engine.git && git config core.sparsecheckout true && echo \"DEPS\" >> .git/info/sparse-checkout && git pull --depth=1 origin master && git reset --hard "+engine_version)
    os.chdir(cwd)
    return read_dart_gitsha(os.path.join(cwd,"engine","DEPS"))

def checkout_dartsdk_with_sha(dart_gitsha):
    cwd=os.getcwd()
    if os.path.exists(".gclient") is False:
        check_command_output("gclient config --name=sdk https://dart.googlesource.com/sdk.git@"+dart_gitsha)
        check_command_output("gclient sync")
    os.chdir(cwd)
    return os.path.join(cwd,"sdk")

def generate_dart_snapshot(dart_bin_dir,sdk_path,package_root_rel_path,entry_dart_file,snapshot_name,training_flags):
    cwd=os.getcwd()
    snapshot_to_save=os.path.join(os.getcwd(),snapshot_name)
    os.chdir(os.path.join(sdk_path,package_root_rel_path))
    dart_binary_path=os.path.join(dart_bin_dir,"dart")
    if os.path.exists(snapshot_to_save):
        os.remove(snapshot_to_save)
    if training_flags is None:
        training_flags="";
    check_command_output(dart_binary_path+" --snapshot="+snapshot_to_save+" --snapshot-kind=app-jit --packages="+os.path.join(sdk_path,".packages")+" "+entry_dart_file+" "+training_flags)
    os.chdir(cwd)

def generate_snapshots(dart_sdk_path, flutter_path):
    cwd=os.getcwd()
    flutter_dart_bin_path=os.path.join(flutter_path,"bin","cache","dart-sdk","bin")
    training_flags=" --sdk="+os.path.join(cwd,"sdk","sdk")+" --train-using="+os.path.join(cwd,"sdk","pkg","analyzer_cli")
    generate_dart_snapshot(flutter_dart_bin_path,dart_sdk_path,os.path.join("pkg","analysis_server"),os.path.join("bin","server.dart"),"analysis_server.dart.snapshot",training_flags)
    training_flags=" --dart-sdk="+os.path.join(cwd,"sdk","sdk")+" "+os.path.join(cwd,"sdk","tests","language_2","first_test.dart")
    generate_dart_snapshot(flutter_dart_bin_path,dart_sdk_path,os.path.join("pkg","analyzer_cli"),os.path.join("bin","analyzer.dart"),"dartanalyzer.dart.snapshot",training_flags)
    training_flags=" --help"
    generate_dart_snapshot(flutter_dart_bin_path,dart_sdk_path,os.path.join("third_party","pkg","dartdoc"),os.path.join("bin","dartdoc.dart"),"dartdoc.dart.snapshot",training_flags)
    training_flags=os.path.join(dart_sdk_path,"third_party","pkg_tested","dart_style")
    generate_dart_snapshot(flutter_dart_bin_path,dart_sdk_path,os.path.join("third_party","pkg_tested","dart_style"),os.path.join("bin","format.dart"),"dartfmt.dart.snapshot",training_flags)
    #Ignore this as not modified generally.
    #generate_dart_snapshot(flutter_dart_bin_path,dart_sdk_path,os.path.join("third_party","pkg","pub"),os.path.join("bin","pub.dart"),"kernel-service.dart.snapshot",training_flags)
    training_flags=""
    generate_dart_snapshot(flutter_dart_bin_path,dart_sdk_path,os.path.join("third_party","pkg","pub"),os.path.join("bin","pub.dart"),"pub.dart.snapshot",training_flags)

def main():
    parser = argparse.ArgumentParser(add_help=False)
    file_name=os.path.basename(__file__)
    parser.add_argument('-h','--help',action='help',default=argparse.SUPPRESS,help=file_name+' -fp flutter-root-path')
    parser.add_argument("-fp", "--flutter_path", help="flutter root path")
    parser.add_argument("-v", "--verbose", help="print verbose logging",dest='verbose')
    parser.set_defaults(verbose=False)
    args = parser.parse_args()
    flutter_path = args.flutter_path
    prior_cwd=os.getcwd()
    script_dir=os.path.dirname(os.path.abspath(__file__))
    engine_version_rel_path = os.path.join("bin","internal","engine.version")

    if flutter_path is None or os.path.exists(flutter_path) is False or os.path.exists(os.path.join(flutter_path,engine_version_rel_path)) is False:
        exit_on_msg("Use -h to see how to use this script")
    with open(os.path.join(flutter_path,engine_version_rel_path), 'r') as myfile:
        engine_version=myfile.read().replace('\n', '')
    
    if os.path.exists(os.path.join(prior_cwd,unique_folder_name)) is False:
        os.mkdir(unique_folder_name)
    os.chdir(unique_folder_name)
    
    dart_sha=sparse_checkout_engine_deps(engine_version)
    dart_sdk_path = checkout_dartsdk_with_sha(dart_sha)
    generate_snapshots(dart_sdk_path, flutter_path)
    os.chdir(prior_cwd)

if __name__ == '__main__':
    main()