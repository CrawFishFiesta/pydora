from .utils import SilentPopen


class MPG123BackEnd(object):
    """Remote control for an mpg123 process

    Starts and owns a handle to an mpg123 process then feeds commands to it to
    play pandora audio
    """

    def __init__(self):
        self._process = None

    def __del__(self):
        """Cleanup player process on destruction
        """
        self._process.kill()

    def ensure_started(self, interesting_fds):
        """Ensure mpg123 is started
        """
        if self._process and self._process.poll() is None:
            return

        self._process = SilentPopen(
            ["mpg123", "-q", "-R", "--ignore-mime"])

        interesting_fds.append(self._process.stdout)

        # Only output play status in the player stdout
        self._send_cmd("silence")

    def _send_cmd(self, cmd):
        """Write command to remote mpg123 process
        """
        self._process.stdin.write("{}\n".format(cmd).encode("utf-8"))
        self._process.stdin.flush()

    def _player_is_stopped(self, value):
        """Determine if player has stopped
        """
        return value.startswith(b"@P") and value.decode("utf-8")[3] == "0"

    def stop(self):
        """Stop the currently playing song
        """
        self._send_cmd("stop")

    def pause(self):
        """Pause the player
        """
        self._send_cmd("pause")

    def play(self, url):
        """Start playing a track
        """
        self._send_cmd("load {}".format(url))

    def handle_message(self, message):
        """Handle a message from the player front-end
        """
        if self._player_is_stopped(message):
            raise StopIteration


# /Applications/VLC.app/Contents/MacOS/VLC \
#       --intf http --http-host 127.0.0.1 --http-port 9090 --http-password 123

class VLCBackEnd(object):
    """Remote control for a VLC process

    Starts and owns a handle to an VLC process then feeds commands to it to
    play pandora audio
    """

    def __init__(self):
        self._process = None

    def __del__(self):
        """Cleanup player process on destruction
        """
        self._process.kill()

    def ensure_started(self, interesting_fds):
        """Ensure mpg123 is started
        """
        if self._process and self._process.poll() is None:
            return

        self._process = SilentPopen(
            ["mpg123", "-q", "-R", "--ignore-mime"])

    def stop(self):
        """Stop the currently playing song
        """
        pass

    def pause(self):
        """Pause the player
        """
        pass

    def play(self, url):
        """Play the player
        """
        pass

    def handle_message(self, message):
        """Handle a message from the player back-end
        """
        if self._player_stopped(message):
            raise StopIteration
