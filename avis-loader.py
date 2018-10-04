#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import ConfigParser
import os
import psycopg2
import datetime
import re
import sys

config = ConfigParser.RawConfigParser()
config.read("avis-loader-config-test.cfg")

newspaperLocation = config.get("loader-config", "newspaperLocation")
dbname = config.get("db-config", "dbname")
dbuser = config.get("db-config", "user")
dbhost = config.get("db-config", "host")
dbpassword = config.get("db-config", "password")

filePatterns = config.items(sys.argv[1])

def storeFjerritslevPdfValues(path, deliveryDate):
  _,date,_,sectionTitle,pageAndFormat = os.path.basename(path).split("_")
  page,fileFormat = pageAndFormat.split(".")
  pageNumber = page.replace("-","")
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = "fjerritslevavis"
  newspaperTitle = "Fjerritslev Avis"
  editionTitle = "0"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeFjerritslevTiffValues(path, deliveryDate):
  date,_,sectionTitle,pageAndFormat = os.path.basename(path).split("_")
  page,fileFormat = pageAndFormat.split(".")
  pageNumber = page.replace("-","")
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = "fjerritslevavis"
  newspaperTitle = "Fjerritslev Avis"
  editionTitle = "0"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeBorsenValues(path, deliveryDate):
  date,pageAndFormat = os.path.basename(path).split("_")
  pageNumber,fileFormat = pageAndFormat.split(".")
  pageNumber = pageNumber.replace("-","")
  year,month,day = date.split("-")
  newspaperId = "boersen"
  newspaperTitle = "Børsen"
  editionTitle="0"
  sectionTitle = "Main"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeBorsenPdfValues3(path, deliveryDate):
  year,month,day,pageAndFormat = os.path.basename(path).split("_")
  date = year + "-" + month + "-" + day
  pageNumber,fileFormat = pageAndFormat.split(".")
  pageNumber = pageNumber.replace("-","")
  newspaperId = "boersen"
  newspaperTitle = "Børsen"
  editionTitle="0"
  sectionTitle = "Main"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeBorsenPdfValues4(path, deliveryDate):
  dateEtc,fileFormat = os.path.basename(path).split(".")
  year = dateEtc[0:4]
  month = dateEtc[4:6]
  day = dateEtc[6:8]
  sectionTitle = dateEtc[8:-3]
  pageNumber = dateEtc[-3:]

  date = year + "-" + month + "-" + day
  newspaperId = "boersen"
  newspaperTitle = "Børsen"
  editionTitle="0"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeBorsenPdfValues5(path, deliveryDate):
  dateEtc,fileFormat = os.path.basename(path).split(".")
  year = dateEtc[0:4]
  month = dateEtc[4:6]
  day = dateEtc[10:12]
  editionTitle = dateEtc[8:10]
  sectionTitle = dateEtc[12:-3]
  pageNumber = dateEtc[-3:]

  date = year + "-" + month + "-" + day
  newspaperId = "boersen"
  newspaperTitle = "Børsen"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeBorsenBrikValues(path, deliveryDate):
  _,_,_,year,monthAndDay,_ = path.split("/")
  if "-" in monthAndDay:
    month,day=monthAndDay.split("-")
  else:
    month=monthAndDay
    day="01"
  date=year+"-"+month+"-"+day

  filenameWithExtension = os.path.basename(path)
  filename,fileFormat = filenameWithExtension.split(".")
  if "_" in filename:
    editionTitle,pageNumber = filename.split("_")
  else:
    pageNumber = "0"
    editionTitle = filename

  singlePage=True
  newspaperId = "boersen"
  newspaperTitle = "Børsen"
  pageLabel = "Brik"
  sectionTitle = ""
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, singlePage, pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate, side_label=pageLabel)

def storeBorsenBagsidePdfValues(path, deliveryDate):
  filenameWithExtension = os.path.basename(path)
  filename,fileFormat = filenameWithExtension.split(".")
  year = filename[0:4]
  month = filename[4:6]
  day = filename[6:8]
  sectionTitle = filename[8:-7]
  pageNumber = "0"

  date = year + "-" + month + "-" + day
  singlePage=True
  newspaperId = "boersen"
  newspaperTitle = "Børsen"
  pageLabel = "Bagside"
  editionTitle = "0"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, singlePage, pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate, side_label=pageLabel)

