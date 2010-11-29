from google.appengine.ext import db, blobstore

# Custom property classes
class BlobReferenceListProperty(db.ListProperty):
    def __init__(self, verbose_name):
        super(BlobReferenceListProperty, self).__init__(blobstore.BlobKey, verbose_name)

class ImageReferenceListProperty(BlobReferenceListProperty):
    pass

class ImageReferenceProperty(blobstore.BlobReferenceProperty):
    pass

# Model classes
class Biography(db.Model):
    text = db.TextProperty('Biography')
    artwork = ImageReferenceProperty('Artwork')
    
class Album(db.Model):
    title = db.StringProperty('Title')
    artwork = ImageReferenceProperty('Artwork')
    
class Article(db.Model):
    title = db.StringProperty('Title')
    text = db.TextProperty('Text')
    img = ImageReferenceProperty('Image')

class Player(db.Model):
    title = db.StringProperty('Title')

class Song(db.Model):
    title = db.StringProperty('Title')
    mp3 = blobstore.BlobReferenceProperty('Song')
    lyrics = db.TextProperty('Lyrics')
    track = db.IntegerProperty('Track')
    album = db.ReferenceProperty(Album, 'Album')
    player = db.ReferenceProperty(Player, 'Player')

class Agenda(db.Model):
    title = db.StringProperty('Title')
    date = db.DateTimeProperty('Date and Time')
    place = db.StringProperty('Location')
    link = db.LinkProperty('Link')

class Photo(db.Model):
    title = db.StringProperty('Title')
    credits = db.StringProperty('Credits')
    img = ImageReferenceProperty('Image')
    photos = ImageReferenceListProperty('Photos')
    concert = db.ReferenceProperty(Agenda, 'Concert')

class Video(db.Model):
    title = db.StringProperty('Title')
    content = db.TextProperty('Content')

class Contact(db.Model):
    title = db.StringProperty('Title')
    name = db.StringProperty('Name')
    phone = db.StringProperty('Telephone')
    email = db.EmailProperty('Email')
    address = db.TextProperty('Address')

class Link(db.Model):
    title = db.StringProperty('Title')
    link = db.LinkProperty('Link')

class Guestbook(db.Model):
    name = db.StringProperty('Name')
    text = db.TextProperty('Message')

class Newsletter(db.Model):
    email = db.EmailProperty('Email')

class News(db.Model):
    title = db.StringProperty('Title')
    text = db.TextProperty('Text')
