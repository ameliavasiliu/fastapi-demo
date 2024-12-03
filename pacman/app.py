import os
import json
import mysql.connector
import boto3
from chalice import Chalice

app = Chalice(app_name='pacman')
app.debug = True

# s3 things
## UPDATE NEXT LINE
S3_BUCKET = 'ega9cw-dp1-spotify'
s3 = boto3.client('s3')

# base URL for accessing the files
## UPDATE NEXT LINE
baseurl = 'http://ega9cw-dp1-spotify.s3-website-us-east-1.amazonaws.com/'

# database things
DBHOST = 'ds2022.cqee4iwdcaph.us-east-1.rds.amazonaws.com'
DBUSER = 'admin'
DBPASS = os.getenv('DBPASS')
DB = 'ega9cw'
db = mysql.connector.connect(user=DBUSER, host=DBHOST, password=DBPASS, database=DB)
cur = db.cursor()

# file extensions to trigger on
_SUPPORTED_EXTENSIONS = (
    '.json'
)

# ingestor lambda function
@app.on_s3_event(bucket=S3_BUCKET, events=['s3:ObjectCreated:*'])
def s3_handler(event):
  if _is_json(event.key):
    # get the file, read it, load it into JSON as an object
    response = s3.get_object(Bucket=S3_BUCKET, Key=event.key)
    text = response["Body"].read().decode()
    data = json.loads(text)

    # parse the data fields 1-by-1 from 'data'
    TITLE = data['title'] 
    ALBUM = data['album']
    ARTIST = data['artist']
    YEAR = data['year']
    GENRE = data['genre']

    # get the unique ID for the bundle to build the mp3 and jpg urls
    # you get 5 data points in each new JSON file that arrives, but
    # you need 7 fields for the INSERT. The two additional values are
    # URLs you must formulate given you know the unique ID these files
    # are named.
    keyhead = event.key
    identifier = keyhead.split('.')
    ID = identifier[0]
    MP3 = baseurl + ID + '.mp3'
    IMG = baseurl + ID + '.jpg'

    app.log.debug("Received new song: %s, key: %s", event.bucket, event.key)

    # try to insert the song into the database
    try:
      add_song = ("INSERT INTO songs "
               "(title, album, artist, year, file, image, genre) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s)")
      song_vals = (TITLE, ALBUM, ARTIST, YEAR, MP3, IMG, GENRE)
      cur.execute(add_song, song_vals)
      db.commit()

    except mysql.connector.Error as err:
      app.log.error("Failed to insert song: %s", err)
      db.rollback()

# perform a suffix match against supported extensions
def _is_json(key):
  return key.endswith(_SUPPORTED_EXTENSIONS)
