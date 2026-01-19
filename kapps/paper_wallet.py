# The MIT License (MIT)


# Copyright (c) 2021-2026 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# -------------------
import os

# avoids importing from flash VSF
os.chdir("/")

try:
    import uhashlib_hw as hashlib
except ImportError:
    import hashlib

try:
    from ucryptolib import aes, hmac
except ImportError:
    from cryptolib import aes, hmac

from embit import ec, script

from krux.baseconv import base_encode
from krux.encryption_ui import OVERRIDE_LABEL
from krux.display import (
    BOTTOM_PROMPT_LINE,
    DEFAULT_PADDING,
    FONT_WIDTH,
    FONT_HEIGHT,
    STATUS_BAR_HEIGHT,
)
from krux.kboard import kboard
from krux.kef import KEFEnvelope
from krux.krux_settings import t, Settings
from krux.pages import Menu, MENU_CONTINUE, MENU_EXIT, LETTERS, DIGITS, ESC_KEY
from krux.pages.login import Login, DIGITS_HEX
from krux.pages.home_pages.home import Home
from krux.settings import ELLIPSIS
from krux.themes import theme

# -------------------

VERSION = "1.0"
NAME = "Paper Wallet"
ALLOW_STARTUP = True


# -------------------
class Utils:

    @staticmethod
    def csprng(key, length):
        """Create a secure pseudo random number generator with HMAC"""
        counter = 0
        csprng = bytearray([])
        while len(csprng) < length:
            result = Utils._hmac(key, length, counter)
            csprng.extend(result)
        return bytes(csprng[:length])

    @staticmethod
    def hmac(key, msg, counter=0):
        """Try to apply a hash message authentication code from
        ``uhashlib_hw``; otherwise, use ``hashlib``"""
        msg = counter.to_bytes(4, "big")
        res = hmac.new(key, msg, hashlib.sha512).digest()
        counter += 1
        return res

    @staticmethod
    def hash256(data):
        """Apply ``hashlib.sha256(hashlib.sha256(data))`` The ``hashlib`` used
        could be ``uhashlib_hw`` or ``hashlib`` depending on
        running environment"""
        return hashlib.sha256(hashlib.sha256(data)).digest()

    @staticmethod
    def hash160(data):
        """Apply ``hashlib.ripemd160(hashlib.sha256(data))`` The ``hashlib`` used
        could be ``uhashlib_hw`` or ``hashlib`` depending on
        running environment"""
        return hashlib.ripemd160(hashlib.sha256(data)).digest()

    @staticmethod
    def encode_base58check(decoded):
        hashed = Utils.checksum(decoded)
        decoded.append(hashed)
        return base_encode(decoded, 58)

    @staticmethod
    def checksum(data):
        """Apply a checksum (first four bytes) of a ``Utils.checksum``"""
        return Utils.hash256(data)[:4]


# -------------------
class KBaseWallet:
    """Base class for create a random bitcoin public key pair"""

    WALLET_TYPES = ("single", "paper", "bulk", "brain")

    def __init__(self, wallet_type="single"):
        self._wallet_type = wallet_type

    @property
    def is_wif(self):
        """Getter for ``PaperWallet.is_wif``"""
        return self.wif is not None

    @property
    def wallet_type(self):
        """Getter for ``PaperWallet.wallet_type``"""
        return self._wallet_type

    @staticmethod
    def generate(seed=b"", wif=False):
        """Generate a pseudorandom generated pair of private and public keys,
        as well return a tuple containing this pair in the format
        (base58_private_key, p2pkh_address)"""

        # Now use the captured entropy to create the keypair
        try:
            raw = Utils._csprng(seed, 32)
            _private_key = ec.PrivateKey(raw)
            _wif = _private_key.wif()
            _public_key = _private_key.get_public_key()
            _script = script.p2pkh(_public_key)
            _address = _script.address()

            # now we can convert the ProivateKey to str
            _private_key = _private_key.to_string()
            if wif:
                return _wif
            else:
                return (_address, _private_key)
        except Exception as e:
            print(e)
            raise ValueError(e) from e


