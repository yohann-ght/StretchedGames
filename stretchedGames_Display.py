import psutil
import time
import ctypes
import subprocess
from winotify import Notification

toast = Notification(
    app_id="Resolution Switcher without Display",
    title="Resolution Switcher without Display",
    msg="Le programme est démarré et fonctionne en arrière-plan."
)

toast.show()

GamePlaying = False
old_resolution = None
disabled_monitors = []
GUID_DEVCLASS_MONITOR = "{4D36E96E-E325-11CE-BFC1-08002BE10318}"


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

class DISPLAY_DEVICE(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_ulong),
        ("DeviceName", ctypes.c_wchar * 32),
        ("DeviceString", ctypes.c_wchar * 128),
        ("StateFlags", ctypes.c_ulong),
        ("DeviceID", ctypes.c_wchar * 128),
        ("DeviceKey", ctypes.c_wchar * 128),
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

def list_displays():
    user32 = ctypes.windll.user32

    i = 0

    while True:
        display = DISPLAY_DEVICE()
        display.cb = ctypes.sizeof(DISPLAY_DEVICE)

        result = user32.EnumDisplayDevicesW(
            None,
            i,
            ctypes.byref(display),
            0
        )

        if not result:
            break

        print("Nom :", display.DeviceName)
        print("Écran :", display.DeviceString)
        print("État :", display.StateFlags)
        print("----------------")

        i += 1

def list_monitors():

    result = subprocess.run(
        ["pnputil", "/enum-devices", "/class", "Monitor"],
        capture_output=True,
        text=True
    )

    lines = result.stdout.splitlines()

    current_id = None
    current_description = None
    active_monitors = []

    for line in lines:

        if "ID d'instance" in line:
            current_id = line.split(":", 1)[1].strip()

        if "Description de l'appareil" in line:
            current_description = line.split(":", 1)[1].strip()

        if "Statut" in line:
            status = line.split(":", 1)[1].strip()

            print(
                current_id,
                "->",
                current_description,
                "->",
                status
            )

            if status == "Début":
                active_monitors.append(current_id)

    print("Moniteurs actifs :", active_monitors)
    return active_monitors

def get_monitor_ids():
    result = subprocess.run(
        ["pnputil", "/enum-devices", "/class", "Monitor"],
        capture_output=True,
        text=True
    )

    lines = result.stdout.splitlines()

    monitors = []

    current_id = None
    current_description = None

    for line in lines:
        if "ID d'instance" in line:
            current_id = line.split(":", 1)[1].strip()

        if "Description de l'appareil" in line:
            current_description = line.split(":", 1)[1].strip()

        if "Statut" in line:
            status = line.split(":", 1)[1].strip()

            if status == "Début":
                monitors.append(current_id)
    return monitors

def disable_monitor(instance_id):
    print("AVANT pnputil")

    command = [
        "pnputil",
        "/disable-device",
        instance_id
    ]

    print("Lancement de pnputil...")

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )

        print("pnputil terminé")
        print("CODE :", result.returncode)
        print(result.stdout)
        print(result.stderr)

    except subprocess.TimeoutExpired:
        print("pnputil a dépassé les 10 secondes.")


def enable_monitor(instance_id):

    print("Je vais réactiver :", instance_id)

    command = [
        "pnputil",
        "/enable-device",
        instance_id
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=10

    )

    print("CODE :", result.returncode)
    print("SORTIE :")
    print(result.stdout)
    print("ERREUR :")
    print(result.stderr)

def list_active_displays():

    user32 = ctypes.windll.user32
    i = 0

    while True:

        display = DISPLAY_DEVICE()
        display.cb = ctypes.sizeof(DISPLAY_DEVICE)

        result = user32.EnumDisplayDevicesW(
            None,
            i,
            ctypes.byref(display),
            0
        )

        if not result:
            break

        if display.StateFlags & 0x1:

            print("DISPLAY :", display.DeviceName)
            print("Carte :", display.DeviceString)
            print("DeviceID :", display.DeviceID)

            monitor = DISPLAY_DEVICE()
            monitor.cb = ctypes.sizeof(DISPLAY_DEVICE)

            result_monitor = user32.EnumDisplayDevicesW(
                display.DeviceName,
                0,
                ctypes.byref(monitor),
                0
            )

            if result_monitor:
                print("MONITEUR :", monitor.DeviceString)
                print("MONITEUR ID :", monitor.DeviceID)

                if "ACR0752" in monitor.DeviceID:
                    print("=> Écran XF240Q S")

                elif "AUS23CC" in monitor.DeviceID:
                    print("=> Écran VZ239")

            print("----------------")

        i += 1

while True:

    find = False
    
    GAMES = [
        "cs2.exe",
        "VALORANT-Win64-Shipping.exe"
    ]

    for process in psutil.process_iter(["name"]):
        try:

            if process.info["name"] in GAMES:
                find = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if find and not GamePlaying:
        print(f"{process.info['name']} vient de se lancer !")

        active_monitors = get_monitor_ids()
        disabled_monitors = []

        for monitor in active_monitors:
            disable_monitor(monitor)
            disabled_monitors.append(monitor)

        print("Écrans désactivés :", disabled_monitors)

        old_resolution = get_current_resolution()
        print(f"Résolution originale : {old_resolution[0]}x{old_resolution[1]}")

        change_resolution()

        GamePlaying = True

    elif not find and GamePlaying:
        print("Le jeu vient de se fermer !")

        change_resolution(
            old_resolution[0],
            old_resolution[1]
        )

        for monitor in disabled_monitors:
            enable_monitor(monitor)

        disabled_monitors = []

        GamePlaying = False

    time.sleep(2)
