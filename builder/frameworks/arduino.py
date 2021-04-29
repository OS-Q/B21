import os

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

board = env.BoardConfig()
build_mcu = env.get("BOARD_MCU", board.get("build.mcu", ""))

MCU_FAMILY = board.get(
    "build.system", "sam" if build_mcu.startswith("at91") else "samd")

if env.BoardConfig().get("build.core", "").lower() == "mbcwb":
    env.SConscript(
        os.path.join(env.PioPlatform().get_package_dir(
            "framework-arduino-mbcwb"), "tools", "platformio-samd-build.py"))
else:
    env.SConscript(os.path.join("arduino", "arduino-%s.py" % MCU_FAMILY))
