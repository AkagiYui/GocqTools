import os
import random
import subprocess
import platform

import requests

from ay_advance import GocqConnection, TextToMidi
from ay_advance.GocqConnection import CqCode
from global_variables import get_global

logger = get_global('logger')

module_name = 'midi转语音'
module_version = '0.0.2'

run_in_shell = platform.system().strip().lower().startswith('win')


def init():
    global logger
    logger = get_global('logger')
    logger.debug(f'{module_name}({module_version}) 初始化完成')


def enable():
    logger.debug(f'{module_name}({module_version}) 被启动了')


def make_filename():
    temp_name = ''.join(random.sample('ABCDEFGHIJKLMNOPQRSTUVWXYZzyxwvutsrqponmlkjihgfedcba9876543210', 16))
    temp_name = './temp/' + temp_name
    return temp_name


def midi_to_audio(midi_file: str, audio_file: str, soundfont: int = 0, gain: float = 0.2):
    soundfont_list = [
        'SalC5Light2.sf2',
        'MuseScore_General.sf2',
    ]

    try:
        filename_soundfont = soundfont_list[soundfont]
    except IndexError:
        filename_soundfont = soundfont_list[0]
    filename_soundfont = './functions/midi_to_record/' + filename_soundfont

    cmd_list = [
        'fluidsynth',
        '-ni',
        filename_soundfont,
        midi_file,
        '-F',
        audio_file,
        '-g',
        str(gain)
    ]
    ret = subprocess.call(cmd_list,
                          shell=run_in_shell,
                          cwd=os.getcwd(),
                          stdout=open(os.devnull, 'w'),
                          stderr=subprocess.STDOUT)
    return not ret


def audio_to_mp3(audio_file: str, mp3_file: str):
    cmd_list = ['ffmpeg', '-i', audio_file, mp3_file]
    ret = subprocess.call(cmd_list,
                          shell=run_in_shell,
                          cwd=os.getcwd(),
                          stdout=open(os.devnull, 'w'),
                          stderr=subprocess.STDOUT)
    return not ret


WORD_PREFIX = ['演奏', '弹奏', 'midi']


# 返回 0继续处理 1终止处理
def main(conn: GocqConnection, msg):
    limit_size = 1
    if msg['post_type'] == 'notice':
        if msg['notice_type'] == 'group_upload':
            file_size = msg['file']['size']
            file_size = file_size / 1024 / 1024  # 单位MB
            if file_size > limit_size:
                return 0
            file_name: str = msg['file']['name']
            if file_name.split('.')[-1].lower() != 'mid':
                return 0
            file_url = msg['file']['url']
            file_content: bytes = requests.get(file_url).content
            filename_base = make_filename()
            filename_midi = filename_base + '.mid'
            filename_wav = filename_base + '.wav'
            filename_mp3 = filename_base + '.mp3'
            with open(filename_midi, 'wb') as f:
                f.write(file_content)
            if midi_to_audio(filename_midi, filename_wav, 1, 0.2):
                if audio_to_mp3(filename_wav, filename_mp3):
                    send_msg = CqCode.record_local(filename_mp3)
                    os.remove(filename_mp3)
                else:
                    send_msg = 'mdi转语音：音频压缩失败.'
                os.remove(filename_wav)
            else:
                send_msg = 'midi转语音：渲染失败.'
            os.remove(filename_midi)
        else:
            return 0
    elif msg['post_type'] == 'message':
        message: str = msg['message']
        for w in WORD_PREFIX:
            if message.startswith(w):
                message = message[len(w):]
        if message == '' or message == msg['message']:
            return 0

        midd = TextToMidi(message)
        midd.make(127)
        if midd.get_length():
            filename_base = make_filename()
            filename_midi = filename_base + '.mid'
            filename_wav = filename_base + '.wav'
            filename_mp3 = filename_base + '.mp3'
            midd.save(filename_midi)

            if midi_to_audio(filename_midi, filename_wav, 0, 0.7):
                if audio_to_mp3(filename_wav, filename_mp3):
                    send_msg = CqCode.record_local(filename_mp3)
                    os.remove(filename_mp3)
                else:
                    send_msg = 'midi文本转语音：音频压缩失败.'
                os.remove(filename_wav)
            else:
                send_msg = 'midi文本转语音：渲染失败.'
            os.remove(filename_midi)
        else:
            send_msg = 'midi文本转语音：音频长度为0.'
    else:
        return 0

    msg['message'] = send_msg
    conn.Api.send_message(msg)
    return 1
