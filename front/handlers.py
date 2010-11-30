import logging
from datetime import datetime
import urllib

import simplejson as json
import markdown2
from google.appengine.ext import webapp
from google.appengine.ext import db, blobstore
from google.appengine.api import images

import view
import models
import utils

serve_url = '/serve/%s'

class AppHandler(webapp.RequestHandler):
    def prepare(self, data=None):
        if not data: return None
        for k,v in data.iteritems():
            if isinstance(v, db.Model):
                data[k] = utils.to_dict(v)
            elif isinstance(v, list) and len(v) and isinstance(v[0], db.Model):
                data[k] = utils.to_dicts(v)
        return data
    
    def renderjson(self, filename, data=None):
        self.response.out.write(json.dumps({
            'data': self.prepare(data),
            'template': view.get_file(filename)
        }))
    
    def render(self, filename, data):
        data = self.prepare(data)
        view.render(self, filename, data)


# Helpers
def agenda(nb):
    agenda = models.Agenda.all().filter('date >=', datetime.now()).fetch(nb)
    agendad = utils.to_dicts(agenda)
    for item in agendad:
        item['date'] = datetime.fromtimestamp(item['date']).strftime('%Y/%m/%d %H:%M')
    return agendad


class MainHandler(AppHandler):
    def get(self):
        self.render('main.html', {
            'agenda': agenda(3),
            'player': self.player(),
            'links': self.links()
        })
    
    def player(self):
        try:
            songs = models.Player.all().get().song_set
        except AttributeError:
            return ''
        url = '/serve/%s'
        data = {
            'mp3': '|'.join([url % str(s.mp3.key()) for s in songs]),
            'title': '|'.join([s.title for s in songs])
        }
        return urllib.urlencode(data).replace('%3D','=')
    
    def links(self):
        links = models.Link.all().fetch(10)
        return utils.to_dicts(links)


class HomeHandler(AppHandler):
    def get(self):
        self.renderjson('home.html', {
            'news': self.news(),
            'contacts': self.contacts(),
        })
    
    def news(self):
        news = models.News.all().get()
        if not news:
            return False
        return utils.to_dict(news)
    
    def contacts(self):
        contacts = models.Contact.all().fetch(10)
        return utils.to_dicts(contacts)
    
    def ressources(self):
        res = models.Ressources.all().fetch(5)
        return utils.to_dicts(res)


class AgendaHandler(AppHandler):
    def get(self):
        self.renderjson('agenda.html', {'agenda': agenda(100)})


class BioHandler(AppHandler):
    def get(self):
        bio = models.Biography.all().get()
        if not bio:
            biod = {}
        else:
            biod = utils.to_dict(bio)
        self.renderjson('bio.html', biod)


class MusicHandler(AppHandler):
    def get(self, id):
        id = int(id or 0)
        self.m = models.Album
        self.renderjson('music.html', {
            'albums': self.albums(),
            'album': self.album(id)
        })
    
    def albums(self):
        albums = self.m.all().fetch(5)
        albums = utils.to_dicts(albums)
        for item in albums:
            # TODO: FIX DATE
            # item['date'] = datetime.fromtimestamp(item['date']).strftime('%Y')
            try:
                item['artwork'] = images.get_serving_url(item['artwork'], 104, crop=True)
            except images.BlobKeyRequiredError:
                item['artwork'] = ''
        return albums
    
    def album(self, id):
        if not id:
            album = self.m.all().get()
        else:
            album = self.m.get_by_id(id)
        if not album:
            return False
        albumd = utils.to_dict(album)
        try:
            albumd['artwork'] = images.get_serving_url(albumd['artwork'], 288)
        except images.BlobKeyRequiredError:
            albumd['artwork'] = ''
        albumd['songs'] = self.songs(album)
        return albumd
    
    def songs(self, album):
        songs = album.song_set
        return utils.to_dicts(songs)


class MediaHandler(AppHandler):
    def get(self):
        self.renderjson('media.html')


