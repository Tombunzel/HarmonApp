from sqlalchemy import String, Integer, Boolean, Column, text, TIMESTAMP, Date, ForeignKey, Float
from sqlalchemy import PrimaryKeyConstraint, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from HarmonApp.datamanager.database import Base
from HarmonApp.schemas.user_schemas import UserRole


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('Now()'))
    role = Column(SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.USER)
    disabled = Column(Boolean, nullable=False)

    # Relationships
    followed_artists = relationship('Follower', back_populates='user')
    playlists = relationship('Playlist', back_populates='user')
    orders = relationship('Order', back_populates='user')
    payment_methods = relationship('UserPaymentMethod', back_populates='user')


class Artist(Base):
    __tablename__ = 'artist'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String, nullable=False)
    name = Column(String, unique=True)
    genre = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('Now()'))
    disabled = Column(Boolean, nullable=False)

    # Relationships
    followers = relationship('Follower', back_populates='artist')
    tracks = relationship('Track', back_populates='artist')
    albums = relationship('Album', back_populates='artist')


class Follower(Base):
    __tablename__ = 'follower'

    user_id = Column(Integer,
                     ForeignKey('user.id', ondelete='CASCADE'),
                     nullable=False)
    artist_id = Column(Integer,
                       ForeignKey('artist.id', ondelete='CASCADE'),
                       nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('Now()'))

    # Relationships
    user = relationship('User', back_populates='followed_artists')
    artist = relationship('Artist', back_populates='followers')

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

    # Relationships
    artist = relationship('Artist', back_populates='tracks')
    album = relationship('Album', back_populates='tracks')
    playlist_entries = relationship('PlaylistTrack', back_populates='track')
    order_items = relationship(
        'OrderItem',
        primaryjoin="and_(foreign(OrderItem.item_id) == Track.id, "
                    "OrderItem.type == 'track')",
        back_populates='track',
        viewonly=True
    )


class Album(Base):
    __tablename__ = 'album'

    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer,
                       ForeignKey('artist.id', ondelete='CASCADE'),
                       nullable=False)
    name = Column(String, nullable=False)
    release_date = Column(Date, nullable=False)
    price = Column(Float)

    # Relationships
    artist = relationship('Artist', back_populates='albums')
    tracks = relationship('Track', back_populates='album')
    order_items = relationship(
        'OrderItem',
        primaryjoin="and_(foreign(OrderItem.item_id) == Album.id, "
                    "OrderItem.type == 'album')",
        back_populates='album',
        viewonly=True
    )


class Playlist(Base):
    __tablename__ = 'playlist'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer,
                     ForeignKey('user.id', ondelete='CASCADE'),
                     nullable=False)
    name = Column(String, nullable=False)

    # Relationships
    user = relationship('User', back_populates='playlists')
    track_entries = relationship('PlaylistTrack', back_populates='playlist')


class PlaylistTrack(Base):
    __tablename__ = 'playlist_track'

    playlist_id = Column(Integer,
                         ForeignKey('playlist.id', ondelete='CASCADE'),
                         nullable=False)
    track_id = Column(Integer,
                      ForeignKey('track.id', ondelete='CASCADE'),
                      nullable=False)
    order = Column(Integer, nullable=False)

    # Relationships
    playlist = relationship('Playlist', back_populates='track_entries')
    track = relationship('Track', back_populates='playlist_entries')

    __table_args__ = (
        PrimaryKeyConstraint('playlist_id', 'track_id'),
    )


class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer,
                     ForeignKey('user.id', ondelete='CASCADE'),
                     nullable=False)
    order_date = Column(TIMESTAMP, nullable=False, server_default=text('Now()'))
    status = Column(String, nullable=False, server_default=text("'Processing'"))
    total = Column(Float)
    payment_method_id = Column(Integer,
                               ForeignKey('user_payment_method.id', ondelete='CASCADE'),
                               nullable=False)

    # Relationships
    user = relationship('User', back_populates='orders')
    payment_method = relationship('UserPaymentMethod', back_populates='orders')
    items = relationship('OrderItem', back_populates='order')


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

    # Relationships
    order = relationship('Order', back_populates='items')
    album = relationship(
        'Album',
        primaryjoin="and_(OrderItem.item_id == Album.id, "
                    "OrderItem.type == 'album')",
        foreign_keys=[item_id],
        viewonly=True
    )
    track = relationship(
        'Track',
        primaryjoin="and_(OrderItem.item_id == Track.id, "
                    "OrderItem.type == 'track')",
        foreign_keys=[item_id],
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

    # Relationships
    user = relationship('User', back_populates='payment_methods')
    orders = relationship('Order', back_populates='payment_method')
