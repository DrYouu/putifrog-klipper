A13-SOM
A13-SOM-1.jpeg A13-SOM-2.jpeg


A13-SOM-XXX features:

A13 Cortex-A8 CPU and Mali 400 GPU
256 or 512MB DDR3 RAM memory
Power supply managment
1x LCD connector
3x GPIO connectors
MicroSD card connector
DEBUG-UART connector for console debug with USB-SERIAL-CABLE-F
status LED
Power LED
RESET button
3.3V input power supply
PCB dimensions: 61 x 33 mm



Contents
1 Official Images from OLIMEX
1.1 Linux
2 A13-SOM-256
3 A13-SOM-512
3.1 Android
3.1.1 Android for NAND
3.1.2 Android for microSD card
4 Notable unofficial images
5 Documents
5.1 A13 Datasheet
5.2 A13 User Manual
6 Hardware
6.1 Power supply and consumption
6.2 Board dimensions
6.3 Schematic
6.4 Board Layout
7 Software
7.1 Linux Commands
7.2 Python
7.3 GPIO under Debian Linux
8 How To?
8.1 How to generate boot-able SD-card Debian Linux image for A13-SOM?
8.2 How do I write the Linux image to a micro SD card to use with my A13-SOM board?
8.3 How to change HDMI, VGA and LCD resolutions under Debian?
8.4 How to edit board configurations and definitions in the official Debian Linux?
8.5 How to properly calibrate a display under Debian
8.6 How to control PWM under Linux?
8.7 How to correctly power off OLinuXino running from NAND Flash
8.8 How to restore the Android image on NAND Flash
8.9 How to add STK1160 video capture driver support in Kernel 3.4
Official Images from OLIMEX
Linux
A13-SOM-256
Newest official Debian releases (recommended):

Direct FTP download location of Debian release #2: Debian 4GB SD-card image release 2 with hardware accelerated video and more

Build instructions for the latest image: https://github.com/OLIMEX/OLINUXINO/blob/master/SOFTWARE/A13/A13-SOM-build/A13_SOM_kernel_3.4.90_building_description_with_mainline_u-boot_2.txt

Older Debian releases (not recommended):

Direct download location of Debian release #1: A13-SOM-256 Debian 4GB SD-card image release-1 with hardware accelerated video and more

A13-SOM-512
Please note that the RAM memory of A13-SOM-512 was changed again in revision G to SAMSUNG K4B4G1646D-BYK0 (previously it used memories SAMSUNG K4B2G0846Q and even older hardware reviisons used HYNIX H5TQ2G83CFR, older boards might require older Linux images).

Newest official Debian releases (recommended):

Direct download of release 4 preliminary Linux image - suitable for boards with SAMSUNG K4B4G1646D-BYK0 DDR3 RAM memory: A13-SOM-512 Debian Linux with kernel 3.4.90+ in case of problems test with the previous release 3.

The build instructions for the latest Debian images might be found in this wiki article: building Debian for A13-SOM-256 and A13-SOM-512 (with support for HYNIX or SAMSUNG RAM memory)

Older Debian releases (not recommended):

Direct download of release 3 preliminary Linux image - suitable for boards with SAMSUNG K4B2G0846Q DDR3 RAM memory: A13-SOM-512 Debian Linux with kernel 3.4.90+ in case of problems test with the previous release 2.

Direct download location for Debian release 2 image - suitable for boards with SAMSUNG K4B2G0846Q DDR3 RAM memory: A13-SOM-512 Debian Linux with kernel 3.4.90+, suitable for boards with SAMSUNG DDR3 RAM

Direct download location for Debian release 1 - suitable for boards with HYNIX H5TQ2G83CFR DDR3 RAM memory: : A13-SOM-512 Debian Linux with kernel 3.4.90+, suitable for boards with HYNIX DDR3 RAM

The image features:

