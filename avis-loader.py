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

dbname = config.get("db-config", "dbname")
dbuser = config.get("db-config", "user")
dbhost = config.get("db-config", "host")
dbpassword = config.get("db-config", "password")
filePatterns = config.items("file-patterns")

def storeFjerritslevPdfValues(path, deliveryDate):
  _,date,_,editionTitle,pageAndFormat = os.path.basename(path).split("_")
  page,fileFormat = pageAndFormat.split(".")
  pageNumber = page.replace("-","")
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = "fjerritslevavis"
  newspaperTitle = "Fjerritslev Avis"
  sectionTitle = ""
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "false", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeFjerritslevTiffValues(path, deliveryDate):
  date,_,editionTitle,pageAndFormat = os.path.basename(path).split("_")
  page,fileFormat = pageAndFormat.split(".")
  pageNumber = page.replace("-","")
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = "fjerritslevavis"
  newspaperTitle = "Fjerritslev Avis"
  sectionTitle = ""
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "false", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def storeBorsenValues(path, deliveryDate):
  date,pageAndFormat = os.path.basename(path).split("_")
  pageNumber,fileFormat = pageAndFormat.split(".")
  year,month,day = date.split("-")
  newspaperId = "boersen"
  newspaperTitle = "Børsen"
  editionTitle="Main"
  sectionTitle = ""
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, "false", pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

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
    singlePage=False
  else:
    pageNumber = "1"
    editionTitle = filename
    singlePage=True

  newspaperId = "boersen"
  newspaperTitle = "Børsen"
  editionTitle = "Brik-" + editionTitle
  sectionTitle = ""
  shadowPath = createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber)
  storeInDB(path, fileFormat, date, singlePage, pageNumber, newspaperId, newspaperTitle, shadowPath, sectionTitle, editionTitle, deliveryDate)

def createShadowPath(newspaperId, editionTitle, sectionTitle, fileFormat, year, month, day, pageNumber):
  section = ""
  if sectionTitle != "":
    section = "_"+sectionTitle
  return newspaperId+"/"+year+"/"+month+"/"+day+"/" + newspaperId+"_"+editionTitle+section+"_"+year+"_"+month+"_"+day+"_"+pageNumber+"."+fileFormat

def storeInDB(orig_relpath, format_type, edition_date, single_page, page_number, avisid, avistitle, shadow_path, section_title, edition_title, delivery_date):
  sql = """INSERT INTO newspaperarchive VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""

  conn = None
  try:
    conn = psycopg2.connect(host=dbhost, database=dbname, user=dbuser, password=dbpassword)
    cursor = conn.cursor()
    cursor.execute(sql, (orig_relpath, format_type, edition_date, single_page, page_number, avisid, avistitle, shadow_path, section_title, edition_title, delivery_date))
    conn.commit()
    cursor.close()
  except (Exception) as error:
    print error
  finally:
    if conn is not None:
      conn.close()

def main():
  now = datetime.datetime.now()
  deliveryDate=now.strftime("%Y-%m-%d")

  unrecognized = open("unrecognizedfiles", "w")

  for line in open(sys.argv[1], "r"):
    if line.endswith(".xml\n") or line.endswith(".log\n") or line.endswith(".txt\n") or line.endswith(".db\n"):
      continue

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
        if "børsen-pdf" in patternId:
          storeBorsenValues(searchResult.group(0), deliveryDate)
          stored = True
          break
        if "børsen-brik-pdf" in patternId:
          storeBorsenBrikValues(searchResult.group(0), deliveryDate)
          stored = True
          break

    if not stored:
      unrecognized.write(line)

  unrecognized.close()

if __name__ == '__main__':
    main()