def storeBorsenSpecialPdfValues(path, deliveryDate):
  filenameWithExtension = os.path.basename(path)
  filename,fileFormat = filenameWithExtension.split(".")
  year = filename[0:4]
  month = filename[4:6]
  day = filename[6:8]
  sectionTitle = filename[17:]
  pageNumber = "0"

  date = year + "-" + month + "-" + day
  singlePage=False
  newspaperId = "boersen"
  newspaperTitle = "Børsen"
  editionTitle = "0"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, singlePage, pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeBorsenBrikJp2Values(path, deliveryDate):
  _,_,year,monthAndDay,_,_ = path.split("/")
  if "-" in monthAndDay:
    month,day=monthAndDay.split("-")
  else:
    month=monthAndDay
    day="01"
  date=year+"-"+month+"-"+day

  filenameWithExtension = os.path.basename(path)
  filename,fileFormat = filenameWithExtension.split(".")
  if "_" in filename:
    editionTitle,pageNumber = filename.split("_")
  else:
    pageNumber = "0"
    editionTitle = filename

  singlePage=True
  newspaperId = "boersen"
  newspaperTitle = "Børsen"
  pageLabel = "Brik"
  sectionTitle = ""
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, singlePage, pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate, side_label=pageLabel)

def storeFrederikshavnTiffValues(path, deliveryDate, fraktur="false"):
  filename,fileFormat = os.path.basename(path).split(".")
  date,_,sectionTitle,page = filename.split("_")
  pageNumber = page.replace("-","")
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = "frederikshavnsavis"
  newspaperTitle = "Frederikshavns Avis"
  editionTitle = "0"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate, fraktur=fraktur)

def storeFrederikshavnPdfValues(path, deliveryDate):
  filename,fileFormat = os.path.basename(path).split(".")
  _,date,_,sectionTitle,page = filename.split("_")
  page = page.replace("-","")
  page = page.replace("M","")
  pageNumber = page.replace("T","")
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = "frederikshavnsavis"
  newspaperTitle = "Frederikshavns Avis"
  editionTitle = "0"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeKristeligtDagbladPdfValues(path, deliveryDate):
  filename = os.path.basename(path)[0:-4]
  fileFormat = os.path.basename(path)[-3:]
  _,date,editionTitle,sectionTitle,page = filename.split("_")
  page = page.replace("-","")
  page = page.replace("M","")
  page = page.replace("T","")
  pageNumber = page.replace("E","")
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = "kristeligtdagblad"
  newspaperTitle = "Kristeligt Dagblad"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeKristeligtDagbladTiffValues(path, deliveryDate):
  filename,fileFormat = os.path.basename(path).split(".")
  date,editionTitle,sectionTitle,page = filename.split("_")
  pageNumber = page.replace("-", "")
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = "kristeligtdagblad"
  newspaperTitle = "Kristeligt Dagblad"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeLogstorTiffValues(path, deliveryDate, fraktur="false"):
  filename,fileFormat = os.path.basename(path).split(".")
  date,_,sectionTitle,page = filename.split("_")
  pageNumber = page.replace("-","")
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = "loegstoeravis1882"
  newspaperTitle = "Løgstør Avis"
  editionTitle = "0"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate, fraktur=fraktur)

