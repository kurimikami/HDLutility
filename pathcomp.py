import argparse
import re

# コメント、バックスラッシュ、空白の除去
def clean_path(line):
    # コメント除去
    line = re.sub(r'#.*|//.*', '', line)  # '#'や'//'以降の文字列を除去
    line = re.sub(r'/\*.*?\*/', '', line, flags=re.DOTALL)  # '/* */'のコメントを除去
    line = line.replace('\\', '')  # バックスラッシュを除去
    line = line.strip()  # 空白の除去
    return line

# ファイルを読み込み、クリーンアップしたPATHリストを作成
def read_paths(filename):
    paths = set()
    with open(filename, 'r') as file:
        for line in file:
            clean = clean_path(line)
            if clean and (clean.startswith('/') or clean.startswith('$')):
                paths.add(clean)
    return paths

# 差分を表示
def compare_paths(paths_a, paths_b):
    diff1 = paths_a.intersection(paths_b)
    diff2 = paths_b - paths_a
    diff3 = paths_a - paths_b

    if diff1:
        print("DIFF1 (同名でPATHが異なる):")
        for path in diff1:
            print(f"XX ファイルA: {path}")
            print(f"XX ファイルB: {path}")

    if diff2:
        print("\nDIFF2 (ファイルBにのみ存在):")
        for path in diff2:
            print(f"XB ファイルB: {path}")

    if diff3:
        print("\nDIFF3 (ファイルAにのみ存在):")
        for path in diff3:
            print(f"AX ファイルA: {path}")

# ファイルAの情報をエクスポート
def export_paths(paths_a):
    print("ファイルAに記述されているファイルのPATH:")
    for path in paths_a:
        print(path)

# メイン処理
def main():
    parser = argparse.ArgumentParser(description="ファイルPATHの比較ツール")
    parser.add_argument('file_a', help='ファイルAのパス')
    parser.add_argument('file_b', nargs='?', help='ファイルBのパス (エクスポート時は不要)', default=None)
    parser.add_argument('--export', action='store_true', help='ファイルAのPATHをエクスポートするオプション')
    
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
            print("エラー: ファイルBが指定されていません。ファイルAとBを比較するには両方のファイルを指定してください。")

if __name__ == "__main__":
    main()