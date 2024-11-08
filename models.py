from sqlalchemy import String, Integer, Boolean, Column, text, TIMESTAMP, Date, ForeignKey, Float, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('Now()'))


class Artist(Base):
    __tablename__ = 'artist'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String, nullable=False)
    name = Column(String, unique=True)
    genre = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('Now()'))


class Follower(Base):
    __tablename__ = 'follower'

    user_id = Column(Integer,
                     ForeignKey('user.id', ondelete='CASCADE'),
                     nullable=False)
    artist_id = Column(Integer,
                       ForeignKey('artist.id', ondelete='CASCADE'),
                       nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('Now()'))

    user = relationship('User', backref='followers')
    artist = relationship('Artist', backref='followers')

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'artist_id'),
    )


class Track(Base):
    __tablename__ = 'track'

    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer,
                       ForeignKey('artist.id', ondelete='CASCADE'),
                       nullable=False)
    album_id = Column(Integer,
                      ForeignKey('album.id', ondelete='CASCADE'),
                      nullable=False)
    name = Column(String, nullable=False)
    release_date = Column(Date, nullable=False)
    price = Column(Float)
    path = Column(String, nullable=False)

    artist = relationship('Artist', backref='tracks')
    album = relationship('Album', backref='tracks')


class Album(Base):
    __tablename__ = 'album'

    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer,
                       ForeignKey('artist.id', ondelete='CASCADE'),
                       nullable=False)
    name = Column(String, nullable=False)
    release_date = Column(Date, nullable=False)
    price = Column(Float)

    artist = relationship('Artist', backref='tracks')


class Playlist(Base):
    __tablename__ = 'playlist'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer,
                     ForeignKey('user.id', ondelete='CASCADE'),
                     nullable=False)
    name = Column(String, nullable=False)

    user = relationship('User', backref='followers')


class PlaylistTrack(Base):
    __tablename__ = 'playlist_track'

    playlist_id = Column(Integer,
                         ForeignKey('playlist.id', ondelete='CASCADE'),
                         nullable=False)
    track_id = Column(Integer,
                      ForeignKey('track.id', ondelete='CASCADE'),
                      nullable=False)
    order = Column(Integer, nullable=False)

    playlist = relationship('Playlist', backref='playlist_tracks')
    track = relationship('Track', backref='playlist_tracks')

    __table_args__ = (
        PrimaryKeyConstraint('playlist_id', 'track_id'),
    )


class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer,
                     ForeignKey('user.id', ondelete='CASCADE'),
                     nullable=False)
    name = Column(String, nullable=False)
    order_date = Column(TIMESTAMP, nullable=False, server_default=text('Now()'))
    status = Column(String, nullable=False, server_default=text("'Processing'"))
    total = Column(Float)
    payment_method_id = Column(Integer,
                               ForeignKey('user_payment_method.id', ondelete='CASCADE'),
                               nullable=False)

    user = relationship('User', backref='tracks')
    payment_method = relationship('UserPaymentMethod', backref='orders')


class OrderItem(Base):
    __tablename__ = 'order_item'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer,
                      ForeignKey('order.id', ondelete='CASCADE'),
                      nullable=False)
    item_id = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    price = Column(Float)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Float)

    order = relationship('Order', backref='order_items')
    album = relationship('Album',
                         primaryjoin="and_(OrderItem.item_id == foreign(Album.id), OrderItem.type == 'album')",
                         viewonly=True)
    track = relationship('Track',
                         primaryjoin="and_(OrderItem.item_id == foreign(Track.id), OrderItem.type == 'track')",
                         viewonly=True
                         )

    @property
    def item(self):
        """Returns the album or track object based on the type."""
        return self.album if self.type == 'album' else self.track


class UserPaymentMethod(Base):
    __tablename__ = 'user_payment_method'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer,
                     ForeignKey('user.id', ondelete='CASCADE'),
                     nullable=False)
    type = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    expiry_date = Column(String, nullable=False)
    cvv = Column(String, nullable=False)
    shipping_address = Column(String, nullable=False)
    billing_address = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    is_default = Column(Boolean)

    user = relationship('User', backref='user_payment_methods')