def storeLogstorPdfValues(path, deliveryDate):
  filename,fileFormat = os.path.basename(path).split(".")
  _,date,_,sectionTitle,page = filename.split("_")
  page = page.replace("-","")
  page = page.replace("M","")
  pageNumber = page.replace("T","")
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = "loegstoeravis1882"
  newspaperTitle = "Løgstør Avis"
  editionTitle = "0"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeFlensborgJp2Values(path, deliveryDate):
  filename,fileFormat = os.path.basename(path).split(".")
  _,date,sectionNumberEtc,sectionTitle,page = filename.split("_")
  sectionNumber = sectionNumberEtc[0:1]
  sectionTitle = sectionTitle + sectionNumber
  pageNumber = page.replace("-","")
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = "flensborgavis"
  newspaperTitle = "Flensborg Avis"
  editionTitle = "0"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeFlensborgJp2Values2(path, deliveryDate):
  filename,fileFormat = os.path.basename(path).split(".")
  date,sectionNumberEtc,sectionTitle,page = filename.split("_")
  sectionNumber = sectionNumberEtc[0:1]
  sectionTitle = sectionTitle + sectionNumber
  pageNumber = page.replace("-","")
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = "flensborgavis"
  newspaperTitle = "Flensborg Avis"
  editionTitle = "0"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeFlensborgJp2Values4(path, deliveryDate):
  filename,fileFormat = os.path.basename(path).split(".")
  _,date,_,sectionAndpage = filename.split("_")
  sectionTitle = sectionAndpage[0:1]
  pageNumber = sectionAndpage[1:]
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = "flensborgavis"
  newspaperTitle = "Flensborg Avis"
  editionTitle = "0"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeFlensborgPdfValues(path, deliveryDate):
  filename = os.path.basename(path)[0:-4]
  fileFormat = os.path.basename(path)[-3:]
  _,date,sectionTitle,_,pageNumber = filename.split("_")
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = "flensborgavis"
  newspaperTitle = "Flensborg Avis"
  editionTitle = "0"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeFlensborgPdfValues2(path, deliveryDate):
  filename = os.path.basename(path)[0:-4]
  fileFormat = os.path.basename(path)[-3:]
  _,date,sectionTitle,sectionNumber,pageNumber = filename.split("_")
  sectionTitle = sectionTitle + sectionNumber
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = "flensborgavis"
  newspaperTitle = "Flensborg Avis"
  editionTitle = "0"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeSudschleswigscheJp2Values(path, deliveryDate):
  filename,fileFormat = os.path.basename(path).split(".")
  _,date,_,sectionTitle,pageNumber = filename.split("_")
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = "suedschleswigscheheimatzeitung"
  newspaperTitle = "Südschleswigsche Heimat-Zeitung"
  editionTitle = "0"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/eb_hnas/2016/02/19/EKS20160219L11A039.pdf
def storeEkstrabladetHnasPdfValues(path, deliveryDate):
  filename,fileFormat = os.path.basename(path).split(".")
  year = filename[3:7]
  month = filename[7:9]
  day = filename[9:11]
  date = year + "-" + month + "-" + day
  sectionTitle = filename[-4:-3]
  pageNumber = filename[-3:]
  newspaperId = "ekstrabladet"
  newspaperTitle = "Ekstra Bladet"
  editionTitle = filename[12:13]
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/eb_hnas/2014/11/27/EKS20141127L12017..pdf
def storeEkstrabladetHnasPdfValues3(path, deliveryDate):
  fileFormat = os.path.basename(path)[-3:]
  filename = os.path.basename(path)[:-5]
  year = filename[3:7]
  month = filename[7:9]
  day = filename[9:11]
  date = year + "-" + month + "-" + day
  sectionTitle = "unknown"
  pageNumber = filename[-3:]
  newspaperId = "ekstrabladet"
  newspaperTitle = "Ekstra Bladet"
  editionTitle = filename[12:13]
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/eb_hnas/2006/02/19/1_SEKTION/45.pdf
def storeEkstrabladetHnasPdfValuesSEKTION(path, deliveryDate):
  vest = "/VEST" in path or "/Vest" in path
  augmentedPath = path.replace("/VEST", "")
  augmentedPath = augmentedPath.replace("/Vest", "")
  _,_,year,month,day,sectionTitle,file = augmentedPath.split("/")
  sectionTitle = sectionTitle[:1]
  pageNumber,fileFormat = file.split(".")
  date = year + "-" + month + "-" + day
  newspaperId = "ekstrabladet"
  newspaperTitle = "Ekstra Bladet"
  editionTitle = "1"
  if vest:
    editionTitle = editionTitle + "(VEST)"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/eb_hnas/2006/02/02/9_UDGAVE/1_SEKTION/2.pdf
