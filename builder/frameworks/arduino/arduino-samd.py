import os

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

VENDOR_CORE = board.get("build.core", "").lower()

framework_package = "framework-arduino-samd"
if VENDOR_CORE != "arduino":
    framework_package += "-%s" % VENDOR_CORE
FRAMEWORK_DIR = platform.get_package_dir(framework_package)
CMSIS_DIR = platform.get_package_dir("framework-cmsis")
CMSIS_ATMEL_DIR = platform.get_package_dir("framework-cmsis-atmel")

assert all(os.path.isdir(d) for d in (FRAMEWORK_DIR, CMSIS_DIR, CMSIS_ATMEL_DIR))

env.SConscript("arduino-common.py")

BUILD_CORE = "arduino"
if VENDOR_CORE == "sparkfun" and board.get("build.mcu", "").startswith("samd51"):
    BUILD_CORE = "arduino51"

env.Append(
    CPPDEFINES=[
        "ARDUINO_ARCH_SAMD"
    ],

    CPPPATH=[
        os.path.join(
            CMSIS_DIR,
            "CMSIS",
            os.path.join("Core", "Include") if VENDOR_CORE in ("adafruit", "seeed") else "Include",
        ),  # Adafruit and Seeed cores use CMSIS v5.4 with different folder structure
        os.path.join(CMSIS_ATMEL_DIR, "CMSIS", "Device", "ATMEL"),
        os.path.join(FRAMEWORK_DIR, "cores", BUILD_CORE)
    ],

    LIBPATH=[
        os.path.join(CMSIS_DIR, "CMSIS", "Lib", "GCC"),
    ],

    LINKFLAGS=[
        "--specs=nosys.specs",
        "--specs=nano.specs"
    ]
)

if board.get("build.cpu") == "cortex-m4":
    env.Prepend(
        CCFLAGS=[
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16"
        ],

        LINKFLAGS=[
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16"
        ],

        LIBS=["arm_cortexM4lf_math"]
    )
else:
    env.Prepend(
        LIBS=["arm_cortexM0l_math"]
    )

if VENDOR_CORE in ("seeed", "adafruit", "moteino"):
    env.Append(
        CPPDEFINES=[
            ("USB_CONFIG_POWER", board.get("build.usb_power", 100))
        ],

        CCFLAGS=[
            "-Wno-expansion-to-defined"
        ],

        CPPPATH=[
            os.path.join(FRAMEWORK_DIR, "cores", BUILD_CORE, "TinyUSB"),
            os.path.join(FRAMEWORK_DIR, "cores", BUILD_CORE, "TinyUSB",
                "Adafruit_TinyUSB_ArduinoCore"),
            os.path.join(FRAMEWORK_DIR, "cores", BUILD_CORE, "TinyUSB",
                "Adafruit_TinyUSB_ArduinoCore", "tinyusb", "src")
        ]
    )

    if VENDOR_CORE in ("adafruit", "seeed"):
        env.Append(CPPPATH=[os.path.join(CMSIS_DIR, "CMSIS", "DSP", "Include")])

#
# Vendor-specific configurations
#

if VENDOR_CORE == "moteino":
    env.Append(
        CPPDEFINES=[
            "ARM_MATH_CM0PLUS"
        ]
    )
elif VENDOR_CORE == "seeed":
    env.Append(
        LINKFLAGS=[
            "-Wl,--wrap,_write",
            "-u", "__wrap__write"
        ]
    )
elif VENDOR_CORE == "arduino":
    env.Prepend(
        CPPPATH=[
            os.path.join(FRAMEWORK_DIR, "cores", BUILD_CORE, "api", "deprecated"),
            os.path.join(FRAMEWORK_DIR, "cores", BUILD_CORE, "api", "deprecated-avr-comp")
        ]
    )

env.Append(
    ASFLAGS=env.get("CCFLAGS", [])[:],
)

#
# Target: Build Core Library
#

libs = []

if "build.variant" in board:
    variants_dir = os.path.join(
        "$PROJECT_DIR", board.get("build.variants_dir")) if board.get(
            "build.variants_dir", "") else os.path.join(FRAMEWORK_DIR, "variants")

    env.Append(
        CPPPATH=[os.path.join(variants_dir, board.get("build.variant"))]
    )
    libs.append(env.BuildLibrary(
        os.path.join("$BUILD_DIR", "FrameworkArduinoVariant"),
        os.path.join(variants_dir, board.get("build.variant"))
    ))

libs.append(env.BuildLibrary(
    os.path.join("$BUILD_DIR", "FrameworkArduino"),
    os.path.join(FRAMEWORK_DIR, "cores", BUILD_CORE)
))

env.Prepend(LIBS=libs)
