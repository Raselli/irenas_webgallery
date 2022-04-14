from .database import Paintings, Artists
from flask import Blueprint, render_template, abort


gallery = Blueprint("gallery", __name__)


@gallery.route("/")
def index():
    tiles = Paintings.query.filter(Paintings.timestamp).order_by(Paintings.timestamp.desc()).limit(16).all()
    entry = Paintings.query.filter(Paintings.timestamp).order_by(Paintings.timestamp.desc()).first_or_404()
    artist = Artists.query.filter(Artists.user_id == entry.user_id).first_or_404()
    return render_template("index.html", entry=entry, artist=artist, tiles=tiles)


# Gallery: filter
@gallery.route("/gallery/", defaults={"filter": "newest"}, methods=["GET"])
@gallery.route("/gallery/<filter>", methods=["GET"])
def gal(filter):

    # filter-function: query paintings.db by "filter"
    # IMPROVEMENT: match/case with python3.10
    def entries_by_filter(filter):
        queries = {
            "newest": Paintings.query.order_by(Paintings.timestamp.desc()).all(),
            "oldest": Paintings.query.order_by(Paintings.timestamp.asc()).all(),
            "title": Paintings.query.order_by(Paintings.title.asc()).all(),
            "artist": Paintings.query.order_by(Paintings.user_id.desc()).all(),
            "width": Paintings.query.filter(Paintings.width).order_by(Paintings.width.desc()).all(),
            "height": Paintings.query.filter(Paintings.height).order_by(Paintings.height.desc()).all(),
            "price": Paintings.query.filter(Paintings.price).order_by(Paintings.price.desc()).all(),
            "available": Paintings.query.filter(Paintings.sold.is_(False)).all(),
        }
        fltrs = dict.keys(queries)
        entries = queries.get(filter)
        if filter in queries:
            return entries, fltrs
        else:
            return abort(400)

    # Method = GET: sort /gallery by filter
    filter_results = entries_by_filter(filter)
    entries = filter_results[0]
    fltrs = filter_results[1]
    return render_template("gallery.html", entries=entries, current_filter=filter, fltrs=fltrs)


@gallery.route("/gallery/<filter>", defaults={"filter": None, "title": None}, methods=["GET"])
@gallery.route("/gallery/<filter>/<title>", methods=["GET"])
def enlargen(filter, title):
    # Method = GET: enlargen image based on title & filter
    enlargen = Paintings.query.filter(Paintings.title == title).first_or_404()
    display_name = Artists.query.filter((Artists.user_id == enlargen.user_id)).first().display_name
    return render_template("enlargen.html", enlargen=enlargen, display_name=display_name, filter=filter)


# Artist: List of all artists
@gallery.route("/artists", methods=["GET"])
def all_artists():
    # Calculate sum of entries per artist
    # TODO: function that returns sum
    artists = Artists.query.order_by(Artists.display_name).all()
    sum_entries = {}
    for artist in artists:
        count = Paintings.query.filter(Paintings.user_id == artist.user_id).count()
        sum_entries[artist] = count

    sm = ['twitter', 'facebook', 'youtube', 'instagram']
    return render_template("artists.html", artists=sum_entries, socialmedias=sm)


# Artist: load specific artist
@gallery.route("/artists/<display_name>/", defaults={"display_name": None, "filter": "newest"}, methods=["GET"])
@gallery.route("/artists/<display_name>/<filter>", methods=["GET"])
def description_artist(display_name, filter):

    # filter-function: query paintings.db by "filter" and artist.user_id
    def entries_by_filter(user_id, filter):
        queries = {
            "newest": Paintings.query.filter(Paintings.user_id.is_(user_id)).order_by(Paintings.timestamp.desc()).all(),
            "oldest": Paintings.query.filter(Paintings.user_id.is_(user_id)).order_by(Paintings.timestamp.asc()).all(),
            "title": Paintings.query.filter(Paintings.user_id.is_(user_id)).order_by(Paintings.title.asc()).all(),
            "width": Paintings.query.filter((Paintings.user_id.is_(user_id)) & (Paintings.width)).order_by(Paintings.width.desc()).all(),
            "height": Paintings.query.filter(Paintings.user_id.is_(user_id) & Paintings.height).order_by(Paintings.height.desc()).all(),
            "price": Paintings.query.filter(Paintings.user_id.is_(user_id) & Paintings.price).order_by(Paintings.price.desc()).all(),
            "available": Paintings.query.filter(Paintings.user_id.is_(user_id) & Paintings.sold.is_(False)).all()
        }
        fltrs = dict.keys(queries)
        entries = queries.get(filter)
        if filter in queries:
            return entries, fltrs
        else:
            return abort(400)

    # method = "GET": load specific artist & specific artist's entries
    artist = Artists.query.filter(Artists.display_name == display_name).first_or_404()
    filter_results = entries_by_filter(artist.user_id, filter)
    entries = filter_results[0]
    fltrs = filter_results[1]
    sm = ['twitter', 'facebook', 'youtube', 'instagram']
    return render_template("artist.html", artist=artist, current_filter=filter, entries=entries, socialmedias=sm, fltrs=fltrs)