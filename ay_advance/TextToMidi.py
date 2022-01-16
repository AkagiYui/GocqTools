"""
    文本转Midi
    作者: Scarlett凛子
    QQ: 1587524

    格式：多行文本，包括参数行与音符行。行内出现参数时则视为参数行，不解析音符。

    参数行：
        调号：支持大调(1=)和小调(6=)记号，另支持低八度(末尾带2)或高八度(末尾带4)。
            示例：1=C，6=A，1=Bb，1=C2，1=C4。默认1=C。
        节拍：数字+bpm。
            示例：140bpm。默认120。

    音符行：01234567是八个音符，每个音符后面加符号来表示时值和音高。
        音高：#:升半音，b:降半音，.:高八度，,:低八度。
        时值：*:0.5拍，-:1拍，~:1.5拍，=:2拍，+:4拍，^:0.25拍(16分)，':0.125拍(32分)，默认0.5拍。

    文本示例
    6=B 138bpm
    3571.753-2121253-
    211-6,1432121253-
    3571.753-2121253-
    211-6-5-357771.2.7577=~66+
"""
import re
import mido

from ay_advance import AyStr

PITCH_NAME = {'A': -3, 'B': -1, 'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7}
PITCH_LIST = [0, 2, 4, 5, 7, 9, 11]

BASIC_PITCH_ADD = [(0, '6', 3), (2, '#', 1), (2, 'b', -1), (3, '2', -12), (3, '4', 12)]
PITCH_ADD = {'#': 1, 'b': -1, '.': 12, ',': -12}
TIME_ADD = {'*': 0.5, '-': 1, '~': 1.5, '=': 2, '+': 4, '^': 0.25, "'": 0.125}


class TextToMidi:
    text = ''
    bpm = 120
    basic_pitch = 60
    score_list = []
    midi_file = None

    def __init__(self, _text: str = ''):
        self.set_text(_text)

    def set_text(self, _text: str):
        self.text = _text

    def decode(self):
        _basic_pitch = 60
        _bpm = 120
        lines = self.text.split('\n')
        _main_list = []
        for line in lines:
            is_param_line = False

            key_signature = re.search('([16])=([ABCDEFG])([#b]?)([24]?)', line)
            if key_signature is not None:
                is_param_line = True
                basic_pitch = 60
                key_signature = key_signature.groups()
                basic_pitch += PITCH_NAME[key_signature[1]]
                for x in BASIC_PITCH_ADD:
                    if key_signature[x[0]] == x[1]:
                        basic_pitch += x[2]
                _basic_pitch = basic_pitch

            meter = re.search('(\d*)bpm', line.lower())
            if meter is not None:
                is_param_line = True
                _bpm = eval(meter.groups()[0])

            if is_param_line:
                continue

            score = AyStr(line).replace_all(' ', '') + '0'
            little_list = []
            pitch = -1
            length = -1
            for char in score:
                if char in '01234567':
                    if length == 0:
                        length = 0.5
                    little_list.append((_basic_pitch + pitch, length, _bpm))

                    if char == '0':
                        pitch = -1000
                    else:
                        pitch = PITCH_LIST[eval(char) - 1]
                    length = 0
                    continue

                try:
                    pitch += PITCH_ADD[char]
                except KeyError:
                    pass

                try:
                    length += TIME_ADD[char]
                except KeyError:
                    pass
            little_list.pop(0)
            _main_list += little_list
        self.score_list = _main_list

    def make(self, velocity: int = 63):
        self.decode()
        self.midi_file = mido.MidiFile()  # 新建midi文件
        track = mido.MidiTrack()  # 新建midi轨道
        self.midi_file.tracks.append(track)  # 加入这条轨道
        track.append(mido.Message('program_change', channel=0, program=0, time=0))
        for note in self.score_list:
            if note[0] < 0:
                track.append(mido.Message('note_on', note=0, velocity=0, time=0))
                track.append(mido.Message('note_off',
                                          note=0,
                                          velocity=0,
                                          time=int(note[1] * (60 / note[2]) * 1000)))
            else:
                track.append(mido.Message('note_on', note=note[0], velocity=velocity, time=0))
                track.append(mido.Message('note_off',
                                          note=note[0],
                                          velocity=velocity,
                                          time=int(note[1] * (60 / note[2]) * 1000)))

    def save(self, file_path: str):
        self.midi_file.save(file_path)

    def get_length(self):
        if not self.midi_file:
            return None
        return self.midi_file.length


if __name__ == '__main__':
    pass
    text = '''1=Eb 130bpm
0-356*^4^*3212656^32*^1-
6,12^*7,^*433.2.71.*^7^*565
356*^4^*327655671.-32-1==
03,3,03,05,^6,^1^5^6^53^*6,123^6,^1.^7^5^35^*65326,3^21^*6,5,#437,21^5^*435,5,^6,^1^5^3^21^*6,123^6,^1.^7^5^35^*6532^6,^1^5^3^21^*6,5,#437,05,^6,^1^2^3^6^5^2^3^6,^1'''
    # text = '70bpm\n1155665-4433221-5544332-5544332-1155665-4433221-'
    aa = TextToMidi(text)
    aa.make(velocity=127)
    print('Music Length: %.2f seconds' % aa.get_length())
    aa.save(r'D:\OneDrive\Projects\GocqTools\temp\new2.mid')