# -------------------
class KSingleWallet(KBaseWallet):
    """Represents a Single Wallet ``'<0>, "<address>", "<prvkey>"``'"""

    def __init__(self, seed=b"", wif=False):
        if not wif:
            addr, prvkey = self.generate(seed=seed, wif=wif)
            self.address = addr
            self.private_key = prvkey
            self.wif = None
        else:
            wif = self.generate(seed=seed, wif=wif)
            self.address = None
            self.private_key = None
            self.wif = wif

    def __str__(self):
        """Represents ``KSingleWallet`` as "<n> <address>, <privkey>"
        when  ``KSingleWallet.wif == False, otherwise, as "<wif>"
        in accord to https://www.bitaddress.org.

        It's worth to comment that, in the second format, bitaddress
        do not specify this format.
        """
        if self.private_key is None and self.wif is not None:
            return self._as_wif(0, self.wif)
        return self._as_single_wallet(0, self.address, self.prvkey)

    def __repr__(self):
        """A formated <KSingleWallet ``KSingleWallet.__str__()``>"""
        return "<KSingleWallet {}>".format(self.__str__())

    def __hex__(self):
        """Returns the ``__str__`` checksum"""
        return Utils.checksum(self.to_string())

    def _as_single_wallet(n, address, private_key):
        """Return a ``str`` in the format
        ``'<n>, "<address>", "<private_key>"``
        """
        return '{}, "{}", "{}"'.format(n, address, private_key)

    def _as_wif(self, n, address, wif):
        """Return a ``str`` in the format
        ``'<n>, "<wif>``
        """
        return '{}, "{}"'.format(n, wif)


# -------------------
class KBulkWallet(KSingleWallet):
    """Represents a ``list`` of ``KSingleWallet``"""

    def __init__(self, seeds=[b"", b"", b""], wif=False):
        super().__init__(b"")
        delattr(self, "address")
        delattr(self, "private_keys")
        delattr(self, "wif")
        self.addresses = None
        self.private_keys = None
        self.wifs = None

        if not wif:
            self.addresses = []
            self.private_keys = []
            for seed in seeds:
                wallet = KSingleWallet(seed, wif)
                self.addresses.append(wallet.address)
                self.private_keys.append(wallet.wallet.private_key)

        else:
            self.wifs = []
            for seed in seeds:
                wallet = KSingleWallet(seed, wif)
                self.wifs.append(wallet.wif)

    def __str__(self):
        """Represents ``PaperWallet`` as a set of "<n> <address>, <privkey>"
        when ``BulkWallet.wif == False, otherwise, as "0, "<wif>" in accord to
        https://www.bitaddress.org.

        It's worth to comment that, in the second format, bitaddress
        do not specify this format.
        """
        if self.private_key is None and self.wif is not None:
            return "\n".join([self._as_wif(i, wif) for wif in self.wifs])

        return "\n".join(
            self._as_single_wallet(i, self.addresses[i], self.private_keys[i])
            for i in range(len(self.private_keys))
        )

    def __repr__(self):
        """A formated <KSingleWallet ``KSingleWallet.__str__()``>"""
        return "<KBulkWallet {}>".format(self.__str__())


# -------------------
class KPaperWallet(KBulkWallet):
    """Represents a ``list`` of stylished ``KBulkWallet``"""

    def __init__(self, seeds=[b"", b"", b""], wif=False):
        super().__init__(seeds, wif)

    def __str__(self):
        return self._as_paper_wallet()

    def __repr__(self):
        """A formated <KSingleWallet ``KSingleWallet.__str__()``>"""
        return "<KPaperWallet {}>".format(self)

    def xml_open(self):
        return '<?xml version="1.0" encoding="UTF-8"?>'

    def svg_open(self):
        return """<svg xmlns="http://www.w3.org/2000/svg" width="900" height="450" viewBox="0 0 900 450">"""

    def svg_header(self, title="Paper Wallet"):
        return "".join(
            [
                '<rect x="20" y="20" width="860" height="410" rx="18" fill="#fff" stroke="#111" stroke-width="3"/>',
                '<text x="50" y="80" font-family="monospace" font-size="34" fill="#111">{}</text>'.format(
                    title
                ),
            ]
        )

    def svg_item(self, key, value):
        return "".join(
            [
                '<text x="50" y="140" font-family="monospace" font-size="18" fill="#111">{}</text>'
                '<rect x="50" y="155" width="520" height="55" rx="10" fill="#f7f7f7" stroke="#222" stroke-width="2"/>'
                '<text x="65" y="190" font-family="monospace" font-size="18" fill="#111">{}</text>'.format(
                    key, address
                )
            ]
        )

    def svg_close(self):
        return "</svg>"

    def _as_paper_wallet(self):
        """Return a ``.svg`` string containing a minimal "paper wallet": a card
        with address/privkey text.
        """
        if self.wifs:
            return "".join(
                [
                    self.xml_open(),
                    self.svg_open(),
                    self.svg_header(),
                    "".join(
                        [
                            self.svg_item("WIF #{}".format(i), addr)
                            for i, addr in enumerate(self.wifs)
                        ]
                    ),
                    self.svg_close(),
                ]
            )

        return "".join(
            [
                self.xml_open(),
                self.svg_open(),
                self.svg_header(),
                "".join(
                    [
                        self.svg_item("Address #{}".format(i), addr)
                        for i, addr in enumerate(self.addresses)
                    ]
                ),
                "".join(
                    [
                        self.svg_item("Private key #{}".format(i), private_key)
                        for i, private_key in enumerate(self.private_keys)
                    ]
                ),
                self.svg_close(),
            ]
        )

    def save_to_sd(self, title):
        from ..file_operations import SaveFile, PUBKEY_FILE_EXTENSION

        save_page = SaveFile(self.ctx)
        save_page.save_file(
            self.to_string(),
            title,
            title,
            title + ":",
            PUBKEY_FILE_EXTENSION,
            save_as_binary=False,
        )


