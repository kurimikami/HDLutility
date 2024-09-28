import re
import sys

def remove_comments(sv_code):
    """SystemVerilogコードからコメントを削除する関数"""
    # // 以降のコメントを削除
    sv_code = re.sub(r'//.*', '', sv_code)
    # /* ... */ のコメントを削除（複数行対応）
    sv_code = re.sub(r'/\*.*?\*/', '', sv_code, flags=re.DOTALL)
    return sv_code

def convert_sv_port_declaration(sv_code):
    # コメントを削除
    sv_code = remove_comments(sv_code)

    # ステップ1: モジュール宣言部分とポート宣言部分を分離
    module_pattern = re.compile(r'(module\s+\w+\s*$begin:math:text$)([\\s\\S]*?)($end:math:text$;)', re.IGNORECASE)
    port_declarations = re.findall(r'(input|output)\s+($begin:math:display$.*?:.*?$end:math:display$)?\s*(\w+)\s*;', sv_code, re.IGNORECASE)

    # モジュールヘッダ部分を処理
    match = module_pattern.search(sv_code)
    if match:
        module_header = match.group(1)
        port_list = [port.strip() for port in match.group(2).split(',') if port.strip()]
        module_footer = match.group(3)
    else:
        raise ValueError("Invalid SystemVerilog module")

    # ステップ2: 各ポートの宣言を変換
    new_port_list = []
    for port in port_list:
        for port_decl in port_declarations:
            port_type, port_width, port_name = port_decl
            if port == port_name:
                # マクロ展開せず、そのまま幅を出力する
                if port_width:
                    new_port_list.append(f'{port_type} {port_width} {port_name}')
                else:
                    new_port_list.append(f'{port_type} {port_name}')

    # ステップ3: 出力形式にまとめる（最後のカンマを削除）
    new_module_declaration = module_header + '\n' + ',\n'.join(new_port_list) + '\n' + module_footer + '\nendmodule'
    return new_module_declaration

def main(input_file, output_file):
    # 入力ファイルを読み込む
    with open(input_file, 'r') as f:
        sv_code = f.read()

    # 変換処理
    output_sv_code = convert_sv_port_declaration(sv_code)

    # 出力ファイルに書き込む
    with open(output_file, 'w') as f:
        f.write(output_sv_code)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    main(input_file, output_file)