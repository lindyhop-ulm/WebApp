from pymongo import MongoClient
from flask import Flask, request, render_template
from datetime import datetime as dt
import time
import html
import os

#Zugangsdaten DB

client=MongoClient(DB_URL, username= DB_USER, password=DB_PASSWORD)
db=client['meine_db']
col=db['meine_collection']
col_id=db['aktuelleID']

print(client.list_database_names())

def sanitisize_input (input_str):
    sanitized_str=html.escape(input_str)
    return sanitized_str

def datum_anpassen (tag, monat, jahr, uhrzeit):
    if len(tag) > 2 or len(monat) > 2 or len(jahr) > 4 or len(uhrzeit) > 2:
        return 'Eingabe fehlerhaft'
    else:
      try:
        day=int(tag)
        month=int(monat)
        year=int(jahr)
        hour=int(uhrzeit)
        datum='%s-%s-%sT%s:00:00' %(jahr.zfill(4),monat.zfill(2),tag.zfill(2),uhrzeit.zfill(2))
        return datum
      except ValueError:
        return 'Eingabe fehlerhaft'
    

def link_valid(link):
    if link[0:8]=='https://':
      return link
    elif link[0:3]== 'www':
        return link
    elif link == '':
        return link
    else:
        return 'invalid'

app=Flask(__name__)

if len(list(col_id.find()))==0:
  col_id.insert_one({'id':0})

@app.route('/')
def index():
    return render_template('lindyhopulm2.j2')

@app.route('/veranstaltungen', methods=['POST', 'GET'])
def veranstaltungen():
  jetzt=dt.now().isoformat()
  col.delete_many({'datum': {'$lt': jetzt}})
  res=col.find(projection={'_id':0})
  posts=list(res)
  if request.method == 'POST':
      if request.form['name'] != '':
                name=sanitisize_input(request.form['name'])
                print(name)
                link=sanitisize_input(request.form.get('link', '-'))
                linkval=link_valid(link)
                if linkval == 'invalid':
                    return render_template('fehlermeldung_link.j2', posts=posts)
                tag=sanitisize_input(request.form.get('tag','-'))
                monat=sanitisize_input(request.form.get('monat','-'))
                jahr=sanitisize_input(request.form.get('jahr','-'))
                uhrzeit=sanitisize_input(request.form.get('uhrzeit','-'))
                datum=datum_anpassen(tag, monat, jahr, uhrzeit)
                print(datum)
                if datum == 'Eingabe fehlerhaft':
                  return render_template('fehlermeldung_datum.j2', posts=posts)
                stadt=sanitisize_input(request.form.get('stadt', '-'))
                col_id.update_one({}, {'$inc':{'id':1}})
                res_id=col_id.find(projection={'_id':0})
                for element in res_id:
                  id_neu=element['id']
                veranstaltung={'id':id_neu, 'name':name, 'link': linkval, 'datum': datum, 'stadt': stadt}
                col.insert_one(veranstaltung)
                res=col.find(projection={'_id':0})
                posts=list(res)
                return render_template('veranstaltungen.j2', posts=posts)
      else:
        return render_template('fehlermeldung_name.j2', posts=posts)
  else:
    return render_template('veranstaltungen.j2', posts=posts)

@app.route('/kurse')
def kurse():
        return render_template('kurse.j2')

print(__name__)

if __name__=='__main__':
    app.run()