# -------------------
class KPaperWalletManager:
    """Manages the wallet type used and should be a single instance"""

    def __init__(self):
        self.wallet = None
        self.wallet_type = None
        self.mode_name = Settings().encryption.version

    @property
    def is_loaded(self):
        """If ``wallet`` is ``None`` then return ``False``,
        otherwise, ``True``"""
        return self.wallet is not None and self.wallet_type is not None

    def checksum(self):
        """Return the calculated checksum of current ``__hex__``"""
        return self.wallet.__hex__()

    def store_paper_wallet_on_memory(self, plaintext, sd_card=False):
        """Save encrypted mnemonic on flash or sd_card"""

        from ..encryption import MnemonicStorage

        encrypted_data, wallet_id = self._encrypt_paper_wallet_with_label(plaintext)
        if encrypted_data is None:
            return

        wallet_storage = MnemonicStorage()
        if wallet_id in wallet_storage.list_mnemonics(sd_card):
            self.flash_error(
                t("ID already exists")
                + "\n"
                + t("Encrypted paper wallet was not stored")
            )
            del wallet_storage
            return

        if wallet_storage.store_encrypted_kef(wallet_id, encrypted_data, sd_card):
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Encrypted paper wallet stored with ID:") + " " + wallet_id,
                highlight_prefix=":",
            )
        else:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Failed to store paper wallet"), theme.error_color
            )
        self.ctx.input.wait_for_button()
        del wallet_storage

    def _encrypt_paper_wallet_with_label(self, plaintext=""):
        """Helper method to encrypt keypair with label selection."""
        kef_envelope = KEFEnvelope(self.ctx)

        # let's obsfuscate the information that the wallet is a paper
        # one throug the checksum of plaintext
        bytestext = plaintext.encode()
        try:
            import uhashlib_hw

            label = uhashlib_hw.sha256(bytestext).digest()[:4].hex()
        except:
            import hashlib

            label = hashlib.sha256(bytestext).digest()[:4].hex()

        kef_envelope.label = label
        encrypted_data = kef_envelope.seal_ui(
            plaintext.encode(),
            overrides=[OVERRIDE_LABEL],
            dflt_label_affirm=True,
        )

        if encrypted_data is None:
            return None, None

        wallet_id = kef_envelope.label
        return encrypted_data, wallet_id


# -------------------
class KMenu(Menu):
    """Customizes the page's menu"""

    def __init__(
        self,
        ctx,
        menu,
        offset=None,
        disable_statusbar=False,
        back_label="Back",
        back_status=lambda: MENU_EXIT,
    ):
        super().__init__(ctx, menu, offset, disable_statusbar, back_label, back_status)
        self.disable_statusbar = False
        if offset is None:
            self.menu_offset = STATUS_BAR_HEIGHT
        else:
            # Always disable status bar if menu has non standard offset
            self.disable_statusbar = True
            self.menu_offset = offset if offset >= 0 else DEFAULT_PADDING

    def new_draw_wallet_indicator(self):
        """Customize the top bar"""
        if not paper_wallet_manager.is_loaded:
            return

        text = NAME
        text = paper_wallet_manager.wallet.checksum() + ELLIPSIS
        if not kboard.is_m5stickv:
            self.ctx.display.draw_hcentered_text(
                text,
                STATUS_BAR_HEIGHT - FONT_HEIGHT - 1,
                theme.highlight_color,
                theme.info_bg_color,
            )
        else:
            self.ctx.display.draw_string(
                24,
                STATUS_BAR_HEIGHT - FONT_HEIGHT - 1,
                text,
                theme.highlight_color,
                theme.info_bg_color,
            )


# -------------------
class Klogin(Login):
    """Page to create o load a Paper wallet"""

    def __init__(self, ctx):
        super().__init__(ctx)
        shtn_reboot_label = t("Shutdown") if kboard.has_battery else t("Reboot")
        self.menu = KMenu(
            ctx,
            [
                (t("Load Paper wallet"), None),
                (t("New Paper wallet"), None),
                (t("About"), None),
                (shtn_reboot_label, self.shutdown),
            ],
            back_label=None,
        )

    def new_paper_wallet(self, wif=False):
        """Render a menu with possible paper wallets:

        - ``SingleWallet``;
        - ``BulkWallet``;
        - ``PaperWallet``.

        All possible wallets offers the WIF format"""
        pass


def run(ctx):
    """Run this kapp"""

    Klogin(ctx).run()
    # if paper_wallet_manager.is_loaded:
    #    Khome(ctx).run()


paper_wallet_manager = KPaperWalletManager()
