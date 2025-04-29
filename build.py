from os import path, chdir, mkdir, makedirs, environ
from shutil import copy
from subprocess import run
from time import sleep

pico_sdk_path = environ.get("PICO_SDK_PATH")
pico_toolchain_path = environ.get("PICO_TOOLCHAIN_PATH")

if not pico_sdk_path or not pico_toolchain_path:
    if not pico_sdk_path:
        print(f"❌{' ' * 5}PICO_SDK_PATH chưa được thiết lập!")
    if not pico_toolchain_path:
        print(f"❌{' ' * 5}PICO_TOOLCHAIN_PATH chưa được thiết lập!")
    print(f"⚠️{' ' * 5}Vui lòng thiết lập các biến môi trường trước khi tiếp tục.")
    exit(1)
    
print(f"✅{' ' * 5}PICO_SDK_PATH: {pico_sdk_path}")
print(f"✅{' ' * 5}PICO_TOOLCHAIN_PATH: {pico_toolchain_path}")

PROJECT_DIR = "project"
BUILD_DIR = path.join(PROJECT_DIR, "build")
INCLUDE_DIR = path.join(PROJECT_DIR, "include")
SRC_DIR = path.join(PROJECT_DIR, "src")
CMAKE_FILE = path.join(PROJECT_DIR, "CMakeLists.txt")
UF2_FILE = path.join(BUILD_DIR, "os.uf2")

def create_project():
    if not path.exists(PROJECT_DIR):
        mkdir(PROJECT_DIR)
    makedirs(BUILD_DIR, exist_ok=True)
    makedirs(INCLUDE_DIR, exist_ok=True)
    makedirs(SRC_DIR, exist_ok=True)
    support_h_path = path.join(INCLUDE_DIR, "support.h")
    if not path.exists(support_h_path):
        with open(support_h_path, "w") as f:
            f.write("#ifndef SUPPORT_H\n#define SUPPORT_H\n\n// Add support functions here\n\n#endif")
    main_c_path = path.join(SRC_DIR, "main.c")
    if not path.exists(main_c_path):
        with open(main_c_path, "w") as f:
            f.write("""#include "pico/stdlib.h"

#define LED 25

int main() {
    gpio_init(LED);
    gpio_set_dir(LED, GPIO_OUT);
    while (true) {
        gpio_put(LED, 1);
        sleep_ms(500); 
        gpio_put(LED, 0);
        sleep_ms(500);
    }
    return 0;
}""")

    if not path.exists(CMAKE_FILE):
        with open(CMAKE_FILE, "w") as f:
            f.write("""cmake_minimum_required(VERSION 3.13)
include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)
project(project C CXX ASM)
set(PICO_NO_HARDWARE 1)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(os 
    src/main.c 
    # src/support.c
)
pico_enable_stdio_uart(project 1)
pico_enable_stdio_usb(project 0)
target_include_directories(os PRIVATE include)
target_link_libraries(os pico_stdlib)
target_compile_definitions(os PRIVATE LED_BUILTIN=25)
pico_add_extra_outputs(os)""")

def build():
    chdir(BUILD_DIR)
    print(f"🔨{' ' * 5}Running CMake...")
    run(["cmake", "..", "-G", "MinGW Makefiles"], check=True)
    print(f"⚙️{' ' * 5}Running Make...")
    run(["mingw32-make"], check=True)
    chdir("../..")

def RPI_RP2():
    print(f"🔍{' ' * 5}Searching for RPi-RP2 drive...")
    while True:
        for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            pico_index_file = f"{drive}:\\INDEX.HTM" 
            if path.exists(pico_index_file):
                print(f"✅{' ' * 5}Found RPi-RP2 at {drive}:\\")
                return f"{drive}:\\"
        print(f"⏳{' ' * 5}Waiting for Pico to enter boot mode...")
        sleep(1)

def flash():
    if not path.exists(UF2_FILE):
        print(f"❌{' ' * 5}UF2 file not found! Build might have failed.")
        return
    rpi_drive = RPI_RP2()
    target_file = path.join(rpi_drive, "firmware.uf2")
    print(f"🚀{' ' * 5}Flashing {UF2_FILE} -> {target_file}")
    copy(UF2_FILE, target_file)
    print(f"🎉{' ' * 5}Flashing complete! Pico will reboot.")

if __name__ == "__main__":
    create_project()
    build() 
    flash() 
