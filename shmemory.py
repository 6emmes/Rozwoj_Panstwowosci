import mmap
import os
import ctypes

class SimControl(ctypes.Structure):
    _fields_ = [
        ("roads_ready", ctypes.c_uint32),
    ]

class SharedControlBlock:
    def __init__(self, name, create=False):
        self.name = name
        self.size = ctypes.sizeof(SimControl)
        path = f"/dev/shm/{name}"

        if create:
            fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o666)
            os.ftruncate(fd, self.size)
        else:
            fd = os.open(path, os.O_RDWR)

        self.buf = mmap.mmap(fd, self.size, mmap.MAP_SHARED,
                             mmap.PROT_READ | mmap.PROT_WRITE)
        os.close(fd)

        self.ctrl = SimControl.from_buffer(self.buf)


class SharedMemoryGrid:
    def __init__(self, name, width, height, control_block=None, create=False):
        self.name = name
        self.width = width
        self.height = height
        self.count = width * height
        self.size = self.count * 4  # float32

        self.control = control_block

        path = f"/dev/shm/{name}"

        if create:
            fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o666)
            os.ftruncate(fd, self.size)
        else:
            fd = os.open(path, os.O_RDWR)

        self.buf = mmap.mmap(fd, self.size, mmap.MAP_SHARED,
                             mmap.PROT_READ | mmap.PROT_WRITE)
        os.close(fd)

        FloatArray = ctypes.c_float * self.count
        self.data = FloatArray.from_buffer(self.buf)
        self.set_ready_flag()

    # -----------------------------
    # Grid <-> Python sync
    # -----------------------------
    def sync_from_python_grid(self, grid2d):
        k = 0
        for row in grid2d:
            for v in row:
                self.data[k] = float(v)
                k += 1

    def sync_to_python_grid(self, grid2d):
        k = 0        # row-major
        for y in range(self.height):
            for x in range(self.width):
                grid2d[y][x] = self.data[k]
                k += 1

    # -----------------------------
    # Flag helpers
    # -----------------------------
    def set_ready_flag(self, flag_name="roads_ready"):
        if self.control is None:
            raise RuntimeError("No control block attached")
        setattr(self.control.ctrl, flag_name, 1)

    def clear_ready_flag(self, flag_name="roads_ready"):
        if self.control is None:
            raise RuntimeError("No control block attached")
        setattr(self.control.ctrl, flag_name, 0)

    def is_ready(self, flag_name="roads_ready"):
        if self.control is None:
            raise RuntimeError("No control block attached")
        return getattr(self.control.ctrl, flag_name) == 0