def storeEkstrabladetHnasPdfValuesUDGAVE(path, deliveryDate):
  vest = "/VEST" in path
  augmentedPath = path.replace("/VEST", "")
  _,_,year,month,day,editionTitle,sectionTitle,file = augmentedPath.split("/")
  sectionTitle = sectionTitle[:1]
  pageNumber,fileFormat = file.split(".")
  date = year + "-" + month + "-" + day
  newspaperId = "ekstrabladet"
  newspaperTitle = "Ekstra Bladet"
  editionTitle = editionTitle[:1]
  if vest:
    editionTitle = editionTitle + "(VEST)"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/eb_ocr01/e1932.08.31/e1932.08.31_0003.pdf
def storeEkstrabladetOcrPdfValues(path, deliveryDate):
  filename = os.path.basename(path)[:-4]
  fileFormat = os.path.basename(path)[-3:]
  year = filename[1:5]
  month = filename[6:8]
  day = filename[9:11]
  date = year + "-" + month + "-" + day
  sectionTitle = "A"
  pageNumber = filename[-3:]
  newspaperId = "ekstrabladet"
  newspaperTitle = "Ekstra Bladet"
  editionTitle = "1"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/eb_ocr01/e1915.06.29/e1915.06.29-a_0002.pdf
def storeEkstrabladetOcrPdfValues2(path, deliveryDate):
  filename = os.path.basename(path)[:-4]
  fileFormat = os.path.basename(path)[-3:]
  year = filename[1:5]
  month = filename[6:8]
  day = filename[9:11]
  date = year + "-" + month + "-" + day
  sectionTitle = "A"
  pageNumber = filename[-3:]
  newspaperId = "ekstrabladet"
  newspaperTitle = "Ekstra Bladet"
  editionTitle = filename[12:13]
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/eb_ocr01/e1986.02.24/36.jpg
def storeEkstrabladetOcrJpgValues(path, deliveryDate):
  _,_,date,file = path.split("/")
  pageNumber = file[:-4]
  fileFormat = file[-3:]
  year = date[1:5]
  month = date[6:8]
  day = date[9:11]
  date = year + "-" + month + "-" + day
  sectionTitle = "A"
  newspaperId = "ekstrabladet"
  newspaperTitle = "Ekstra Bladet"
  editionTitle = "1"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/efterlev_141116_2/e1921.05.23/2.jpg
def storeEkstrabladetEfterlevJpgValues(path, deliveryDate):
  _,_,date,file = path.split("/")
  pageNumber,fileFormat = file.split(".")
  fileFormat = "jpg"
  year, month, day = date.split(".")
  year = year[1:]
  date = year + "-" + month + "-" + day
  sectionTitle = "A"
  newspaperId = "ekstrabladet"
  newspaperTitle = "Ekstra Bladet"
  editionTitle = "1"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/pol_hnas/2016/02/19/POL20160219L12E001.pdf
def storePolitikenHnasPdfValues(path, deliveryDate):
  filename,fileFormat = os.path.basename(path).split(".")
  year = filename[3:7]
  month = filename[7:9]
  day = filename[9:11]
  date = year + "-" + month + "-" + day
  sectionTitle = filename[-4:-3]
  pageNumber = filename[-3:]
  newspaperId = "politiken"
  newspaperTitle = "Politiken"
  editionTitle = filename[12:13]
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/pol_hnas/2013/04/07/POL20130407L14019..pdf
def storePolitikenHnasPdfValues3(path, deliveryDate):
  fileFormat = os.path.basename(path)[-3:]
  filename = os.path.basename(path)[:-5]
  year = filename[3:7]
  month = filename[7:9]
  day = filename[9:11]
  date = year + "-" + month + "-" + day
  sectionTitle = "unknown"
  pageNumber = filename[-3:]
  newspaperId = "politiken"
  newspaperTitle = "Politiken"
  editionTitle = filename[12:13]
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/pol_hnas/2006/02/19/5_SEKTION/17.pdf
def storePolitikenHnasPdfValuesSEKTION(path, deliveryDate):
  vest = "/VEST" in path or "/Vest" in path
  augmentedPath = path.replace("/VEST", "")
  augmentedPath = augmentedPath.replace("/Vest", "")
  _,_,year,month,day,sectionTitle,file = augmentedPath.split("/")
  sectionTitle = sectionTitle[:1]
  pageNumber,fileFormat = file.split(".")
  date = year + "-" + month + "-" + day
  newspaperId = "politiken"
  newspaperTitle = "Politiken"
  editionTitle = "1"
  if vest:
    editionTitle = editionTitle + "(VEST)"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/pol_hnas/2006/02/09/VEST/2_UDGAVE/3_SEKTION/4.pdf
