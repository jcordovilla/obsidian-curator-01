---
source: https://netosec.com/tethering-mobile-phone-to-home-network/
title: Tethering mobile phone to home network using ASUS router - NetOSec
date created: Friday, September 4th 2020, 11:31:15 am
date modified: Wednesday, May 21st 2025, 3:24:15 pm
language: en
---

[![[attachments/Tethering_mobile_phone_to_home_network_using_ASUS_router_-_NetOSec.resources/unknown_filename.4.png]]](https://netosec.com/)

* [Cyber Security](https://netosec.com/personal-cyber-security/)

* [Pen Testing](https://netosec.com/pen-testing/)
* [React SPA](https://alanocoder.com/blog/)
* [About](https://netosec.com/about-netosec/)

[Menu](https://netosec.com/tethering-mobile-phone-to-home-network/#)

# Tethering Mobile Phone to home Network Using ASUS Router

* [Alan Chan](https://netosec.com/author/actlc3388/)

* January 27, 2020

What happen when your home Internet is down and won’t be available for a while?

Internet has become part of our daily life. Many of our activities involve Internet access. From gaming, online shopping, banking, searching for information and etc. Simply put, it’s really inconvenience and tough when home Internet is not available.

I once had a power outage for several days because of a winter storm. Of course there were no Internet during power outage. The trouble was, there were still no Internet access after power was restored. And it would take ISP provider a week to have their technician came and restore the Internet. Those were the time when you realize how connected we are to the Internet. Without Internet, it has become a huge inconvenience and disrupting our daily routines.

## Tethering Mobile Phone to home Network

If you have unlimited data plan and strong signal with your mobile phone, it probably would be a great backup Internet connection for your home. What you need is a router that supports tethering mobile phone. With proper settings, your home network can then connect to this router instead of the ISP router and boom, your home network now has Internet access again.

For some, wireless Internet (using a hotspot wireless device from wireless carrier) may even be a viable option to serve as your primary home Internet connection. It all depends on the availability, pricing, signal strength and stability at your area.

The router I used is [ASUS WiFi Router RT-AC3200](https://www.amazon.com/Tri-Band-Lag-Free-AiProtection-security-RT-AC3200/dp/B00S9SGNNS/ref=sr_1_3?ie=UTF8&qid=1541594044&sr=8-3&keywords=rt-ac3200#customerReviews). It’s a solid router that serves me well mostly as a wireless access point for a couple years. And when needed, paired with my mobile phone to serves as a secondary Internet connection.

There are 2 ways to setup this router to provide Internet connection: usb tethering using router mode or hotspot connection using repeater mode.

Quick note: Wireless carriers may have restrictions on what protocols are allowed. Some services, especially those that require port forwarding may not be working properly.

## Preparation

You would need the latest firmware to have a stable connection and repeater mode method is only available with the latest firmware. Please update your ASUS router to latest firmware first, if needed, before proceeding.

We need a computer to connect to the ASUS router to configure the router. The default IP address of the router is 192.168.1.1. If the IP address is different, login to the router, and manually set the IP address back to 192.168.1.1.

Next is to set computer’s IP address manually to 192.168.1.100 so that they can communicate to each other.

* In windows 10, go to Windows Settings > Network & Internet > Change adapter options

* right click on the Ethernet adapter, then Properties
* select Internet Protocol Version 4 (TCP/IPv4) and click on Properties
* Set the static IP address as follow and the click OK.

![[attachments/Tethering_mobile_phone_to_home_network_using_ASUS_router_-_NetOSec.resources/unknown_filename.jpeg]]

Optionally, you can use the command ipconfig at a command prompt to verify that the network adapter is assigned the IP address 192.168.1.100 correctly. We can switch back to ‘Obtain an IP address automatically’ once the setup of the switch part is complete.

Both the router & the computer should be isolated from your home network now. Disconnect them from home network. Then connect the computer directly to this router and login to the router at 192.168.1.1

## Method 1: USB Tethering Using Wireless Router Mode

This method only works for android phones, doesn’t work for iPhones.

![[attachments/Tethering_mobile_phone_to_home_network_using_ASUS_router_-_NetOSec.resources/unknown_filename.3.jpeg]]

If the operation mode is already in ‘Wireless router’ mode, you can skip the next sub-section. Otherwise, we need to switch it to Wireless router mode first.

### Switch to Wireless Router Mode

* go to Administration > Operation Mode
* select ‘Wireless router mode’ radio button
* click ‘Save’
* wait for the router to update its settings
* login to the router again and it will do the ‘Quick Internet Setup’
* select No for ‘Does your Internet connection require user name and password?’ and click ‘Next’
* then select ‘Automatic IP’ and click ‘Next’
* Next is Wireless Setting. Just keep your previous settings or quickly enter one. click ‘Apply’ when done.
* Click ‘Complete’

Your router should now be in ‘Wireless router mode’ as shown below.

![[attachments/Tethering_mobile_phone_to_home_network_using_ASUS_router_-_NetOSec.resources/unknown_filename.5.jpeg]]

### Connecting the Mobile Phone

now connect your mobile phone to the top USB port of the ASUS router. Allow permission if your phone requests for permission. Now refresh the browser and your phone should show up as USB device. Turn on USB tethering at your phone.

![[attachments/Tethering_mobile_phone_to_home_network_using_ASUS_router_-_NetOSec.resources/unknown_filename.1.jpeg]]

* go to USB Application > 3G/4G > Internet Connection
* turn on ‘Enable USB Mode’
* select ‘Android phone’ for ‘Select USB Device’
* click ‘Apply’
* wait for Applying Settings and then login again.

The Secondary WAN should show as ‘Connected’ as shown.

![[attachments/Tethering_mobile_phone_to_home_network_using_ASUS_router_-_NetOSec.resources/unknown_filename.2.jpeg]]

## Method 2: Hotspot Using Repeater Mode

This method should work for both android & iPhone. Turn on mobile hotspot on your cell phone first.

* go to Administration > Operation Mode
* select ‘Repeater mode’ radio button
* a list of available SSIDs should appear. select your mobile hotspot.
* enter the mobile hotspot’s password, then click ‘Connect’
* ‘LAN IP Setting’ screen will show up. Let it obtain info automatically. Simply click ‘Next’.
* Next is Wireless Setting. Just use default settings or quickly enter one. click ‘Apply’ when done.
* wait for the router to connect to the hotspot

![[attachments/Tethering_mobile_phone_to_home_network_using_ASUS_router_-_NetOSec.resources/unknown_filename.6.jpeg]]

Once the router finished connecting, your computer should be able to connect to the Internet. However, the router will obtain a different IP address from the mobile hotspot. As a result, you would need to find the IP address in order to connect to the router’s configuration webpage. For android, you can find the router’s IP address at the cell phone hotspot’s connected device. For iPhone, however, there’s no information about that. You would need to use a network scanner or [ASUS device discovery utility](https://www.asus.com/us/Networking/RTAC3200/HelpDesk_Download/). Or when you disconnect the mobile hotspot, the router will reset it’s IP address to 192.168.1.1.

### You Might Also Like

### [8 tips to make your home router more secure](https://netosec.com/make-router-more-secure/)

May 17, 2019

### [Testing ethernet cable](https://netosec.com/testing-ethernet-cable/)

October 29, 2019

### [Setup VLAN subnets for home network](https://netosec.com/home-network-vlans/)

January 29, 2019

### Leave a Reply

	

* <https://twitter.com/share?text=Tethering%20mobile%20phone%20to%20home%20network%20using%20ASUS%20router&url=https://netosec.com/tethering-mobile-phone-to-home-network/>

* <https://www.facebook.com/sharer.php?u=https://netosec.com/tethering-mobile-phone-to-home-network/>

#### Popular Posts

* [Protect home network using subnets with pfSense](https://netosec.com/protect-home-network/)

* [Setup VLAN subnets for home network](https://netosec.com/home-network-vlans/)
* [Tethering mobile phone to home network using ASUS router](https://netosec.com/tethering-mobile-phone-to-home-network/)
* [Setup Wi-Fi VLAN subnets for home network](https://netosec.com/home-network-wi-fi-vlans/)
* [Guide to install pfSense 2.4.4 using flash drive](https://netosec.com/install-pfsense-flash-drive/)
* [Setup Wi-Fi VLANs with DD-WRT on RT-AC3200](https://netosec.com/dd-wrt-wifi-vlans/)
* [pWnOS – vulnhub walkthrough](https://netosec.com/pwnos-vulnhub-walkthrough/)
* [My journey to pass OSCP in 3 months](https://netosec.com/my-journey-through-oscp/)

#### Recent Posts

* [How to turn off all RGB lights on my 3700X PC build](https://netosec.com/how-to-turn-off-all-rgb-lights-on-my-3700x-pc-build/)

* [Ryzen 7 3700X $2K Build with Asus TUF Gaming X570-Plus](https://netosec.com/ryzen-7-3700x-build-with-asus-tuf-gaming-x570-plus/)
* [Jarvis – HackTheBox writeup](https://netosec.com/jarvis-hackthebox-writeup/)
* [Continuous Deployment using AWS CodeBuild with CDK for Next.js](https://netosec.com/continuous-deployment-using-aws-codebuild-with-cdk-for-next-js/)
* [Mirai – HackTheBox writeup](https://netosec.com/mirai-hackthebox-writeup/)
* [Deploying Static React Next.js to AWS S3](https://netosec.com/deploying-static-react-nextjs-to-aws-s3/)
* [Setup on-premise NFS file share using AWS File Gateway](https://netosec.com/setup-nfs-share-aws-file-gateway/)
* [Migrating React SPA from .NET Core to Next.js](https://netosec.com/migrating-react-spa-from-net-core-to-next-js/)

#### HackTheBox Writeups

* [Jarvis – HackTheBox writeup](https://netosec.com/jarvis-hackthebox-writeup/)

* [Mirai – HackTheBox writeup](https://netosec.com/mirai-hackthebox-writeup/)
* [Writeup – HackTheBox writeup](https://netosec.com/writeup-hackthebox-writeup/)
* [Irked – HackTheBox writeup](https://netosec.com/irked-hackthebox-writeup/)
* [SwagShop – HackTheBox writeup](https://netosec.com/swagshop-hackthebox-writeup/)
* [Jeeves – HackTheBox writeup](https://netosec.com/jeeves-hackthebox-writeup/)
* [Bitlab – HackTheBox writeup](https://netosec.com/bitlab-hackthebox-writeup/)
* [Craft – HackTheBox writeup](https://netosec.com/craft-hackthebox-writeup/)

#### Vulnhub Walkthrough

* [Jarbas 1 – vulnhub walkthrough](https://netosec.com/jarbas-1-vulnhub-walkthrough/)

* [Dina 1.0.1 – vulnhub walkthrough](https://netosec.com/dina-101-vulnhub-walkthrough/)
* [Kioptrix Level 1 – vulnhub walkthrough](https://netosec.com/kioptrix-level-1-vulnhub/)
* [Tr0ll 1 – vulnhub walkthrough](https://netosec.com/tr0ll-1-vulnhub-walkthrough/)
* [pWnOS – vulnhub walkthrough](https://netosec.com/pwnos-vulnhub-walkthrough/)
* [Holynix v1 – vulnhub walkthrough](https://netosec.com/holynix-v1-vulnhub-walkthrough/)
* [Reset Linux root password using Kali live](https://netosec.com/reset-linux-root-password/)
* [LAMPSecurity: CTF5 – vulnhub walkthrough](https://netosec.com/lampsecurity-ctf5-vulnhub-walkthrough/)
<https://netosec.com/tethering-mobile-phone-to-home-network/#>
[Close Menu](https://netosec.com/tethering-mobile-phone-to-home-network/#)

[Close Menu](https://netosec.com/tethering-mobile-phone-to-home-network/#)

* [Cyber Security](https://netosec.com/personal-cyber-security/)

* [Pen Testing](https://netosec.com/pen-testing/)
* [React SPA](https://alanocoder.com/blog/)
* [About](https://netosec.com/about-netosec/)
