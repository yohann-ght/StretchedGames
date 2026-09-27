import psutil
import time
import ctypes
from winotify import Notification

toast = Notification(
    app_id="Resolution Switcher",
    title="Resolution Switcher",
    msg="Le programme est démarré et fonctionne en arrière-plan."
)

toast.show()

GamePlaying = False
old_resolution = None


class DEVMODE(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", ctypes.c_wchar * 32),
        ("dmSpecVersion", ctypes.c_ushort),
        ("dmDriverVersion", ctypes.c_ushort),
        ("dmSize", ctypes.c_ushort),
        ("dmDriverExtra", ctypes.c_ushort),
        ("dmFields", ctypes.c_ulong),
        ("dmPositionX", ctypes.c_long),
        ("dmPositionY", ctypes.c_long),
        ("dmDisplayOrientation", ctypes.c_ulong),
        ("dmDisplayFixedOutput", ctypes.c_ulong),
        ("dmColor", ctypes.c_short),
        ("dmDuplex", ctypes.c_short),
        ("dmYResolution", ctypes.c_short),
        ("dmTTOption", ctypes.c_short),
        ("dmCollate", ctypes.c_short),
        ("dmFormName", ctypes.c_wchar * 32),
        ("dmLogPixels", ctypes.c_ushort),
        ("dmBitsPerPel", ctypes.c_ulong),
        ("dmPelsWidth", ctypes.c_ulong),
        ("dmPelsHeight", ctypes.c_ulong),
        ("dmDisplayFlags", ctypes.c_ulong),
        ("dmDisplayFrequency", ctypes.c_ulong),
        ("dmICMMethod", ctypes.c_ulong),
        ("dmICMIntent", ctypes.c_ulong),
        ("dmMediaType", ctypes.c_ulong),
        ("dmDitherType", ctypes.c_ulong),
        ("dmReserved1", ctypes.c_ulong),
        ("dmReserved2", ctypes.c_ulong),
        ("dmPanningWidth", ctypes.c_ulong),
        ("dmPanningHeight", ctypes.c_ulong),
    ]


def get_current_resolution():
    user32 = ctypes.windll.user32

    dm = DEVMODE()
    dm.dmSize = ctypes.sizeof(DEVMODE)

    user32.EnumDisplaySettingsW(None, -1, ctypes.byref(dm))

    return dm.dmPelsWidth, dm.dmPelsHeight


def change_resolution(width=1440, height=1080):
    user32 = ctypes.windll.user32

    dm = DEVMODE()
    dm.dmSize = ctypes.sizeof(DEVMODE)

    user32.EnumDisplaySettingsW(None, -1, ctypes.byref(dm))

    dm.dmPelsWidth = width
    dm.dmPelsHeight = height
    dm.dmFields = 0x80000 | 0x100000

    result = user32.ChangeDisplaySettingsW(
        ctypes.byref(dm),
        0
    )

    if result == 0:
        print(f"Résolution changée : {width}x{height}")
    else:
        print("Impossible de changer la résolution.")


while True:

    find = False
    Games = [
        "FortniteClient-Win64-Shipping.exe",
        "Deceit2Game-Win64-Shipping.exe"
    ]

    for process in psutil.process_iter(["name"]):
        try:
            if process.info["name"] in Games:
                find = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if find and not GamePlaying:

        print(f"{process.info['name']}  vient de se lancer !")

        old_resolution = get_current_resolution()

        print(f"Résolution originale : {old_resolution[0]}x{old_resolution[1]}")

        change_resolution()

        GamePlaying = True

    elif not find and GamePlaying:

        print(f"{process.info['name']} vient de se fermer !")

        change_resolution(
            old_resolution[0],
            old_resolution[1]
        )

        GamePlaying = False

    time.sleep(2)