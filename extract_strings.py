#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import argparse
import sys
import os

exclude_strings = {}

def replace_invalid_chars(text):
    return ''.join(c if c.isalnum() else '_' for c in text)

def extract_descriptions_from_ct(input_file, output_dir):
    """
    Extract all Description strings from CheatEntry elements in a .ct file

    Args:
        input_file (str): Path to the input .ct file
        output_dir (str): Path to the output text file
    """

    def process_cheat_entry(cheat_entry):
        """
        Recursively process CheatEntry elements, skipping ParamPatcher entries and their children

        Args:
            cheat_entry: The CheatEntry element to process
        """

        # Find Description element
        description_element = cheat_entry.find('Description')

        if description_element is not None and description_element.text:
            description_text = description_element.text.rstrip('\r\n')
            if description_text.startswith('"') and description_text.endswith('"'):
                description_text = description_text[1:-1]

            # Skip ParamPatcher entries and their children
            if description_text in exclude_strings:
                return

            # Find DropDownList element
            drop_down_list_element = cheat_entry.find('DropDownList')
            if drop_down_list_element is not None and drop_down_list_element.text:
                if len(drop_down_list_element.text) > 0 and drop_down_list_element.text not in existing_dropdownlists:
                    dropdownlists.append(drop_down_list_element.text)

            # Add non-empty description to list
            if len(description_element.text) > 0 and description_text not in existing_strings:
                print(description_text)
                descriptions.append(description_text)

        # Process child CheatEntries elements first
        child_cheat_entries_elements = cheat_entry.findall('CheatEntries')
        for cheat_entries in child_cheat_entries_elements:
            # Find all CheatEntry elements under each CheatEntries
            cheat_entry_elements = cheat_entries.findall('CheatEntry')
            for child_entry in cheat_entry_elements:
                process_cheat_entry(child_entry)

    try:
        descriptions_output_file = os.path.join(output_dir, 'strings.txt')
        dropdownlists_output_file = os.path.join(output_dir, 'dropdownlists.txt')

        existing_strings = {}
        if os.path.exists(descriptions_output_file):
            with open(descriptions_output_file, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    if line.startswith('< '):
                        existing_strings[line[2:].rstrip('\r\n')] = True
        try:
            with open(os.path.join(output_dir, 'exclude.txt'), 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    exclude_strings[line.rstrip('\r\n')] = True
        except FileNotFoundError:
            pass

        existing_dropdownlists = {}
        if os.path.exists(dropdownlists_output_file):
            with open(dropdownlists_output_file, 'r', encoding='utf-8') as f:
                text = f.read()
                if text is not None and len(text) > 0:
                    start_index = 0
                    while True:
                        start_index = text.find('\n<<<<<\n', start_index)
                        if start_index < 0:
                            break
                        end_index = text.find('\n=====\n', start_index)
                        if end_index < 0:
                            break
                        existing_dropdownlists[text[start_index + 7:end_index]] = True
                        start_index = end_index + 7

        # Parse the XML file
        tree = ET.parse(input_file)
        root = tree.getroot()

        descriptions = []
        dropdownlists = []

        # Find all CheatEntries elements
        cheat_entries_elements = root.findall('CheatEntries')

        for cheat_entries in cheat_entries_elements:
            # Find all CheatEntry elements under each CheatEntries
            cheat_entry_elements = cheat_entries.findall('CheatEntry')

            for cheat_entry in cheat_entry_elements:
                # Process each CheatEntry recursively
                process_cheat_entry(cheat_entry)

        # Remove duplicates while preserving order
        seen = set()
        unique_descriptions = []
        for description in descriptions:
            if description not in seen:
                seen.add(description)
                unique_descriptions.append(description)

        # Write unique descriptions to output file
        if len(unique_descriptions) > 0:
            with open(descriptions_output_file, 'a+', encoding='utf-8') as f:
                f.seek(0, os.SEEK_END - 1)
                if f.tell() > 0 and f.read() != '\n':
                    f.write('\n')

                for description in unique_descriptions:
                    f.write(f'< {description}\n')
                    f.write('> \n')
            print(f'去重后保留了 {len(unique_descriptions)} 个唯一描述字符串')
            print(f'结果已保存到: {descriptions_output_file}')

        seen = set()
        unique_dropdownlists = []
        for dropdownlist in dropdownlists:
            if dropdownlist not in seen:
                seen.add(dropdownlist)
                unique_dropdownlists.append(dropdownlist)

        if len(dropdownlists) > 0:
            with open(dropdownlists_output_file, 'a+', encoding='utf-8') as f:
                f.seek(0, os.SEEK_END - 1)
                if f.tell() > 0 and f.read() != '\n':
                    f.write('\n')
                for dropdownlist in unique_dropdownlists:
                    f.write(f'\n<<<<<\n{dropdownlist}\n=====\n\n>>>>>\n')

            print(f'去重后保留了 {len(unique_dropdownlists)} 个唯一下拉列表字符串')
            print(f'结果已保存到: {dropdownlists_output_file}')

    except ET.ParseError as e:
        print(f'XML 解析错误: {e}')
        sys.exit(1)
    except FileNotFoundError:
        print(f'文件未找到: {input_file}')
        sys.exit(1)
    except Exception as e:
        print(f'处理文件时出错: {e}')
        sys.exit(1)

def main():
    """
    Main function to handle command line arguments and execute the extraction
    """
    parser = argparse.ArgumentParser(
        description="从 .ct 文件中提取 CheatEntry 的 Description 字符串",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python extract_strings.py input.ct output.txt
  python extract_strings.py cheat_table.ct descriptions.txt
        """
    )

    parser.add_argument('input_file',
                       help='输入的 .ct 文件路径')
    parser.add_argument('output_dir',
                       help='输出的文件的目录')

    args = parser.parse_args()

    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f'错误: 输入文件不存在: {args.input_file}')
        sys.exit(1)

    # Create output directory if it doesn't exist
    if args.output_dir and not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Extract descriptions
    extract_descriptions_from_ct(args.input_file, args.output_dir)

if __name__ == '__main__':
    main()
