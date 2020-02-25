import os
import subprocess
import math


class ProxyConverter:
    def __init__(self, width=1920, height=1080):
        self.padding = False
        self.force_aspect = True
        self.width = width
        self.height = height


    def countFrames(self,input):

        framecounter = subprocess.Popen(f'mediainfo --Inform="Video;%Duration%,%FrameRate%" "{input}"',
                                        shell=True,
                                        bufsize=0,
                                        stdout=subprocess.PIPE
                                        ).stdout
        output = framecounter.read().decode("utf-8")
        length_in_ms, fps= (output.split(","))
        framecount = float(length_in_ms)/1000*float(fps)
        print(f"{framecount} frames counted")
        return framecount


    def process(self, input, output, signals, codec):
        print("Converting file: {}".format(input))
        signals.filename_signal.emit(os.path.basename(input))
        length = self.countFrames(input)

        if self.force_aspect:
            aspect_cmd = ':force_original_aspect_ratio=decrease'
            if self.padding:
                padding_cmd = f',pad={self.width}:{self.height}:(ow-iw)/2:(oh-ih)/2'
            else:
                padding_cmd = ''
        else:
            aspect_cmd = ''
            padding_cmd = ''

        if codec == "prores":
            codec_cmd = '-c:v "prores_ks" -profile:v 0 -pix_fmt yuv422p10'
        if codec == "h264":
            codec_cmd = '-c:v "libx264" -pix_fmt yuv420p'


        command = f'ffmpeg -n -hide_banner -loglevel error -stats -i "{input}" -vf "scale={self.width}:{self.height} {aspect_cmd} {padding_cmd}" -c:a copy {codec_cmd} "{output}"'

        result = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            encoding='utf-8',
            shell=True
        )

        for line in result.stdout:
            print((line))
            try:
                signals.progress_signal.emit(math.floor((float(line.strip().split()[1])/length)*100))
            except:
                # print error message
                signals.processed_signal.emit(line)
                return
        signals.processed_signal.emit(input)
        signals.count_signal.emit(None)
        signals.filename_signal.emit(None)
        signals.waiting_signal.emit(None)

    def make_folder(self, path, watchfolder, sorted_per_card):

        # Basefolder represents the first sub-directory in the path when we start looking from the watchfolder path
        base_folder = os.path.relpath(os.path.dirname(path), watchfolder)

        if base_folder != ".":  # When the bottom folder of path and watchfolder are the same it returns "."
            while os.path.split(base_folder)[0]:
                base_folder = os.path.split(base_folder)[0]
        else:
            base_folder = ""

        if sorted_per_card:
            proxy_folder = os.path.join(watchfolder,f"{base_folder}_PROXY")
        else:
            proxy_folder = f"{os.path.dirname(path)}{os.path.sep}PROXIES"
        # This is the folder where the proxies are placed
        if not os.path.exists(proxy_folder):
            print("Creating folder: {}".format(proxy_folder))
            os.makedirs(proxy_folder)
        return proxy_folder
