import serial
import subprocess
import psutil
import time
import sys
import GPUtil

os = ''

if sys.platform.startswith('win32'):
    os = 'windows'
    ser = serial.Serial('COM3')
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    range = volume.GetVolumeRange()
    # This scale comes from the code of WoolDoughnut310 on GitHub
    scale = {'100%': 0, '99%': -0.15066957473754883, '98%': -0.30284759402275085, '97%': -0.4565645754337311, '96%': -0.6118528842926025, '95%': -0.768743097782135,
               '94%': -0.9272695183753967, '93%': -1.0874667167663574, '92%': -1.2493702173233032, '91%': -1.4130167961120605, '90%': -1.5784454345703125,
               '89%': -1.7456932067871094, '88%': -1.9148017168045044, '87%': -2.08581280708313, '86%': -2.2587697505950928, '85%': -2.4337174892425537,
               '84%': -2.610703229904175, '83%': -2.7897727489471436, '82%': -2.970977306365967, '81%': -3.1543679237365723, '80%': -3.339998245239258,
               '79%': -3.527923583984375, '78%': -3.718202590942383, '77%': -3.9108924865722656, '76%': -4.1060566902160645, '75%': -4.3037590980529785,
               '74%': -4.5040669441223145, '73%': -4.707049369812012, '72%': -4.912779808044434, '71%': -5.121333599090576, '70%': -5.33278751373291,
               '69%': -5.547224998474121, '68%': -5.764730453491211, '67%': -5.98539400100708, '66%': -6.209307670593262, '65%': -6.436570644378662,
               '64%': -6.6672821044921875, '63%': -6.901548862457275, '62%': -7.1394829750061035, '61%': -7.381200790405273, '60%': -7.626824855804443,
               '59%': -7.876484394073486, '58%': -8.130311965942383, '57%': -8.388449668884277, '56%': -8.651047706604004, '55%': -8.918261528015137,
               '54%': -9.190258026123047, '53%': -9.46721076965332, '52%': -9.749302864074707, '51%': -10.036728858947754, '50%': -10.329694747924805,
               '49%': -10.62841796875, '48%': -10.933131217956543, '47%': -11.2440767288208, '46%': -11.561516761779785, '45%': -11.88572883605957,
               '44%': -12.217005729675293, '43%': -12.555663108825684, '42%': -12.902039527893066, '41%': -13.256492614746094, '40%': -13.61940860748291,
               '39%': -13.991202354431152, '38%': -14.372318267822266, '37%': -14.763236045837402, '36%': -15.164472579956055, '35%': -15.576590538024902,
               '34%': -16.000192642211914, '33%': -16.435937881469727, '32%': -16.884546279907227, '31%': -17.3467960357666, '30%': -17.82354736328125,
               '29%': -18.315736770629883, '28%': -18.824398040771484, '27%': -19.350669860839844, '26%': -19.895822525024414, '25%': -20.461252212524414,
               '24%': -21.048532485961914, '23%': -21.6594181060791, '22%': -22.295886993408203, '21%': -22.960174560546875, '20%': -23.654823303222656,
               '19%': -24.38274574279785, '18%': -25.147287368774414, '17%': -25.95233154296875, '16%': -26.80240821838379, '15%': -27.70285415649414,
               '14%': -28.66002082824707, '13%': -29.681535720825195, '12%': -30.77667808532715, '11%': -31.956890106201172, '10%': -33.23651123046875,
               '9%': -34.63383865356445, '8%': -36.17274856567383, '7%': -37.88519287109375, '6%': -39.81534194946289, '5%': -42.026729583740234,
               '4%': -44.61552047729492, '3%': -47.73759078979492, '2%': -51.671180725097656, '1%': -56.992191314697266, '0%': range[0]}
elif sys.platform.startswith('linux'):
    os = 'linux'
    ser = serial.Serial('/dev/ttyACM0')

from threading import Thread
from pynput.keyboard import *

