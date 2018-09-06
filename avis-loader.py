#!/usr/bin/env python2.7

import ConfigParser
import os
import psycopg2
import datetime
import re


config = ConfigParser.RawConfigParser()
config.read("avis-loader-config.cfg")

dbname = config.get("db-config", "dbname")
dbuser = config.get("db-config", "user")
dbhost = config.get("db-config", "host")
dbpassword = config.get("db-config", "password")

newspaperName = config.get("loader-config", "newspaper-name")
newspaperPath = config.get("loader-config", "newspaper-path")
filePatterns = config.items("file-patterns")

def storeFjerritslevPdfValues(path, deliveryDate):
  paper,date,_,editionTitle,pageAndFormat = os.path.basename(path).split("_")
  page,fileFormat = pageAndFormat.split(".")
  pageNumber = page.replace("-","")
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = newspaperName.replace(" ", "_")
  shadowPath = createShadowPath(newspaperId, editionTitle, fileFormat, year, month, day)
  storeInDB(path, fileFormat, date, "false", pageNumber, newspaperId, shadowPath, "", editionTitle, deliveryDate)

def storeFjerritslevTiffValues(path, deliveryDate):
  paper,_,_,_ = path.split("/")
  date,_,editionTitle,pageAndFormat = os.path.basename(path).split("_")
  page,fileFormat = pageAndFormat.split(".")
  pageNumber = page.replace("-","")
  year = date[0:4]
  month = date[4:6]
  day = date[6:8]
  date = year + "-" + month + "-" + day
  newspaperId = newspaperName.replace(" ", "_")
  shadowPath = createShadowPath(newspaperId, editionTitle, fileFormat, year, month, day)
  storeInDB(path, fileFormat, date, "false", pageNumber, newspaperId, shadowPath, "", editionTitle, deliveryDate)

def createShadowPath(newspaperId, editionTitle, fileFormat, year, month, day):
  return newspaperId+"/"+year+"/"+month+"/"+day+"/" + newspaperId+"_"+editionTitle+"_"+year+"_"+month+"_"+day+"."+fileFormat

def storeInDB(orig_relpath, format_type, edition_date, single_page, page_number, avisid, shadow_path, section_title, edition_title, delivery_date):
  sql = """INSERT INTO newspaperarchive VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""

  conn = None
  try:
    conn = psycopg2.connect(host=dbhost, database=dbname, user=dbuser, password=dbpassword)
    cursor = conn.cursor()
    cursor.execute(sql, (orig_relpath, format_type, edition_date, single_page, page_number, avisid, shadow_path, section_title, edition_title, delivery_date))
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

  for line in open("filelist", "r"):
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
    if not stored:
      unrecognized.write(line)

  unrecognized.close()

if __name__ == '__main__':
    main()