import struct
import logging
from typing import Optional

import gevent
from gevent import socket
from gevent import queue
from gevent import event
from gevent.select import select as gselect

logger = logging.getLogger("Connection")


class Connection(object):
    MAGIC = b'VT01'
    FMT = '<I4s'
    FMT_SIZE = struct.calcsize(FMT)

    def __init__(self):
        # Assigned to a real ``gevent.socket`` inside subclass
        # ``_new_socket`` implementations; ``None`` on init means
        # "not connected yet".  Access sites below narrow via
        # ``assert self.socket is not None`` before touching any
        # socket attribute so the ``Optional`` type flows cleanly
        # through Pylance without a bunch of casts.
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.server_addr = None

        self._reader = None
        self._writer = None
        self._readbuf = b''
        self.send_queue = queue.Queue()
        self.recv_queue = queue.Queue()

        self.event_connected = event.Event()

    @property
    def local_address(self):
        assert self.socket is not None, "local_address called before connect()"
        return self.socket.getsockname()[0]

    def connect(self, server_addr):
        self._new_socket()

        logger.debug("Attempting connection to %s", str(server_addr))

        try:
            self._connect(server_addr)
        except socket.error:
            return False

        self.server_addr = server_addr
        # gevent's ``Queue.queue`` is a ``deque`` at runtime but its
        # stubs expose it as a ``property``; ``.clear()`` works fine
        # in practice but static-analysis can't see through the
        # descriptor.  Suppression is scoped tight to this single
        # attribute chain.
        self.recv_queue.queue.clear()  # pyright: ignore[reportAttributeAccessIssue]

        self._reader = gevent.spawn(self._reader_loop)
        self._writer = gevent.spawn(self._writer_loop)

        logger.debug("Connected.")
        self.event_connected.set()
        return True

    def disconnect(self):
        if not self.event_connected.is_set():
            return
        self.event_connected.clear()

        self.server_addr = None

        if self._reader:
            self._reader.kill(block=False)
            self._reader = None
        if self._writer:
            self._writer.kill(block=False)
            self._writer = None

        self._readbuf = b''
        # Same gevent-stub descriptor issue as the ``connect`` site
        # above — see the comment there.
        self.send_queue.queue.clear()  # pyright: ignore[reportAttributeAccessIssue]
        self.recv_queue.queue.clear()  # pyright: ignore[reportAttributeAccessIssue]
        self.recv_queue.put(StopIteration)

        assert self.socket is not None, "disconnect() reached with no live socket"
        self.socket.close()

        logger.debug("Disconnected.")

    def __iter__(self):
        return self.recv_queue

    def put_message(self, message):
        self.send_queue.put(message)

    # ─── template-method stubs ────────────────────────────────────
    # ``TCPConnection`` / ``UDPConnection`` override these to fill in
    # the socket-family-specific behaviour.  Base defaults raise so a
    # direct ``Connection()`` instantiation surfaces the mistake
    # loudly, and Pylance can see the attributes exist on the base
    # class (silences ``reportAttributeAccessIssue`` at the four
    # call sites in ``connect`` / ``_reader_loop`` / ``_writer_loop``
    # below).
    def _new_socket(self) -> None:
        raise NotImplementedError

    def _connect(self, server_addr) -> None:
        raise NotImplementedError

    def _read_data(self) -> bytes:
        raise NotImplementedError

    def _write_data(self, data: bytes) -> None:
        raise NotImplementedError

    def _writer_loop(self):
        while True:
            message = self.send_queue.get()
            packet = struct.pack(Connection.FMT, len(message), Connection.MAGIC) + message
            try:
                self._write_data(packet)
            except:
                logger.debug("Connection error (writer).")
                self.disconnect()
                return

    def _reader_loop(self):
        while True:
            rlist, _, _ = gselect([self.socket], [], [])

            if self.socket in rlist:
                data = self._read_data()

                if not data:
                    logger.debug("Connection error (reader).")
                    self.disconnect()
                    return

                self._readbuf += data
                self._read_packets()

    def _read_packets(self):
        header_size = Connection.FMT_SIZE
        buf = self._readbuf

        while len(buf) > header_size:
            message_length, magic = struct.unpack_from(Connection.FMT, buf)

            if magic != Connection.MAGIC:
                logger.debug("invalid magic, got %s" % repr(magic))
                self.disconnect()
                return

            packet_length = header_size + message_length

            if len(buf) < packet_length:
                return

            message = buf[header_size:packet_length]
            buf = buf[packet_length:]

            self.recv_queue.put(message)

        self._readbuf = buf


class TCPConnection(Connection):
    def _new_socket(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _connect(self, server_addr) -> None:
        assert self.socket is not None, "_connect called before _new_socket"
        self.socket.connect(server_addr)

    def _read_data(self) -> bytes:
        assert self.socket is not None, "_read_data called before _new_socket"
        try:
            return self.socket.recv(16384)
        except socket.error:
            # Returning ``b''`` (bytes) — NOT ``''`` (str) — so the
            # caller's ``self._readbuf += data`` in ``_reader_loop``
            # doesn't blow up mixing bytes + str.
            return b''

    def _write_data(self, data: bytes) -> None:
        assert self.socket is not None, "_write_data called before _new_socket"
        self.socket.sendall(data)


class UDPConnection(Connection):
    def _new_socket(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _connect(self, server_addr) -> None:
        pass

    def _read_data(self) -> bytes:
        # No datagram handling yet — return an empty payload so the
        # reader loop bails out cleanly rather than raising.
        return b''

    def _write_data(self, data: bytes) -> None:
        pass
