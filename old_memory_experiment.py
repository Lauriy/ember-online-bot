import win32process
import win32ui
from _ctypes import byref
from ctypes import windll, c_char_p, c_ulong, c_int, create_string_buffer, cast
from ctypes.wintypes import LPVOID

#from win32con import PROCESS_ALL_ACCESS

#PROCESS_ALL_ACCESS = (0x000F0000L | 0x00100000L | 0xFFF)

PROCESS_ALL_ACCESS = 0x1F0FFF

class Memory:
    OpenProcess = windll.kernel32.OpenProcess
    ReadProcessMemory = windll.kernel32.ReadProcessMemory
    WriteProcessMemory = windll.kernel32.WriteProcessMemory
    CloseHandle = windll.kernel32.CloseHandle

    def __init__(self, pid):
        self.process_handle = self.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        self.buffer = c_char_p(b"data buffer")
        self.buffer_size = len(self.buffer.value)
        self.bytes_read = c_ulong(0)
        self.bytes_written = c_ulong(0)

    def read_app_base(self, address):
        app_base = c_int()
        self.ReadProcessMemory(self.process_handle, address, byref(app_base), 4, byref(self.bytes_read))

        return app_base.value


class EmberOnline:
    def __init__(self, memory):
        self.memory = memory
        self.base_pointer = 0x00000558
        self.app_base = self.memory.read_app_base(self.base_pointer)
        print self.app_base

# def read_process_memory(pid, address, offsets, size_of_data):
#     process_handle = windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
#     size_of_data = 4  # Size of your data
#     data = ""
#     read_buff = create_string_buffer(size_of_data)
#     count = c_ulong(0)
#     current_address = address
#     offsets.append(None)  # We want a final loop where we actually get the data out, this lets us do that in one go.
#     for offset in offsets:
#         if not windll.kernel32.ReadProcessMemory(process_handle, current_address, cast(read_buff, LPVOID), size_of_data,
#                                                  byref(count)):
#             return -1  # Error, so we're quitting.
#         else:
#             val = read_buff.value
#             result = int.from_bytes(val, byteorder='little')
#             # Here that None comes into play.
#             if (offset != None):
#                 current_address = result + offset
#             else:
#                 windll.kernel32.CloseHandle(process_handle)
#                 return result


def main():
    window_handle = win32ui.FindWindow(None, u"Ember Online - Lorkhan").GetSafeHwnd()
    pid = win32process.GetWindowThreadProcessId(window_handle)[1]

    print 'PID %i' % pid

    #print read_process_memory(pid, PROCESS_ALL_ACCESS, [0x418, 0x5E0, 0x600, 0x3F4], 4)


    memory = Memory(pid)
    ember = EmberOnline(memory)
    print ember.app_base
    # logic = Logic(hexagon)
    # logic.start()
    # memory.close_handle()


if __name__ == '__main__':
    main()