Linux Kernel 3.4.90+
LXDE desktop environment
Mplayer CLI
GCC 4.6
4.3"(480x272), 7"(800x480), 10" (1024x600) and 15.6" (1366x768) LCD and touchscreen support
GPIO
I2C
USB WIFI RTL8188CU, Ethernet AX88772B
dpkg
git
i2c-tools
perl
xorg
Python 2.7
USB-ETHERNET-AX88772B
MOD-WIFI-RTL8188
A13-LCD 4.3″TS 4.3″ LCD with backlight and touchscreen 480×272 pixels
A13-LCD7″TS 7″ LCD with backlight and touchscreen 800×480 pixels
A10-LCD10″TS 10.1″ LCD with backlight and touchscreen 1024×600 pixels
Micro SD card
OTG USB
HIGH SPEED HOST1 USB
I2C2(100KHz)
I2C1(100KHz)
Default Login: root/olimex

Tested board peripherals with this image:

GPIO - located at /sys/class/gpio
LCD - supported are A13-LCD4.3TS, A13-LCD7TS, A13-LCD10TS
Touch screen - you need calibrate LCD before using touch screen. Type: ts_calibrate and then test it with ts_test
ASIX 8877 USB-LAN - USB-ETHERNET-AX88772B
RTL8188CU - MOD-WIFI-RTL8188
USB_OTG - works as OTG device and Low/Full/High USB host
USB_HOST - works as Low/Full/High USB host
mico_SD_card - allow Linux boot
I2C2(100KHz) - /dev/i2c-2
I2C1(100KHz) - /dev/i2c-1

Note: the A13-SOM-Debian-SD card which we have in our web store contains the same image on 4GB Class10 fast micro SDcard, if you want to use this image please use card of Class10 speed or the performance of Linux will be very slow.

Note: in the previous Debian releases the Ethernet was auto-detected and initialized during boot BUT this was causing big delays in the start-up of the board if you didn't want to use Ethernet or if there wasn't Ethernet cable connected.

You can enable it by following these two steps:

1. To check under what name the LAN is associated write "ifconfig –a"

2. If, for example, it is under eth0 name, then write: "dhclient eth0"

This should enable the Ethernet and then SSH would also be available.

Android
The Android images are suitable only for the A13-SOM-512 version of the board (the 256 version of the board is not equipped with enough RAM to run Android smoothly). You can boot Android from SD card or the on-board NAND memory. However, in order to upload the Android to the NAND you would also need A13-SOM-WIFI-4GB (to extend the board with NAND flash memory).

The Android images don't have software buttons implemented, use the HOME/UBOOT button to navigate back if you are stuck in a menu and want to return to the main screen!

The board would enter "Sleep" mode after 30 minutes. If you wish to keep it awake start the AutoStartService application in the APPS section. You have to start it again after power down. You can try with other applications - keep alive and keep screen on applications from Google Play Store.

Android for NAND
Torrent of Android 4.2.2 release 1 for NAND memory with 720p HDMI and 800x480 (7 inch display) video support: A13-SOM-512 Android for NAND with HDMI and 7 inch display support

Torrent of Android 4.2.2 release 1 for NAND memory with 720p HDMI and 1024x600 (10 inch display) video support: ‎A13-SOM-512 Android for NAND with HDMI and 10 inch display support

The build instructions for the latest Android images might be found in this wiki article: building Android for A13-SOM-512 (with support for HYNIX or SAMSUNG RAM memory)

The image is with these features:

Android 4.2.2
NAND image will work only on A13-SOM-512+A13-SOM-WIFI-4GB
MicroSD card image will work on A13-SOM-512+A13-SOM-WIFI and A13-SOM-512+A13-SOM-WIFI-4GB
Different images support 7" LCD 800x480 pixels and 10" LCD 1024x600 pixels
Touchscreen supported
GPIO support
USB-Ethernet ASIX 88772
USB-WIFI RTL8188
USB-OTG support USB device and USB host with Low/Full/High speed
USB-HOST-top Low/Full/High speed
micro SD card
I2C1
I2C2
Buttons


Android for microSD card
Direct download for A13-SOM-512 Android 4.2.2 release 1 for microSD card with 800x480 (7 inch display) video support: A13-SOM-512 Android for microSD card 7 inch display support

Direct download for A13-SOM-512 Android release 1 for microSD card with 480x272 (4.3 inch display) video support: [Torrent A13-SOM-512 Android for microSD card 4.3 inch display support]

Extract and download the image the same way as Debian for microSD card (Win32DiskImager or "dd") as explained above.