def storePolitikenHnasPdfValuesUDGAVE(path, deliveryDate):
  vest = "/VEST" in path
  augmentedPath = path.replace("/VEST", "")
  _,_,year,month,day,editionTitle,sectionTitle,file = augmentedPath.split("/")
  sectionTitle = sectionTitle[:1]
  pageNumber,fileFormat = file.split(".")
  date = year + "-" + month + "-" + day
  newspaperId = "politiken"
  newspaperTitle = "Politiken"
  editionTitle = editionTitle[:1]
  if vest:
    editionTitle = editionTitle + "(VEST)"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/pol_hnas/2009/05/22/POL20090522V13#0005.pdf
def storePolitikenHnasPdfValuesSquare(path, deliveryDate):
  filename,fileFormat = os.path.basename(path).split(".")
  year = filename[3:7]
  month = filename[7:9]
  day = filename[9:11]
  date = year + "-" + month + "-" + day
  sectionTitle = filename[13:14]
  pageNumber = filename[-3:]
  newspaperId = "politiken"
  newspaperTitle = "Politiken"
  editionTitle = filename[12:13]
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/pol_hnas/2004/05/01/7_SEKTION/TAB1L001052004GG029Q.PDF
def storePolitikenHnasPdfValuesTAB(path, deliveryDate):
  _,_,year,month,day,sectionTitle,file = path.split("/")
  sectionTitle = sectionTitle[:1]
  filename,fileFormat = file.split(".")
  fileFormat = "pdf"
  pageNumber = filename[-4:-1]
  date = year + "-" + month + "-" + day
  newspaperId = "politiken"
  newspaperTitle = "Politiken"
  editionTitle = "1"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/pol_hnas/2002/07/13/POL1L01307202002HA007Q.PDF
# avis-pol/pol_hnas/2011/07/12/POLPNDAB120711L10A005.pdf
def storePolitikenHnasPdfValuesRandom(path, deliveryDate):
  _,_,year,month,day,file = path.split("/")
  filename,fileFormat = file.split(".")
  fileFormat = "pdf"
  if "Q" == filename[-1:]:
    sectionTitle = filename[-5:-4]
    pageNumber = filename[-4:-1]
  else:
    sectionTitle = filename[-4:-3]
    pageNumber = filename[-3:]
  date = year + "-" + month + "-" + day
  newspaperId = "politiken"
  newspaperTitle = "Politiken"
  editionTitle = "1"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/pol_ocr01/p1892.07.15/p1892.07.15_0002.pdf
def storePolitikenOcrPdfValues(path, deliveryDate):
  filename = os.path.basename(path)[:-4]
  fileFormat = os.path.basename(path)[-3:]
  year = filename[1:5]
  month = filename[6:8]
  day = filename[9:11]
  date = year + "-" + month + "-" + day
  sectionTitle = "M"
  pageNumber = filename[-3:]
  newspaperId = "politiken"
  newspaperTitle = "Politiken"
  editionTitle = "1"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/pol_ocr01/p1968.08.15/p1968.08.15_0009q.pdf
