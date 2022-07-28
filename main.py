import re
element_type  = 'single'
element_name  = '.*module.*"tool-provision-application".*'
path = 'sample.tf'
lines_to_add = ["provision_internal_alb         = var.provision_internal_alb", "provision_external_alb         = var.provision_external_alb"]
lines_to_remove = [".*provision_ecs_cluster.*=.*var.provision_ecs_cluster.*"]
BLOCK_START = '.*{.*'
BLOCK_END = '.*}.*'


def get_block_delimeter_lines(_path, _element_name) :
    start_block_line, end_block_line  = 0, 0
    balanced_brackets = 0

    with open(_path, 'r') as fp:

        for i, line in enumerate(fp) :
            if re.search(_element_name, line) :
                start_block_line = i

            if(start_block_line!=0 and re.search(BLOCK_START, line)):
                balanced_brackets += 1

            if(start_block_line!=0 and re.search(BLOCK_END, line)):
                end_block_line = i
                balanced_brackets -= 1

            if (start_block_line!=0 and end_block_line!=0 and balanced_brackets ==0):
                return [start_block_line, end_block_line]


def get_block_sections(_path):
    sections = []
    with open(_path, 'r') as fp:
        for i, line in enumerate(fp) :                
            if re.search('.*{.*', line) :
                sections.append(line)
    return [get_block_delimeter_lines(path,section) for section in sections]


def between_two_lines(number,limit_min,limit_max):
    return limit_min <= number <= limit_max


def get_lines_in_out_sections(_type, _sections, _index_list):
    index_to_filter = []

    for index in _index_list:
        found = False
        for section in _sections:
            if between_two_lines(index, section[0], section[1]):
                found = True

        if _type == 'inside' and not found:
            index_to_filter.append(index)
        elif _type == 'outside' and found:
            index_to_filter.append(index)
    
    return [index for index in _index_list if index not in index_to_filter]


def get_existing_keys(_path, _lines_to_add):
    index_key = []
    for line_to_add in _lines_to_add:
        key = re.match(r'(.*)=.*', line_to_add.replace(' ','')).groups()[0]

        pattern_to_search_key = f".*{key}.*=.*"

        with open(_path, 'r') as fp:
            for i, line in enumerate(fp) :
                    if re.search(pattern_to_search_key, line) :
                        index_key.append((i,key))
    index_key.sort()

    return index_key


def remove_blank_lines(_content):
    while _content[-1] == '\n':
        _content.pop(-1)
    return _content


def delete_lines(_path, _index_to_delete):
    count_lines_deleted = 0
    with open(_path, "r+") as fp :
        content = fp.readlines()
        for index in _index_to_delete :
            del content[index-count_lines_deleted]
            count_lines_deleted += 1

        fp.seek(0)
        fp.truncate()
        fp.writelines(content)


def clean_keys_if_exists(_path, _element_type, _element_name, _lines_to_add):
    index_to_delete_filtered = []
    line_keys = list(zip(*get_existing_keys(_path, _lines_to_add)))
    keys_exists = [] if len(line_keys) == 0 else line_keys[0]
    
    if _element_type == 'block':
        section = get_block_delimeter_lines(_path, _element_name)             
        index_to_delete_filtered = get_lines_in_out_sections('inside',[section], keys_exists)        
    elif _element_type == 'single':
        sections = get_block_sections(path)        
        index_to_delete_filtered = get_lines_in_out_sections('outside', sections, keys_exists)
    delete_lines(_path, index_to_delete_filtered)


def add_lines(_element_type, _path, _element_name, _lines_to_add) :    
    content = []

    with open(_path, "r+") as fp :
        content = fp.readlines()
        
        end_block_line = get_block_delimeter_lines(_path, _element_name)[1] if _element_type == 'block' else len(content)

        content = remove_blank_lines(content)

        [ content.insert(end_block_line, ("  " if _element_type == 'block' else "\n") + line + "\n") for line in _lines_to_add ]

        fp.seek(0)
        fp.truncate()
        fp.writelines(content)


def add_lines_main(_path, _element_type, _element_name, _lines_to_add):

    clean_keys_if_exists(_path, _element_type, _element_name, _lines_to_add)

    if _element_type == 'block':
        add_lines(_element_type, _path, _element_name, _lines_to_add)
    elif _element_type == 'single':
        add_lines(_element_type, _path, '', _lines_to_add)


def get_lines_to_delete(_path, _lines_to_remove):
    index_to_delete = []
    with open(_path, "r") as fp :
        for i, line in enumerate(fp) :
            for line_to_remove in _lines_to_remove :
                if re.search(line_to_remove, line) :
                    index_to_delete.append(i)
    return index_to_delete


def remove_lines_main(_path, _element_type, _element_name, _lines_to_remove):

    index_to_delete = get_lines_to_delete(_path, _lines_to_remove)

    if _element_type == 'block':
        section = get_block_delimeter_lines(path, _element_name)
        index_to_delete_filtered = get_lines_in_out_sections('inside',[section], index_to_delete)
    elif _element_type == 'single':
        sections = get_block_sections(path)        
        index_to_delete_filtered = get_lines_in_out_sections('outside', sections, index_to_delete)
    
    delete_lines(_path, index_to_delete_filtered)


#remove_lines_main(path, element_type, element_name, lines_to_remove)
add_lines_main(path, element_type, element_name, lines_to_add)