#!/bin/python3
import argparse
import re
import os
import subprocess
# import sys,io,codecs

# # sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

# コメント、バックスラッシュ、空白の除去
def clean_path(line):
    # コメント除去
    line = re.sub(r'#.*|//.*', '', line)  # '#'や'//'以降の文字列を除去
    line = re.sub(r'/\*.*?\*/', '', line, flags=re.DOTALL)  # '/* */'のコメントを除去
    line = re.sub(r'::env\(WORKAREA\)', '\{WORKAREA\}', line, flags=re.DOTALL) 
    line = line.replace('\\', '')  
    line = line.replace('+', ' ')  
    line = line.replace('=', ' ')  
    line = line.replace('"', ' ')  
    line = line.replace('\[', ' ')  
    line = line.replace('\]', ' ') 
    return line

def get_dirpath(path)
    dir_path = os.path.dirname(path)
    dir_path_csh = subprocess.run(['csh', '-c', '(cd ' + dir_path + ' pwd)'], stdout=subprocess.PIPE)
    dir_path_real = dir_path_csh.stdout.decode('utf-8')
    return dir_path_real.strip()
# >>> aaa = subprocess.run(['csh', '-c', '(cd ${WORKAREA}/resources/ip_audio_lib/source/verilog/rtl; pwd)'], stdout=subprocess.PIPE)
# >>> bbb = aaa.stdout.decode('utf-8')
# >>> print (bbb.strip())
# /opt/rmrepo/pool1/data/RC_RT0DEE_10PG_11ZK_A7A/RDT_RT3KY5_21F_3U6L_A7A/ip_audio_lib.Golden_test_08212024_0_tc44/ip_audio_lib/source/verilog/rtl

def resolve_symlink(path):
    """
    シンボリックリンクのネストを追跡し、環境変数が含まれている場合は展開して、
    最終的なターゲットファイルのパスを返す。
    """
    try:
        # 環境変数を展開
        expanded_path = os.path.expandvars(path)
        # リンクが最終的に指しているファイル/ディレクトリの実際のパスを取得
        real_path = os.path.realpath(expanded_path)
        return real_path
    except Exception as e:
        return str(e)

# ファイルを読み込み、クリーンアップしたPATHリストを作成
def read_paths(filename):
    paths = {}
    linenum = 0
    with open(filename, 'r') as file:
        for line in file:
            linenum += 1
            # print(line)
    # pattern = r"(?:\s*[=|\'|\"]\s*)([^\'\"=\s]+)(?:\s*)"
    
    # # 正規表現にマッチする部分をすべて取得
    # matches = re.findall(pattern, text)

            clean = clean_path(line)
            fullpath = re.search(r'[\s^](\${\w+}|/)\S+\.(vhd|sv|v|svh)[\s$]',clean)
            if fullpath:
                fullpath = fullpath.group()
                filename = re.search(r'[\w\-]+\.(vhd|sv|v|svh)[\s$]',fullpath)
                if filename:
                    filename = filename.group()
                    filename = filename.strip() 
                fullpath = fullpath.strip()
                # print(filename,fullpath)
                # dirpath = get_dirpath(fullpath)
                # paths[filename]= {'LN': str(linenum).rjust(10), 'PATH': dirpath+'/'+filename}
                paths[filename]= {'LN': str(linenum).rjust(10), 'PATH': resolve_symlink(fullpath)}

            # if clean and (clean.startswith('/') or clean.startswith('$') or clean.startswith('e')):
            #     paths.add(clean)
    return paths

# 差分を表示
def compare_paths(paths_a, paths_b):
    for filename,fullpath in paths_b.items():
        filename = paths_a.get('PATH',{}).get('PATH',None)
        if filename:
            if paths_a[filename]['PATH']  != paths_b[filename]['PATH'] :
                print('#UM A :'+paths_a[filename]['LN']+' '+paths_a[filename]['PATH'] )
                print('#UM B :'+paths_b[filename]['LN']+' '+paths_b[filename]['PATH'] )
        else :
            print('#xA B ',paths_b[filename]['PATH'] )
    for filename,fullpath in paths_a.items():
        if filename not in paths_b :
            print('#xB A ',paths_a[filename]['PATH'] )

# ファイルAの情報をエクスポート
def export_paths(paths_a):
    # print("ファイルAに記述されているファイルのPATH:")
    for filename,fullpath in paths_a.items():
        print(paths_a[filename]['LN']+' '+paths_a[filename]['PATH'])     

# メイン処理
def main():
    parser = argparse.ArgumentParser(description="ファイルPATHの比較ツール")
    parser.add_argument('file_a', help='file A')
    parser.add_argument('file_b', nargs='?', help='file B', default=None)
    parser.add_argument('--export', action='store_true', help='print paths of file A')
    
    args = parser.parse_args()

    # ファイルAのPATHリストを作成
    paths_a = read_paths(args.file_a)

    if args.export:
        # --exportが指定された場合はファイルAのPATHのみエクスポート
        export_paths(paths_a)
    else:
        # --exportが指定されていない場合はファイルAとファイルBを比較
        if args.file_b:
            paths_b = read_paths(args.file_b)
            compare_paths(paths_a, paths_b)
        else:
            print("Error")

if __name__ == "__main__":
    main()