# (page number is probably wrong)
def storePolitikenOcrPdfValues5(path, deliveryDate):
  filename = os.path.basename(path)[:-4]
  fileFormat = os.path.basename(path)[-3:]
  year = filename[1:5]
  month = filename[6:8]
  day = filename[9:11]
  date = year + "-" + month + "-" + day
  sectionTitle = "M"
  pageNumber = filename[-4:-1]
  newspaperId = "politiken"
  newspaperTitle = "Politiken"
  editionTitle = "1"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/pol_ocr01/p1976.09.08/p1976.09.08_0019-b.pdf
def storePolitikenOcrPdfValues6(path, deliveryDate):
  filename = os.path.basename(path)[:-4]
  fileFormat = os.path.basename(path)[-3:]
  year = filename[1:5]
  month = filename[6:8]
  day = filename[9:11]
  date = year + "-" + month + "-" + day
  sectionTitle = "M"
  pageNumber = filename[-5:-2]
  newspaperId = "politiken"
  newspaperTitle = "Politiken"
  editionTitle = "1"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

# avis-pol/efterlev_211116_2/p2003.03.18/14.jpg
def storePolitikenEfterlevJpgValues(path, deliveryDate):
  _,_,date,file = path.split("/")
  pageNumber,fileFormat = file.split(".")
  fileFormat = "jpg"
  year, month, day = date.split(".")
  year = year[1:]
  date = year + "-" + month + "-" + day
  sectionTitle = "M"
  newspaperId = "politiken"
  newspaperTitle = "Politiken"
  editionTitle = "1"
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "true", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber):
  section = ""
  if sectionTitle != "":
    section = "_"+sectionTitle
  return newspaperId+"/"+year+"/"+month+"/"+day+"/" + newspaperId+"_"+editionTitle+section+"_"+year+"_"+month+"_"+day+"_"+pageNumber+"."+fileFormat

