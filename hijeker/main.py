#!/bin/python3
import sys

from constants import *

def read_binary_file(file_path, bytes_count = INFINITY, index_in_file = 0):
    result = bytes()
    with open(file_path, 'rb') as open_file:
        open_file.seek(index_in_file)
        for _ in range(bytes_count):
            result = open_file.read(1) + result
    return result

def write_binary_file(file_path, data, index_in_file = 0):
    with open(file_path, 'wb') as open_file:
        open_file.seek(index_in_file)
        result = open_file.write(data)

def get_initial_address(maps_file_path):
    with open(maps_file_path, "r") as maps_file:
        lines = maps_file.readlines()
    first_line_splitted = lines[0].split(" ")
    fisrt_adress_page = first_line_splitted[0].split("-")[0]
    return fisrt_adress_page

def get_program_header_table_offset(mem_file_path, offset_in_mem_int):
    program_header_offset = read_binary_file(mem_file_path, PHOFF_SIZE, offset_in_mem_int + PHOFF_OFFSET)
    return program_header_offset.hex()

def get_program_header_size(mem_file_path, offset_in_mem_int):
    program_header_size = read_binary_file(mem_file_path, E_PHENTSIZE_SIZE, offset_in_mem_int + E_PHENTSIZE_OFFSET)
    return program_header_size.hex()

def get_program_header_count(mem_file_path, offset_in_mem_int):
    program_header_count = read_binary_file(mem_file_path, E_PHNUM_SIZE, offset_in_mem_int + E_PHNUM_OFFSET)
    return program_header_count.hex()

def get_program_header_type(mem_file_path, offset_to_program_header_int):
    program_header_type = read_binary_file(mem_file_path, P_TYPE_SIZE, offset_to_program_header_int + P_TYPE_OFFSET)
    return program_header_type.hex()

def get_program_header_virtual_offset(mem_file_path, offset_to_program_header_int):
    program_header_virtual_offset = read_binary_file(mem_file_path, P_VADDR_SIZE, offset_to_program_header_int + P_VADDR_OFFSET)
    return program_header_virtual_offset.hex()

def get_dynamic_header_offset(mem_file_path, program_header_size, program_header_table_offset, program_header_count):
    for index in range(program_header_count):
        current_program_header_offset = program_header_table_offset + program_header_size * index
        program_header_type = get_program_header_type(mem_file_path, current_program_header_offset)
        program_header_type_int = int(program_header_type, 16)
        if(program_header_type_int == PROGRAM_HEADER_TYPE_DYNAMIC):
            program_header_virtual_offset = get_program_header_virtual_offset(mem_file_path, current_program_header_offset)
            return program_header_virtual_offset

def get_elf64_dyn(mem_file_path, elf64_dyn_address_int):
    elf64_dyn_val = read_binary_file(mem_file_path, ELF64_DYN_VAR_SIZE, elf64_dyn_address_int).hex()
    elf64_dyn_ptr = read_binary_file(mem_file_path, ELF64_DYN_PTR_SIZE, elf64_dyn_address_int + ELF64_DYN_VAR_SIZE).hex()
    return (elf64_dyn_val, elf64_dyn_ptr)

def get_elf64_dyn_pltgot(mem_file_path, dynamic_segment_address_int):
    elf64_dyn = get_elf64_dyn(mem_file_path, dynamic_segment_address_int)
    elf64_dyn_index = 0
    while(int(elf64_dyn[0], 16) != 0 ):
        if(int(elf64_dyn[0], 16) == ELF64_DYN_VAR_PLTGOT):
            return elf64_dyn
        else:
            elf64_dyn_index += 1
            elf64_dyn = get_elf64_dyn(mem_file_path, dynamic_segment_address_int + (elf64_dyn_index * ELF64_DYN_SIZE))

def main():
    process_pid = sys.argv[1]
    process_mem_path = "/proc/{}/mem".format(process_pid)
    process_maps_path = "/proc/{}/maps".format(process_pid)

    initial_adress = get_initial_address(process_maps_path)
    initial_adress_int = int(initial_adress, 16)
    print(initial_adress)
    print(initial_adress_int)
    program_header_offset = get_program_header_table_offset(process_mem_path, initial_adress_int)
    program_header_offset_int = int(program_header_offset, 16)
    program_header_size = get_program_header_size(process_mem_path, initial_adress_int)
    program_header_size_int = int(program_header_size, 16) 
    program_header_count = get_program_header_count(process_mem_path, initial_adress_int)
    program_header_count_int = int(program_header_count, 16)
    print(program_header_offset)
    print(program_header_offset_int)
    print(program_header_size_int)
    print(program_header_count_int)

    dynamic_segment_offset = get_dynamic_header_offset(process_mem_path, program_header_size_int, initial_adress_int + program_header_offset_int, program_header_count_int)
    dynamic_segment_offset_int = int(dynamic_segment_offset, 16)
    print(dynamic_segment_offset)

    elf64_dyn_pltgot = get_elf64_dyn_pltgot(process_mem_path, initial_adress_int + dynamic_segment_offset_int)
    print(elf64_dyn_pltgot)

    elf64_dyn_pltgot_address = elf64_dyn_pltgot[1]
    elf64_dyn_pltgot_address_int = int(elf64_dyn_pltgot_address, 16)
    print(elf64_dyn_pltgot_address)
    write_binary_file(process_mem_path, bytes("00000000000000000000000000000000000000000000000", "utf-8"), elf64_dyn_pltgot_address_int)


if __name__ == '__main__':
    main()