print(ser.name)
ser.write(b'hello')

ns = True
interval = 0.1

keyboard = Controller()
mute_key = Key.pause

def toggle_audio(next_sink: bool) -> None:
    ''' This function toggles the audio output from one to the other.
        Currently only implemented in Linux '''
    
    if os == 'windows': return

    print('toggling audio to ' + str(int(next_sink)))
    i = 0
    stdout,stderr = subprocess.Popen(['pacmd', 'list-sink-inputs'],
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.STDOUT).communicate()

    input_sinks = []

    for line in stdout.strip().decode('utf-8').splitlines():
        if 'index' in line:
            input_sinks.append(''.join([i for i in line if i.isdigit()]))

    print(input_sinks)

    for i_s in input_sinks:
        subprocess.Popen(['pacmd', 'move-sink-input', i_s,
                         str(int(next_sink))], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.STDOUT).communicate()

    # Now we just have to set the default so all new sink inputs will go to the right
    # sink
    subprocess.Popen(['pacmd', 'set-default-sink', str(int(next_sink))])

def toggle_mute(mute) -> None:
    ''' Toggle the Discord mute key on or off; default off.'''
    if mute:
        # In this case, we are being told to mute
        keyboard.press(mute_key);
    else:
        # In this case, we are being told to unmute
        keyboard.release(mute_key)

def set_volume(v: str) -> None:
    ''' Sets the system volume to the input volume v percent.
        Currently only implemented in Windows. '''
    
    if os == 'linux': return
    volume.SetMasterVolumeLevel(float(scale.get(v + "%", "0")), None) 
    print("setting volume to " + str(v))

def update_cpu() -> bytes:
    ''' Returns cpu percent in bytes which can be read by the Arduino'''
    cpu_percent = psutil.cpu_percent()
    return 'c'.encode('UTF-8') + str(int(cpu_percent)).encode('UTF-8') \
           + '\n'.encode('UTF-8')


def update_ram() -> bytes:
    ''' Returns ram percent in bytes which can be read by the Arduino'''
    ram = psutil.virtual_memory()
    ram_percent = ram.percent
    return 'r'.encode('UTF-8') + str(int(ram_percent)).encode('UTF-8') \
           + '\n'.encode('UTF-8')


def update_gpu() -> bytes:
    ''' Returns gpu percent in bytes which can be read by the Arduino'''
    gpu = GPUtil.getGPUs()[0]
    gpu_percent = gpu.load * 100
    return 'g'.encode('UTF-8') + str(int(gpu_percent)).encode('UTF-8') \
           + '\n'.encode('UTF-8')

def update() -> None:
    ''' This function runs constantly to send all required outputs to
        the arduino '''
    while True:
        # Every half second, we will call all the functions that are
        # continuously writing to serial
        cpu_bytes = update_cpu()
        ram_bytes = update_ram()
        gpu_bytes = update_gpu()
        ser.write(cpu_bytes)
        ser.write(ram_bytes)
        ser.write(gpu_bytes)
        time.sleep(interval)

# We put the half-second update thread onto a different thread so that both update
# loops can run at the same time
Thread(target=update).start()

while True:
    # We will always be reading lines from serial
    try:
        s = ser.read_until().strip().decode("utf-8")
    except:
        print("cannot read serial this time, trying to restart serial connection")
        if os == 'windows':
            ser.close()
            ser = serial.Serial('COM3')
        elif os == 'linux':
            ser.close()
            ser = serial.Serial('/dev/ttyACM0')
    if s == 'audiotoggle':
        toggle_audio(ns)
        ns = not ns
    elif s == 'mute':
        toggle_mute(1)
        print("muting")
    elif s == 'unmute':
        toggle_mute(0)
        print("unmuting")
    #elif s[0] == 'v':
        #set_volume(s[1:])

    # We will also run all these functions who will write to serial
    # immediately (error lights, one time indicators, etc)


ser.close()