def storeInDB(orig_relpath, format_type, edition_date, single_page, page_number, avisid, avistitle, shadow_path, section_title, edition_title, delivery_date, side_label="", fraktur="false"):
  sql = """INSERT INTO newspaperarchive(orig_relpath, format_type, edition_date, single_page, page_number, avisid, avistitle, shadow_path, section_title, edition_title, delivery_date, side_label, fraktur) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""

  conn = None
  try:
    conn = psycopg2.connect(host=dbhost, database=dbname, user=dbuser, password=dbpassword)
    cursor = conn.cursor()
    cursor.execute(sql, (orig_relpath, format_type, edition_date, single_page, page_number, avisid, avistitle, shadow_path, section_title, edition_title, delivery_date, side_label, fraktur))
    conn.commit()
    cursor.close()
  except (Exception) as error:
    print error
  finally:
    if conn is not None:
      conn.close()

def main():
  if len(sys.argv) > 3:
    unrecognized = open(sys.argv[3], "w")
  else:
    unrecognized = open("unrecognizedfiles", "w")

  for line in open(sys.argv[2], "r"):
    line = line.replace("\n", "")
    if line.endswith(".xml") or line.endswith(".log") or line.endswith(".txt") or line.endswith(".db") or line.endswith(".sh") or line.endswith(".DS_Store"):
      continue
    fullPath = newspaperLocation + "/" + line
    if not os.path.isfile(fullPath):
      print "No file found at " + fullPath
      continue
    deliveryDate = datetime.datetime.fromtimestamp(os.path.getmtime(fullPath)).date()
    # deliveryDate = "2000-01-01"

    stored = False
    for patternId, pattern in filePatterns:
      searchResult = re.search(pattern, line)
      if searchResult != None:
        if "fjerritslev-pdf" in patternId:
          storeFjerritslevPdfValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "fjerritslev-tiff" in patternId:
          storeFjerritslevTiffValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "børsen-jp2" in patternId:
          storeBorsenValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "børsen-pdf3" == patternId:
          storeBorsenPdfValues3(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "børsen-pdf4" == patternId:
          storeBorsenPdfValues4(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "børsen-pdf5" == patternId:
          storeBorsenPdfValues5(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "børsen-pdf6" == patternId:
          storeBorsenPdfValues4(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "børsen-pdf" in patternId:
          storeBorsenValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "børsen-brik-pdf" in patternId:
          storeBorsenBrikValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "børsen-bagside-pdf" == patternId:
          storeBorsenBagsidePdfValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "børsen-special-pdf" == patternId:
          storeBorsenSpecialPdfValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "børsen-brik-jp2" in patternId:
          storeBorsenBrikJp2Values(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "frederikshavn-tiff" in patternId:
          storeFrederikshavnTiffValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "frederikshavn-fraktur-tiff" in patternId:
          storeFrederikshavnTiffValues(searchResult.group(0), deliveryDate, "true")
          stored = True
          break
        if "frederikshavn-pdf" in patternId:
          storeFrederikshavnPdfValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "kristeligtdagblad-pdf" in patternId:
          storeKristeligtDagbladPdfValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "kristeligtdagblad-tiff" in patternId:
          storeKristeligtDagbladTiffValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "loegstoeravis-tiff" in patternId:
          storeFrederikshavnTiffValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "loegstoeravis-fraktur-tiff" in patternId:
          storeLogstorTiffValues(searchResult.group(0), deliveryDate, "true")
          stored = True
          break
        if "loegstoeravis-pdf" in patternId:
          storeLogstorPdfValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "flensborgavis-jp2-2" == patternId:
          storeFlensborgJp2Values2(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "flensborgavis-jp2-4" == patternId:
          storeFlensborgJp2Values4(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "flensborgavis-jp2" in patternId:
          storeFlensborgJp2Values(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "flensborgavis-pdf2" == patternId:
          storeFlensborgPdfValues2(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "flensborgavis-pdf" in patternId:
          storeFlensborgPdfValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "sudschleswigsche-jp2" in patternId:
          storeSudschleswigscheJp2Values(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "politiken-ocr-pdf5" == patternId:
          storePolitikenOcrPdfValues5(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "politiken-ocr-pdf6" == patternId:
          storePolitikenOcrPdfValues6(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "politiken-ocr-pdf" in patternId:
          storePolitikenOcrPdfValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "politiken-hnas-pdf3" == patternId:
          storePolitikenHnasPdfValues3(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "politiken-hnas-sektion-pdf" in patternId:
          storePolitikenHnasPdfValuesSEKTION(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "politiken-hnas-udgave-pdf" in patternId:
          storePolitikenHnasPdfValuesUDGAVE(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "politiken-hnas-#-pdf" in patternId:
          storePolitikenHnasPdfValuesSquare(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "politiken-hnas-tab-pdf" in patternId:
          storePolitikenHnasPdfValuesTAB(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "politiken-hnas-random-pdf" in patternId:
          storePolitikenHnasPdfValuesRandom(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "politiken-hnas-pdf" in patternId:
          storePolitikenHnasPdfValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "politiken-efterlev-jpg" in patternId:
          storePolitikenEfterlevJpgValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "ekstrabladet-hnas-pdf3" == patternId:
          storeEkstrabladetHnasPdfValues3(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "ekstrabladet-hnas-pdf" in patternId:
          storeEkstrabladetHnasPdfValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "ekstrabladet-hnas-sektion-pdf" in patternId:
          storeEkstrabladetHnasPdfValuesSEKTION(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "ekstrabladet-hnas-udgave-pdf" in patternId:
          storeEkstrabladetHnasPdfValuesUDGAVE(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "ekstrabladet-ocr-pdf2" == patternId:
          storeEkstrabladetOcrPdfValues2(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "ekstrabladet-ocr-pdf" in patternId:
          storeEkstrabladetOcrPdfValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "ekstrabladet-ocr-jpg" in patternId:
          storeEkstrabladetOcrJpgValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "ekstrabladet-efterlev-jpg" in patternId:
          storeEkstrabladetEfterlevJpgValues(searchResult.group(0), deliveryDate)
          stored = True
          break

    if not stored:
      unrecognized.write(line + "\n")

  unrecognized.close()

if __name__ == '__main__':
    main()