Notable unofficial images
Below you would find locations to images released by the community. These are not officially supported by Olimex, however, some of these releases are pretty good and worth a try:

A13-SOM has support in armbian by Igor Pečovnik. The configuration might be found here: https://github.com/igorpecovnik/lib/tree/master/config/boards ; beginner help can be found in the documentation and in the forums: https://docs.armbian.com/


Documents
A13 Datasheet
A13 datasheet

A13 User Manual
A13 Users manual

Hardware
Power supply and consumption
If used as a stand-alone board A13-SOM can be powered from:

+3.3V power source, applied to GPIO-1 connector

Typical power consumption is as follows:

A13-SOM-512 + A13-SOM-WIFI-4GB running Debian - consumption: 0.45A @ 5V
A13-SOM-512 + A13-SOM-WIFI-4GB + A13-LCD7-TS running Debian - consumption: 0.75A @ 5V
A13-SOM-512 + A13-SOM-WIFI-4GB + A13-LCD7-TS running Android - consumption: 0.40A @ 5V

Additionally, if used together with A13-SOM-WIFI the whole setup can be powered from:

+5V via miniUSB cable, applied to USB_OTG connector
+5V power source, applied to the +5V pin near the red PWR_LED


Board dimensions
A13-SOM-XXX basic dimensions might be seen in the picture here: A13-SOM board dimensions

Schematic
A13-SOM-256/512 schemaitc is available at GitHub

A13-SOM-WIFI schematic and CAD files are at GitHub

The CAD product used to design A13-SOM-WIFI is Eagle and you can download evaluation free version from their web-site.

Board Layout
A13-SOM-512.png

Software
Linux Commands
Linux-Commands Brief Linux Command reference

Python
The Debian Linux Python package for A13-SOM is called pyA13SOM. It is installed in the default Debian image. More information and examples on how it can be used might be found here:

Link to pyA13SOM package at python.org

GPIO under Debian Linux
The GPIOs are defined in the script.bin of the Debian distribution. If you edit the script.bin you can change the names of the GPIOs. You can also remove the definitions for certain pins or add additional ones that we might have missed.

Inside the Debian Linux the GPIOs are located in /sys/class/gpio directory. Before using a GPIO you would need to export it.

There is an easy way to export all GPIOs:

 mount -t debugfs none /sys/kernel/debug
 for i in `seq 1 1 230`; do echo $i > /sys/class/gpio/export; done
To list all available GPIOs write:

 cat /sys/kernel/debug/gpio
This would return:

 gpio-1   (sysfs               ) in  hi
 gpio-2   (sysfs               ) in  hi
 gpio-3   (sysfs               ) out hi
 gpio-4   (sysfs               ) in  lo
 gpio-5   (sysfs               ) in  lo
 gpio-6   (sysfs               ) in  lo
 gpio-7   (sysfs               ) in  lo
 gpio-8   (sysfs               ) in  lo
 gpio-9   (sysfs               ) in  lo
 gpio-10  (sysfs               ) in  hi
 gpio-11  (sysfs               ) in  lo
 gpio-12  (sysfs               ) in  lo
 gpio-13  (sysfs               ) in  hi
 gpio-14  (sysfs               ) in  lo
The rest of the GPIOs have to be defined in the fex. Refer to this wiki article: how to edit board configurations and definitions

An example for a single port add is below (PB03):

   root@A13:~# echo 1 > /sys/class/gpio/export
to make PB03 output

   root@A13:~# echo out > /sys/class/gpio/gpio1_pb3/direction
to make PB03 high level(3.3V)

   root@A13:~# echo 1 > /sys/class/gpio/gpio1_pb3/value
to make PB03 low level(0V)

   root@A13:~# echo 0 > /sys/class/gpio/gpio1_pb3/value
note that:

There might be multiplexing on some of the pins especially if you are using a shield! Consider that when picking a GPIO. Refer to the schematics of the board and the shield for clearer view of the possible multiplexing locations.

How To?
How to generate boot-able SD-card Debian Linux image for A13-SOM?
The building instructions for the latest images might be found in this wiki article: building Debian for A13-SOM-256 and A13-SOM-512 (with support for XYNIX or SAMSUNG RAM memory)

