import select

from .utils import iterate_forever


class PlayerCallbacks(object):
    """Interface for Player Callbacks

    This class simply exists to document the interface for callback
    implementers implementers need not extend this class.
    """

    def play(self, song):
        """Called once when a song starts playing
        """
        pass

    def pre_poll(self):
        """Called before polling for process status
        """
        pass

    def post_poll(self):
        """Called after polling for process status
        """
        pass

    def input(self, value, song):
        """Called after user input during song playback
        """
        pass


class Player(object):
    """Implementation Independent Player Logic

    Provides a player interface by wrapping a back-end that actually does the
    song playing.
    """

    def __init__(self, callbacks, control_channel, backend):
        """Create a player instance

        Callbacks is an class implementing the PlayerCallbacks interface.
        Control channel is a file-like object that will provide commands to the
        player instance.
        """
        self._interesting_fds = [control_channel]
        self._control_fd = control_channel.fileno()
        self._callbacks = callbacks
        self._backend = backend
        self._backend.ensure_started(self._interesting_fds)

    def _is_control_channel(self, fd):
        """Determines if channel is control channel
        """
        return fd.fileno() == self._control_fd

    def _poll(self, song):
        """Poll control channel and optionally other fds

        Will pass input to input callback otherwise returns input to player
        loop for handling.
        """
        readers, _, _ = select.select(self._interesting_fds, [], [], 1)

        for fd in readers:
            value = fd.readline().strip()

            if self._is_control_channel(fd):
                self._callbacks.input(value, song)
            else:
                self._backend.handle_message(value)

    def play(self, song):
        """Play a new song from a Pandora model

        Returns once the stream starts but does not shut down the remote mpg123
        process. Calls the input callback when the user has input. Back-ends
        can abort playback by raising a StopIteration exception.
        """
        self._callbacks.play(song)
        self._backend.play(song.audio_url)

        while True:
            try:
                self._callbacks.pre_poll()
                self._backend.ensure_started(self._interesting_fds)

                try:
                    self._poll(song)
                except StopIteration:
                    return
            finally:
                self._callbacks.post_poll()

    def stop(self):
        """Stop the currently playing song
        """
        self._backend.stop()

    def pause(self):
        """Pause the currently playing song
        """
        self._backend.pause()

    def end_station(self):
        """Stop playing the station
        """
        raise StopIteration

    def play_station(self, station):
        """Play the station until something ends it

        This function will run forever until termintated by calling
        end_station.
        """
        for song in iterate_forever(station.get_playlist):
            try:
                self.play(song)
            except StopIteration:
                self.stop()
                return