class PhotosHandler(AppHandler):
    def get(self, id):
        id = int(id or 0)
        self.m = models.Photo
        self.renderjson('photos.html', {
          'photos': self.photos(),
          'photo': self.photo(id)
        })
        
    def photos(self):
        photos = self.m.all().fetch(10)
        photosd = utils.to_dicts(photos)
        for item in photosd:
            item['photos'] = []
            item['img'] = images.get_serving_url(item['img'], 144, True)
        return photosd
    
    def photo(self, id):
        if not id:
            photo = self.m.all().get()
        else:
            photo = self.m.get_by_id(id)
        if not photo:
            return False
        photod = utils.to_dict(photo)
        photod['concert'] = photo.concert.title
        for i in range(len(photod['photos'])):
            key = str(photod['photos'][i])
            url = images.get_serving_url(key, 80, True)
            url_big = images.get_serving_url(key, 720)
            photod['photos'][i] = {'url': url, 'url_big': url_big}
        return photod


class VideosHandler(AppHandler):
    def get(self, id):
        id = int(id or 0)
        self.m = models.Video
        self.renderjson('videos.html', {
            'videos': self.videos(),
            'video': self.video(id)
        })
    
    def videos(self):
        videos = self.m.all().fetch(10)
        videosd = utils.to_dicts(videos)
        for item in videosd:
            item['content'] = ''
        return videosd
    
    def video(self, id):
        if not id:
            video = self.m.all().get()
        else:
            video = self.m.get_by_id(id)
        if not video:
            return False
        return utils.to_dict(video)


class PressHandler(AppHandler):
    def get(self, id):
        id = int(id or 0)
        self.m = models.Article
        self.renderjson('press.html', {
            'articles': self.articles(),
            'article': self.article(id)
        })
    
    def articles(self):
        items = self.m.all().fetch(10)
        itemsd = utils.to_dicts(items)
        for item in itemsd:
            item['text'] = ''
        return itemsd

    def article(self, id):
        if not id:
            item = self.m.all().get()
        else:
            item = self.m.get_by_id(id)
        if not item:
            return False
        itemd = utils.to_dict(item)
        return itemd


class NewsletterHandler(AppHandler):
    def get(self, delete):
        email = self.request.get('email', None)
        if delete:
            self.delete(email)
        else:
            self.subscribe(email)
    
    def subscribe(self, email):
        if not email:
            self.response.out.write('0')
            return
        if models.Newsletter.gql('WHERE email = :1', email).count():
            self.response.out.write('2')
            return
        models.Newsletter(email=email).put()
        self.response.out.write('1')
    
    def delete(self, email):
        if not email:
            self.reponse.out.write('Not a valid Email')
            return
        query = models.Newsletter.gql('WHERE email = :1', email)
        if query.count():
            query.get().delete()
            self.response.out.write('L\'address email "%s" has been removed from the newsletter.' % email)
        else:
            self.response.out.write('...')


class GuestbookHandler(AppHandler):
    def get(self):
        mess = models.Guestbook.all().fetch(100)
        if mess:
            messd = utils.to_dicts(mess)
            messd = sorted(messd, lambda x,y: cmp(x['id'], y['id']), reverse=True)
        else:
            messd = {}
        self.renderjson('guestbook.html', {
            'mess': messd
        })
    
    def post(self):
        name = self.request.get('name', '')
        text = self.request.get('text', '')
        if name and text:
            models.Guestbook(name=name, text=text).put()
            self.response.out.write('1')
        else:
            self.response.out.write('0')


routes = [
    (r'^/bio/?', BioHandler),
    (r'^/music/?(\d+)?/?', MusicHandler),
    (r'^/photos/?(\d+)?/?', PhotosHandler),
    (r'^/videos/?(\d+)?/?', VideosHandler),
    (r'^/press/?(\d+)?/?', PressHandler),
    (r'^/media/?', MediaHandler),
    (r'^/newsletter/?(\w+)?/?', NewsletterHandler),
    (r'^/guestbook/?', GuestbookHandler),
    (r'^/home/?', HomeHandler),
    (r'^/agenda/?', AgendaHandler),
    (r'^/', MainHandler)
]
