#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import argparse
import sys
import os

exclude_map = {
    '[ ParamPatcher ]': True,
}

def replace_descriptions_in_ct(input_file, strings_dir, existing_strings):
    """
    Extract all Description strings from CheatEntry elements in a .ct file

    Args:
        input_file (str): Path to the input .ct file
        strings_dir (str): Path to the strings directory
        existing_strings (list): List of existing strings to exclude
    """

    def process_cheat_entry(cheat_entry, existing_strings):
        """
        Recursively process CheatEntry elements, skipping ParamPatcher entries and their children

        Args:
            cheat_entry: The CheatEntry element to process
            existing_strings (list): List of existing strings to exclude
        """
        # Find Description element
        description_element = cheat_entry.find('Description')

        if description_element is not None and description_element.text:
            description_text = description_element.text.strip()
            has_quotes = description_text.startswith('"') and description_text.endswith('"')
            if has_quotes:
                description_text = description_text[1:-1]

            # Find DropDownList element
            drop_down_list_element = cheat_entry.find('DropDownList')
            if drop_down_list_element is not None and drop_down_list_element.text:
                new_file = os.path.join(strings_dir, f'{description_text}_new.txt')
                if os.path.exists(new_file):
                    with open(new_file, 'r', encoding='utf-8') as f:
                        new_string = f.read()
                    if new_string is not None and len(new_string) > 0:
                        drop_down_list_element.text = new_string

            # Skip ParamPatcher entries and their children
            if description_text in exclude_map:
                return

            # Replace description if found in existing_strings
            new_string = existing_strings.get(description_text)
            if new_string is not None and len(new_string) > 0:
                description_element.text = f'"{new_string}"' if has_quotes else new_string

        # Process child CheatEntries elements first
        child_cheat_entries_elements = cheat_entry.findall('CheatEntries')
        for cheat_entries in child_cheat_entries_elements:
            # Find all CheatEntry elements under each CheatEntries
            cheat_entry_elements = cheat_entries.findall('CheatEntry')
            for child_entry in cheat_entry_elements:
                process_cheat_entry(child_entry, existing_strings)

    try:
        # Parse the XML file
        tree = ET.parse(input_file)
        root = tree.getroot()

        # Find all CheatEntries elements
        cheat_entries_elements = root.findall('CheatEntries')

        for cheat_entries in cheat_entries_elements:
            # Find all CheatEntry elements under each CheatEntries
            cheat_entry_elements = cheat_entries.findall('CheatEntry')

            for cheat_entry in cheat_entry_elements:
                # Process each CheatEntry recursively
                process_cheat_entry(cheat_entry, existing_strings)

        # Write to ct file with replaced strings
        tree.write(f"{os.path.splitext(input_file)[0]}_cn{os.path.splitext(input_file)[1]}", encoding='utf-8', xml_declaration=True)

        print(f"成功替换描述字符串")


    except ET.ParseError as e:
        print(f"XML 解析错误: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"文件未找到: {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"处理文件时出错: {e}")
        sys.exit(1)

def main():
    """
    Main function to handle command line arguments and execute the extraction
    """
    parser = argparse.ArgumentParser(
        description="替换 .ct 文件中的 Description 字符串",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python replace_strings.py input.ct output.txt
  python replace_strings.py cheat_table.ct descriptions.txt
        """
    )

    parser.add_argument('ct_file',
                       help='输入的 .ct 文件路径')
    parser.add_argument('strings_dir',
                        help='替换的文本文件目录')

    args = parser.parse_args()

    # Check if input file exists
    if not os.path.exists(args.ct_file):
        print(f"错误: 输入文件不存在: {args.ct_file}")
        sys.exit(1)

    if not os.path.exists(args.strings_dir):
        print(f"错误: 输入文件不存在: {args.strings_dir}")
        sys.exit(1)

    existing_strings = {}
    strings_file = os.path.join(args.strings_dir, 'strings.txt')
    if not os.path.exists(strings_file):
        print(f"错误: 输入文件不存在: {strings_file}")
        sys.exit(1)

    with open(strings_file, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            if line.startswith('< '):
                original_string = line[2:].strip()
            elif line.startswith('> '):
                if original_string is not None:
                    new_string = line[2:].strip()
                    existing_strings[original_string] = new_string
                    original_string = None

    # Extract descriptions
    replace_descriptions_in_ct(args.ct_file, args.strings_dir, existing_strings)

if __name__ == "__main__":
    main()
