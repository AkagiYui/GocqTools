"""
    用文件头判断文件格式
    真正的文件格式判断
    https://blog.csdn.net/privateobject/article/details/78069500
"""


# 用16进制字符串的目的是可以知道文件头是多少字节
# 各种文件头的长度不一样，少半2字符，长则8字符
from io import BufferedReader

type_list = {
    "68746D6C3E": 'html',
    "d0cf11e0a1b11ae10000": 'xls',
    "44656C69766572792D64": 'eml',
    'ffd8ffe000104a464946': 'jpg',
    '89504e470d0a1a0a0000': 'png',
    '47494638396126026f01': 'gif',
    '49492a00227105008037': 'tif',
    '424d228c010000000000': 'bmp',
    '424d8240090000000000': 'bmp',
    '424d8e1b030000000000': 'bmp',
    '41433130313500000000': 'dwg',
    '3c21444f435459504520': 'html',
    '3c21646f637479706520': 'htm',
    '48544d4c207b0d0a0942': 'css',
    '696b2e71623d696b2e71': 'js',
    '7b5c727466315c616e73': 'rtf',
    '38425053000100000000': 'psd',
    '46726f6d3a203d3f6762': 'eml',
    'd0cf11e0a1b11ae10000': 'doc',
    'd0cf11e0a1b11ae10000': 'vsd',
    '5374616E64617264204A': 'mdb',
    '252150532D41646F6265': 'ps',
    '255044462d312e350d0a': 'pdf',
    '2e524d46000000120001': 'rmvb',
    '464c5601050000000900': 'flv',
    '00000020667479706d70': 'mp4',
    '49443303000000002176': 'mp3',
    '000001ba210001000180': 'mpg',
    '3026b2758e66cf11a6d9': 'wmv',
    '52494646e27807005741': 'wav',
    '52494646d07d60074156': 'avi',
    '4d546864000000060001': 'mid',
    '504b0304140000080044': 'zip',
    '504b03040a0000080000': 'zip',
    '504b03040a0000000000': 'zip',
    '526172211a0700cf9073': 'rar',
    '235468697320636f6e66': 'ini',
    '504b03040a0000000000': 'jar',
    '4d5a9000030000000400': 'exe',
    '3c25402070616765206c': 'jsp',
    '4d616e69666573742d56': 'mf',
    '3c3f786d6c2076657273': 'xml',
    '494e5345525420494e54': 'sql',
    '7061636b616765207765': 'java',
    '406563686f206f66660d': 'bat',
    '1f8b0800000000000000': 'gz',
    '6c6f67346a2e726f6f74': 'properties',
    'cafebabe0000002e0041': 'class',
    '49545346030000006000': 'chm',
    '04000000010000001300': 'mxp',
    '504b0304140006000800': 'docx',
    'd0cf11e0a1b11ae10000': 'wps',
    '6431303a637265617465': 'torrent',
}


# 字节码转16进制字符串
def bytes_to_hex(__bytes):
    num = len(__bytes)
    hex_str = u''
    for i in range(num):
        t = u'%x' % __bytes[i]
        if len(t) % 2:
            hex_str += u'0'
        hex_str += t
    return hex_str.upper()


def get_file_format(file):
    if isinstance(file, str):
        import os
        if not os.path.isfile(file):
            return None
        with open(file, 'rb') as f:
            # 提取关键码
            bins = f.read(20)  # 提取20个字符
    elif isinstance(file, bytes):
        bins = file[:19]
    elif isinstance(file, BufferedReader):
        bins = file.read(20)
    else:
        return None
    bins = bytes_to_hex(bins)  # 转码
    bins = bins.lower()  # 小写
    file_type = ''
    # 关键码比对中
    for hex_code in type_list.keys():
        lens = len(hex_code)  # 需要的长度
        if bins[0:lens] == hex_code:
            file_type = type_list[hex_code]
            break
    # 全码未找到，优化处理，码表取5位验证
    if file_type == '':
        bins = bins[0:5]
        for hex_code in type_list.keys():
            if len(hex_code) > 5 and bins == hex_code[0:5]:
                file_type = type_list[hex_code]
                break
    return file_type
