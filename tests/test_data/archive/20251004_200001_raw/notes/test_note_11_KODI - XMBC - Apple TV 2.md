---
title: KODI - XMBC - Apple TV 2
date created: Sunday, December 10th 2017, 9:40:17 pm
date modified: Wednesday, May 21st 2025, 3:24:16 pm
language: en
---

# KODI - XMBC - Apple TV 2

Jailbreak con SeaOnPass

Terminal.app:

Conectamos con el apple tv:

ssh root@YOUR.ATV2.IP.ADDRESS

o bien usar 

ssh [root@apple-tv.loca](mailto:root@apple-tv.loca)l

Y después 1 a 1:

apt-get install wget

wget -O- http://apt.awkwardtv.org/awkwardtv.pub | apt-key add -

echo "deb http://apt.awkwardtv.org/ stable main" > /etc/apt/sources.list.d/awkwardtv.list

echo "deb http://mirrors.kodi.tv/apt/atv2 ./" > /etc/apt/sources.list.d/xbmc.list

apt-get update

apt-get install org.xbmc.kodi-atv2

reboot

Y ya está instalado KODI, la nueva versión de XMBC, media manager.

<http://www.a2z-support.com/kodi-on-apple-tv-2/>
