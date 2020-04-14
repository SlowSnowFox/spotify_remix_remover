import sys
import spotipy
import spotipy.util as util
import re
import configparser


CONFIG_FILENAME = "remover_params.conf"


class SpotifyRemixRemover:
    REQUIRED_SCOPE = "playlist-modify-private playlist-read-private"

    def __init__(self, username, banned_keywords, token, new_releases_playlist_name):
        """
        :param username: Spotify username
        :param banned_keywords: Song names containing these words are filtered out.
        :param token: spotify api access token
        :param new_releases_playlist_name: name of the playlist that should be filtered
        """
        self.new_releases_playlist_name = new_releases_playlist_name
        self.username = username
        self.banned_regex = "|".join(banned_keywords)
        self.sp = spotipy.Spotify(auth=token)

    def run_removal_process(self, new_playlist_name, delete_old_songs_in_playlist):
        """
        :param new_playlist_name: name of the new playlist without the remixes etc. Can also be an existing playlist
        :param delete_old_songs_in_playlist: Deletes all the previous songs in the playlist if it exists and if this
        flag is enabled
        """
        all_playlists = self.sp.user_playlists(self.username)
        new_releases_pl = self._get_new_releases_playlist(all_playlists)
        all_songs = self._get_all_songs_from_playlist(new_releases_pl)
        filtered_songs = self._filter_songs(all_songs)
        self._add_songs_to_new_playlist(filtered_songs, new_playlist_name, delete_old_songs_in_playlist)

    def _add_songs_to_new_playlist(self, songs, new_playlist_name, delete_old_songs_in_playlist):
        existing_playlist = self._get_playlist_with_existing_name(new_playlist_name)
        if existing_playlist:
            if delete_old_songs_in_playlist:
                self._delete_all_songs_from_playlist(existing_playlist)
            target_playlist_id = existing_playlist['id']
        else:
            results = self.sp.user_playlist_create(self.sp.me()['id'], new_playlist_name, public=False)
            target_playlist_id = results['id']
        self.sp.user_playlist_add_tracks(self.sp.me()['id'], target_playlist_id, [song['track']['id'] for song in songs])

    def _get_new_releases_playlist(self, playlists):
        for playlist in playlists['items']:
            if playlist['name'] == self.new_releases_playlist_name:
                return playlist
        raise FileNotFoundError("Could not find the new releases playlist in Spotify. Please check the specified name")

    def _filter_songs(self, songs):
        def filter_song(song):  # For speed up use the Aho–Corasick algorithm
            return not any(re.findall(self.banned_regex,
                                      song['track']['name'],
                                      re.IGNORECASE))

        return list(filter(filter_song, songs))

    def _get_all_songs_from_playlist(self, playlist):
        all_tracks = []
        results = self.sp.playlist(playlist['id'], fields="tracks,next")
        tracks = results['tracks']
        all_tracks += tracks['items']
        while tracks['next']:
            tracks = self.sp.next(tracks)
            all_tracks += tracks['items']
        return all_tracks

    def _get_playlist_with_existing_name(self, playlist_name):
        all_playlists = self.sp.user_playlists(self.sp.me()['id'])['items']
        names_matched = [pl for pl in all_playlists if pl['name'] == playlist_name]
        if names_matched:
            return names_matched[0]

    def _delete_all_songs_from_playlist(self, playlist):
        all_songs = self._get_all_songs_from_playlist(playlist)
        song_ids = [song['track']['id'] for song in all_songs]
        self.sp.user_playlist_remove_all_occurrences_of_tracks(self.username, playlist['id'], song_ids)


def get_spotipy_token(config):
    token = util.prompt_for_user_token(config['REMOVER_PARAMS']['username'],
                                       client_id=config['SPOTIPY_DEV_PARAMETERS']['CLIENT_ID'],
                                       client_secret=config['SPOTIPY_DEV_PARAMETERS']['CLIENT_SECRET'],
                                       redirect_uri=config['SPOTIPY_DEV_PARAMETERS']['REDIRECT_URI'],
                                       scope=SpotifyRemixRemover.REQUIRED_SCOPE)
    if token:
        return token
    else:
        print("Could not get the Spotify Api Access token")
        sys.exit(1)


def get_enabled_words(config):
    enabled_words = [bad_word for bad_word in config['BANNED_KEYWORDS'].keys() if config['BANNED_KEYWORDS'][bad_word]]
    return enabled_words


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(CONFIG_FILENAME)
    banned_keywords = get_enabled_words(config)
    spotipy_token = get_spotipy_token(config)
    remix_remover = SpotifyRemixRemover(config['REMOVER_PARAMS']["USERNAME"],
                                        banned_keywords,
                                        spotipy_token,
                                        config['REMOVER_PARAMS']['RELEASE_PLAYLIST_NAME'])

    remix_remover.run_removal_process(config["REMOVER_PARAMS"]['REMIX_FREE_PLAYLIST_NAME'],
                                      bool(config['REMOVER_PARAMS']['REPLACE_OLD_SONGS']))