Wordpress post on the building the previous (now outdated) Debian image (suitable only for boards with HYNIX memories, does not work properly with boards with SAMSUNG memories): wordpress post

How do I write the Linux image to a micro SD card to use with my A13-SOM board?
To write a Linux image to an SD card under Windows we use Win32 Disk Imager):

Download Win32 Disk Imager Win32 Disk Imager
Insert card
Start program
Select file
Click "write"
To write a Linux image to an SD card under Linux:

For instance you have an image with the file name of "debian_2g.img". It would be downloaded to the SD card connected to a Linux machine using one of the following commands:

# dd bs=4M oflag=sync if=debian_2g.img of=/dev/sdX
or

# cp debian_2g.img /dev/sdX
where X is the uSD card.

How to change HDMI, VGA and LCD resolutions under Debian?
The default SD card setup is made with settings for 7 inch LCD 800x480.

If you want to change to video output to other LCD (or in rare cases VGA) resolution under Debian then you have to start change_display.sh script file in /root directory.

For Linux Debian you would need to execute a shell script to be able to change the resolution. It is very good idea to use a serial cable for connection to the board from a personal computer since in this case you are dependent on a video resolution (a cable like USB-SERIAL-CABLE-F). If you want to change to some other LCD, VGA or HDMI resolution then you have to start change_display.sh script file in /root directory. When you are logged as super user in the board type:

  For Debian Wheezy releases: ./change_display* (* = press 'tab' to auto-complete)
  For Debian Jessie releases: change_display* (* = press 'tab' to auto-complete)
and press "Enter".

Note that the script should be executed as super user. Under the command line interface you are automatically logged as super user (user "root", password "olimex"). However, under the graphical environment you are not auto-logged as super user and you must type "sudo" before the command (in the GUI the super-user is "olimex" and the password is "olimex")

Choose the resolution and the interface (LCD or VGA). Note that VGA output is hard to implement and requires both additional hardware and good soldering experience. The supported resolutions are:

For LCD:

4.3" (480×272)
7" (800×480)
10" (1024×600)

For VGA (A13-SOM lacks VGA support on hardware level):

1680×1050
1440×900
1360×768
1280×1024
1024×768
800×600
640×480
1920×1080
1280×720


How to edit board configurations and definitions in the official Debian Linux?
There is a separate article on the subject here: editing the script.bin configurations

How to properly calibrate a display under Debian
If the problem is under Debian Linux make sure you are properly logged in the LXDE interface! Else applying calibration would not happen for the current user - if you are calibrating from the X graphical interface make sure that you are logged as user “olimex” (if calibrating without the X, the user is “root”).

  #su olimex
enter the olimex password:olimex

   #sudo ts_calibrate
calibrate the touch screen and reboot the board

   #sudo reboot
It would be a good idea to test with Android or another Debian image also, it has a built-in calibration application by default.

How to control PWM under Linux?
There is an article here: how to add pwm

How to correctly power off OLinuXino running from NAND Flash
In this blog post we explain what are the problems of sudden power down. This is common problem for all computers running an OS made specifically for handheld devices. Here you can read more about MLC NAND Flash and Linux file system.

How to restore the Android image on NAND Flash
Android corruption might happen if the A13-SOM-512 and A13-SOM-WIFI setup loses suddenly all power supply. In that case you can restore the Android image. Download an Android image from above (there are two images available one for 7 inch display and the other for 10 inch display), then follow the algorithm:

1. Install and run LiveSuit software (can be found here: [1]).

2. Go to “SelectImg” tab of the program and point to a valid Android image (the latest official one may also be downloaded above).

3. Disconnect the power supply and USB cable from the A13 board.

4. Press and hold HOME button, apply power supply 5V, release HOME button.

5. Connect USB cable to the mini USB connector.

6. You will be asked for drivers for the bootloader. Navigate to the folder where you extracted the LiveSuit and install the drivers from the respective executable (or manually point the installer to the drivers folder in the LiveSuit’s installation path).

7. LiveSuit will detect the board and would ask for the method of writing the image. Choose method of writing the image and confirm your wish to write the image.

8. Wait till upgrade succeeds

How to add STK1160 video capture driver support in Kernel 3.4
STK1160 driver backport by Dimitar Tomov

