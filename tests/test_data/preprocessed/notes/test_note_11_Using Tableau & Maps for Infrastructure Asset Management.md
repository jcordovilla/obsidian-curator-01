---
title: Using Tableau & Maps for Infrastructure Asset Management
date created: '2017-02-01 14:32:25'
date modified: '2025-05-21 15:24:31'
language: en
source: https://blog.safe.com/2017/01/tableau-map-dashboards-infrastructure-asset-management/
tags:
- RISK
- TECHNOLOGY
- ABERTIS
- SOFTWARE
- ASSET-MANAGEMENT
author: Roger Aikema
publication_date: _January 4, 2017
---

Delivered by [FeedBurner](http://feedburner.google.com/)

[About FME](http://blog.safe.com/2017/01/tableau-map-dashboards-infrastructure-asset-management/#)    |   _January 4, 2017_   |   _By Roger Aikema_

# Using Tableau & Maps for Infrastructure Asset Management

[Tweet](https://twitter.com/intent/tweet?original_referer=http%3A%2F%2Fblog.safe.com%2F2017%2F01%2Ftableau-map-dashboards-infrastructure-asset-management%2F&ref_src=twsrc%5Etfw&text=Using%20Tableau%20%26%20Maps%20for%20Infrastructure%20Asset%20Management%3A&tw_p=tweetbutton&url=https%3A%2F%2Fblog.safe.com%2F2017%2F01%2Ftableau-map-dashboards-infrastructure-asset-management%2F)

_Today we welcome guest bloggers Henri Veldhuis and Jurgen van Tiggelen from [Sweco](http://www.sweco.nl/en). They will share what they’ve been able to accomplish in just a few short months, by using FME with Tableau to create map-based visualizations of infrastructure data. Sweco is Europe’s leading architecture and engineering consultancy with over 14,500 employees and projects in over 70 countries worldwide. Sweco has been a Safe Software Partner since 2005._

Sweco has been developing software for the maintenance of infrastructure and terrain for over 20 years. [Obsurv](http://www.obsurv.com/) system is used by organizations in The Netherlands for making an inventory of their assets (using GIS), for technical inspections and planning, and budgeting for maintenance. Assets which are typically managed with Obsurv include: roads, traffic systems, sewer systems, civil construction or trees and green areas.

## Tableau Dashboard for Decision Support

Inspired by a webinar from Safe about [preparing mapping data for Tableau](http://www.safe.com/webinars/how-prep-mapping-data-tableau-become-geographic-viz-wiz/), Sweco NL evaluated Tableau and got so enthusiastic about the possibilities that it immediately started using Tableau to create a dashboard. This dashboard supports a municipality’s decision-making process for the budgeting of road maintenance.

Since a budget is rarely sufficient to solve all of the needed maintenance, **this dashboard helps Sweco’s clients prioritize the part of the roads where risks are the highest due to the technical condition of the road**.

![[attachments/Using_Tableau_&_Maps_for_Infrastructure_Asset_Management.resources/Obsurv-Tableau-Dashboard-Powered-by-FME.png]]

Tableau dashboard with an analysis of risks based on the technical condition of the road.

## How the Data Is Prepared for Tableau

Sweco used formulas based on a research performed by Sweco and [Twente University](https://www.utwente.nl/en/) in The Netherlands. The original research was performed using calculations in Excel after exporting data from the user interface in Obsurv.

The power of [FME](https://www.safe.com/how-it-works/) is that it provides all the necessary tools to directly perform the calculations and transformations on data extracted from the database itself. Road managers can change their own parameters for the calculations using Excel. **This allows them to get the desired output for Tableau directly from FME Server, removing all the additional steps that were needed before.**

The SQLCreator and the AttributeManager in particular are powerful transformers for the FME workspace that powers the Tableau dashboards. These transformers provide the best access to all of the required data, and can make all the translations that are normally made in a complex application.

![[attachments/Using_Tableau_&_Maps_for_Infrastructure_Asset_Management.resources/Tableau-SQLCreator.png]]![[attachments/Using_Tableau_&_Maps_for_Infrastructure_Asset_Management.resources/Tableau-Database-Parameters.png]]

_Screenshots of the SQLCreator and AttributeManager transformers used by Sweco._

The [SQLCreator](http://www.safe.com/transformers/sql-creator/) allows us to get all the specific data from the database without having to read and join different tables with joiners or mergers. We can directly get the correct and filtered attributes by submitting the correct query.

Due to the fact that that the database works with Foreign keys and values that mostly do not mean anything to the user, we use the [AttributeManager](http://www.safe.com/transformers/attribute-manager/) to translate the values to meaningful information by using conditional values. This also prevents us from having to read in extra files that would translate these foreign keys to the correct parent code.

When all the translations are made, the rest of the FME workspace is mostly focused on performing all of the calculations. By using arithmetic editor and statistic calculator transformers within FME, all the formulas from the research are able to be used on the data.

## Visualizing the Output in Tableau

When this is done, all that’s left is creating the right output for Tableau. We choose Tableau because, in our opinion, it is simply the best tool to create dashboards that are clear and easy for customers to use, with an excellent spatial and non-spatial component.

Most other tools focus on the statistical output without a map. However, in our work-area maps provide very important data. They say: ‘’A picture is worth a thousand words’’, **we think a good map can say even more!**

_See also: Henri demos using the Microsoft HoloLens with Obsurv – [watch the video](https://www.youtube.com/watch?v=ZGmZrNcworo)._

![[attachments/Using_Tableau_&_Maps_for_Infrastructure_Asset_Management.resources/GIS-interface-Obsurv-with-analysis-created-with-FM.png]]

GIS interface Obsurv with the result of the analysis created with FME.

### More on Tableau and FME

* Tutorial: [Reprojection and Spatial Overlay for Tableau](https://knowledge.safe.com/articles/37691/reprojection-and-spatial-overlay-with-fme.html)

* Tool: [Shapefile to Tableau Free Online File Converter](http://www.safe.com/free-tools/shapefile-to-tableau/)
* Blog: [Importing Spatial Data into Tableau using FME](http://blog.safe.com/2016/08/importing-spatial-data-tableau-using-fme/)
* Webinar: [How to Prep Mapping Data for Tableau (Become a Geographic Viz Wiz!)](http://www.safe.com/webinars/how-prep-mapping-data-tableau-become-geographic-viz-wiz/)

## About the Authors

| ![[]] | _**Henri Veldhuis**<br>As Business Development Manager Henri is responsible for creating new business opportunities for Sweco in The Netherlands. He is also responsible for the development of Obsurv in the past and has introduced FME within the Sweco Netherlands organization. Creating simple intuitive software solutions for complex business / engineering requests is what drives him._ |
| ![[]] | _**Jurgen van Tiggelen**_<br>_Jurgen van Tiggelen has studied Geomatics and Physical Geography at the Lund University in Sweden. He now works as a software developer and consultant at Sweco in The Netherlands. His expertise lies especially in developing software on the Oracle platform (PL/SQL) and in combination with FME._ |

[![[attachments/Using_Tableau_&_Maps_for_Infrastructure_Asset_Management.resources/world-tour-2017-snippet.jpg]]](https://www.safe.com/worldtour/) FME World Tour 2017

Discover the magic of FME 2017 at a user meeting near you. Starting March 1, FME events will be happening in 70+ cities across the world. Register now to save your spot.

<https://www.safe.com/worldtour/>

### Related Posts

[![[attachments/Using_Tableau_&_Maps_for_Infrastructure_Asset_Management.resources/FME-Server-survey-2017.png]]](https://blog.safe.com/2017/01/2017-fme-server-customer-survey/)

### [FME Server 2017 – The Best Ever, Thanks To You!](https://blog.safe.com/2017/01/2017-fme-server-customer-survey/)

Hello again. I’m here to report how your feedback to Safe Software has helped us make FME Server 2017 the \[...\]

[![[attachments/Using_Tableau_&_Maps_for_Infrastructure_Asset_Management.resources/2017-Parameters-FeaturedImage.png]]](https://blog.safe.com/2017/01/fme2017-parameters-evangelist160/)

### [FME 2017 Sneak Peek: Parameters, Parameters, Parameters…](https://blog.safe.com/2017/01/fme2017-parameters-evangelist160/)

We've made quite a few improvements in 2017 to make it easier to access, set, and use different FME parameters. \[...\]

[![[attachments/Using_Tableau_&_Maps_for_Infrastructure_Asset_Management.resources/FME2017-featured.png]]](https://blog.safe.com/2017/01/whats-new-in-fme-2017-0-release-candidate-available/)

### [What’s New in FME 2017.0 (Release Candidate Available)](https://blog.safe.com/2017/01/whats-new-in-fme-2017-0-release-candidate-available/)

We’re doing something different this year. Those of you who like to open presents early will be thrilled. It’s a Release \[...\]

[![[attachments/Using_Tableau_&_Maps_for_Infrastructure_Asset_Management.resources/Marinah-Zhao.jpg]]](https://blog.safe.com/2017/01/my-co-op-term-at-safe-software/)

### [A Culture Built on Fun: My Co-Op Term at Safe Software](https://blog.safe.com/2017/01/my-co-op-term-at-safe-software/)

Co-op students have been an integral part of Safe Software for over 20 years, contributing to core FME technology and often returning as full-time \[...\]

[![[attachments/Using_Tableau_&_Maps_for_Infrastructure_Asset_Management.resources/FME-wine-featured.png]]](https://blog.safe.com/2016/12/fme-2017-we-will-ship-no-fme-before-its-time/)

### [FME 2017: We will ship no FME before its time](https://blog.safe.com/2016/12/fme-2017-we-will-ship-no-fme-before-its-time/)

It took Michelangelo 4 years to paint the ceiling in the Sistine Chapel. It took Beethoven 4 years to write \[...\]

## Leave a Reply

Your email address will not be published. Required fields are marked \*

Comment

Name \*

Email \*

Website