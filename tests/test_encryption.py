import sys
import pytest
from unittest import mock
from unittest.mock import patch, mock_open
from Crypto.Cipher import AES
import base64

if "ucryptolib" not in sys.modules:
    sys.modules["ucryptolib"] = mock.MagicMock(
        aes=AES.new, MODE_ECB=AES.MODE_ECB, MODE_CBC=AES.MODE_CBC
    )

TEST_KEY = "test key"
TEST_MNEMONIC_ID = "test ID"
ITERATIONS = 1000
TEST_WORDS = (
    "crush inherit small egg include title slogan mom remain blouse boost bonus"
)
ECB_WORDS = "brass creek fuel snack era success impulse dirt caution purity lottery lizard boil festival neither case swift smooth range mail gravity sample never ivory"
CBC_WORDS = "dog guitar hotel random owner gadget salute riot patrol work advice panic erode leader pass cross section laundry elder asset soul scale immune scatter"

ECB_ENCRYPTED_WORDS = "1NV55l0ny9vkFV6s4MnDvDlpiWUJo35sv5hs6ZKp4T0zVrOxXft8E/RLX9unZJJwii2/crVgr+XE/lAgWhL7YoKYtimDmbpdOFK9U84+3bE="
CBC_ENCRYPTED_WORDS = "pJy/goOD11Nulfzd07PPKCOuPWsy2/tONwHrpY/AihVDcGxmIgzasyhs3fY90E0khrCqqgCvzjukMCdxif2OljKDxZQPGoVNeJKqE4nu5fq5023WhO1yKtAcPt3mML6Q"

ECB_ENCRYPTED_QR = b"\x07test ID\x00\x00\x00\n*\xe1\x9d\xc5\x82\xc1\x19\x9b\xb7&\xf2?\x03\xc7o\xf6\xaf\x9e\x81#F,Qs\xe6\x1d\xeb\xd1Y\xa0/\xcf"
CBC_ENCRYPTED_QR = b"\x07test ID\x01\x00\x00\n\xf3<k\xc1Qn\x95`hrs],^R\x9b\xfa\xec\xfe4\x9e\xf1\xaaT\x8f\xdan<,\xa7\x87Pm\xd8\x80\xd7\x15@\x95\xeb\xc1\xdb\xcd\xb2\xfc\xf7 \x8e"

ECB_QR_PUBLIC_DATA = (
    "Encrypted QR Code:\nID: test ID\nVersion: AES-ECB\nKey iter.: 100000"
)
CBC_QR_PUBLIC_DATA = (
    "Encrypted QR Code:\nID: test ID\nVersion: AES-CBC\nKey iter.: 100000"
)

SEEDS_JSON = """{
    "ecbID": {
        "version": 0,
        "key_iterations": 100000,
        "data": "sMCvAUvVpGSCsXsBl7EBNGPZLymZoyB8eAUHb2TMbarhqD4GJga/SW/AstxIvZz6MR1opXLfF7Pyd+IJBe3E0lDQCkvqytSQfVGnVSeYz+sNfd5T1CXS0/C2zYKTKFL7RTpHd0IXHZ+GQuzX1hoJMHkh0sx0VgorVdDj87ykUQIeC95MS98y/ha2q/vWfLyIZU1hc5VcehzmTA1B6ExMGA=="
    },
    "cbcID": {
        "version": 1,
        "key_iterations": 100000,
        "data": "GpNxj9kzdiTuIf1UYC6R0FHoUokBhiNLkxWgSOHBhmBHb0Ew8wk1M+VlsR4v/koCfSGOTkgjFshC36+n7mx0W0PI6NizAoPClO8DUVamd5hS6irS+Lfff0//VJWK1BcdvOJjzYw8TBiVaL1swAEEySjn5GsqF1RaJXzAMMgu03Kq32iDIDy7h/jHJTiIPCoVQAle/C9vXq2HQeVx43c0LhGXTZmIhhkHPMgDzFTsMGM="
    }
}"""

ECB_ONLY_JSON = """{"ecbID": {"version": 0, "key_iterations": 100000, "data": "sMCvAUvVpGSCsXsBl7EBNGPZLymZoyB8eAUHb2TMbarhqD4GJga/SW/AstxIvZz6MR1opXLfF7Pyd+IJBe3E0lDQCkvqytSQfVGnVSeYz+sNfd5T1CXS0/C2zYKTKFL7RTpHd0IXHZ+GQuzX1hoJMHkh0sx0VgorVdDj87ykUQIeC95MS98y/ha2q/vWfLyIZU1hc5VcehzmTA1B6ExMGA=="}}"""
CBC_ONLY_JSON = """{"cbcID": {"version": 1, "key_iterations": 100000, "data": "GpNxj9kzdiTuIf1UYC6R0FHoUokBhiNLkxWgSOHBhmBHb0Ew8wk1M+VlsR4v/koCfSGOTkgjFshC36+n7mx0W0PI6NizAoPClO8DUVamd5hS6irS+Lfff0//VJWK1BcdvOJjzYw8TBiVaL1swAEEySjn5GsqF1RaJXzAMMgu03Kq32iDIDy7h/jHJTiIPCoVQAle/C9vXq2HQeVx43c0LhGXTZmIhhkHPMgDzFTsMGM="}}"""
I_VECTOR = b"OR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e"


@pytest.fixture
def mock_file_operations(mocker):
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data=SEEDS_JSON))


def test_ecb_encryption(m5stickv):
    from krux.encryption import AESCipher

    encryptor = AESCipher(TEST_KEY, TEST_MNEMONIC_ID, ITERATIONS)
    encrypted = encryptor.encrypt(TEST_WORDS, AES.MODE_ECB).decode("utf-8")
    assert encrypted == ECB_ENCRYPTED_WORDS
    decrypted = encryptor.decrypt(base64.b64decode(encrypted), AES.MODE_ECB)
    assert decrypted == TEST_WORDS


def test_cbc_encryption(m5stickv):
    from krux.encryption import AESCipher
    from Crypto.Random import get_random_bytes

    encryptor = AESCipher(TEST_KEY, TEST_MNEMONIC_ID, ITERATIONS)
    iv = get_random_bytes(AES.block_size)
    encrypted = encryptor.encrypt(TEST_WORDS, AES.MODE_CBC, iv).decode("utf-8")
    assert encrypted == CBC_ENCRYPTED_WORDS
    data = base64.b64decode(encrypted)
    encrypted_mnemonic = data[AES.block_size :]
    i_vector = data[: AES.block_size]
    decrypted = encryptor.decrypt(encrypted_mnemonic, AES.MODE_CBC, i_vector)
    assert decrypted == TEST_WORDS


def test_list_mnemonic_storage(m5stickv, mock_file_operations):
    from krux.encryption import MnemonicStorage

    storage = MnemonicStorage()
    assert storage.has_sd_card is True
    flash_list = storage.list_mnemonics(sd_card=False)
    sd_list = storage.list_mnemonics(sd_card=True)
    assert "ecbID" and "cbcID" in flash_list
    assert "ecbID" and "cbcID" in sd_list


def test_load_decrypt_ecb(m5stickv, mock_file_operations):
    from krux.encryption import MnemonicStorage

    storage = MnemonicStorage()
    words = storage.decrypt(TEST_KEY, "ecbID", sd_card=False)
    words_sd = storage.decrypt(TEST_KEY, "ecbID", sd_card=True)
    assert words == ECB_WORDS
    assert words_sd == ECB_WORDS


def test_load_decrypt_cbc(m5stickv, mock_file_operations):
    from krux.encryption import MnemonicStorage

    storage = MnemonicStorage()
    words = storage.decrypt(TEST_KEY, "cbcID", sd_card=False)
    words_sd = storage.decrypt(TEST_KEY, "cbcID", sd_card=True)
    assert words == CBC_WORDS
    assert words_sd == CBC_WORDS


def test_encrypt_ecb_flash(mocker):
    from krux.krux_settings import Settings
    from krux.encryption import MnemonicStorage

    with patch("krux.encryption.open", new=mocker.mock_open(read_data="{}")) as m:
        storage = MnemonicStorage()
        Settings().encryption.version = "AES-ECB"
        success = storage.store_encrypted(TEST_KEY, "ecbID", ECB_WORDS, sd_card=False)
    assert success is True
    m().write.assert_called_once_with(ECB_ONLY_JSON)


def test_encrypt_cbc_flash(mocker):
    from krux.krux_settings import Settings
    from krux.encryption import MnemonicStorage

    with patch("krux.encryption.open", new=mocker.mock_open(read_data="{}")) as m:
        storage = MnemonicStorage()
        Settings().encryption.version = "AES-CBC"
        success = storage.store_encrypted(
            TEST_KEY, "cbcID", CBC_WORDS, sd_card=False, i_vector=I_VECTOR
        )
    assert success is True
    m().write.assert_called_once_with(CBC_ONLY_JSON)


def test_encrypt_ecb_sd(mocker, mock_file_operations):
    from krux.krux_settings import Settings
    from krux.encryption import MnemonicStorage

    with patch("krux.sd_card.open", new=mocker.mock_open(read_data="{}")) as m:
        storage = MnemonicStorage()
        Settings().encryption.version = "AES-ECB"
        success = storage.store_encrypted(TEST_KEY, "ecbID", ECB_WORDS, sd_card=True)
    assert success is True
    m().write.assert_called_once_with(ECB_ONLY_JSON)


def test_encrypt_cbc_sd(mocker, mock_file_operations):
    from krux.krux_settings import Settings
    from krux.encryption import MnemonicStorage

    with patch("krux.sd_card.open", new=mocker.mock_open(read_data="{}")) as m:
        storage = MnemonicStorage()
        Settings().encryption.version = "AES-CBC"
        success = storage.store_encrypted(
            TEST_KEY, "cbcID", CBC_WORDS, sd_card=True, i_vector=I_VECTOR
        )
    assert success is True
    m().write.assert_called_once_with(CBC_ONLY_JSON)


def test_delet_from_flash(mocker):
    from krux.encryption import MnemonicStorage

    # Loads a file with 2 mnemonics, one with ID="ecbID", other with ID="cbcID"
    # Deletes "ecbID" and assures only "cbcID" is left
    with patch("krux.encryption.open", new=mocker.mock_open(read_data=SEEDS_JSON)) as m:
        storage = MnemonicStorage()
        storage.del_mnemonic("ecbID")
    m().write.assert_called_once_with(CBC_ONLY_JSON)


def test_delet_from_sd(mocker, mock_file_operations):
    from krux.encryption import MnemonicStorage

    # Loads a file with 2 mnemonics, one with ID="ecbID", other with ID="cbcID"
    # Deletes "ecbID" and assures only "cbcID" is left
    with patch("krux.sd_card.open", new=mocker.mock_open(read_data=SEEDS_JSON)) as m:
        storage = MnemonicStorage()
        storage.del_mnemonic("ecbID", sd_card=True)
    m().write.assert_called_once_with(CBC_ONLY_JSON)


def test_create_ecb_encrypted_qr_code():
    from krux.encryption import EncryptedQRCode
    from krux.krux_settings import Settings

    Settings().encryption.version = "AES-ECB"
    encrypted_qr = EncryptedQRCode()
    qr_data = encrypted_qr.create(TEST_KEY, TEST_MNEMONIC_ID, TEST_WORDS)
    assert qr_data == ECB_ENCRYPTED_QR


def test_create_cbc_encrypted_qr_code():
    from krux.encryption import EncryptedQRCode
    from krux.krux_settings import Settings

    Settings().encryption.version = "AES-CBC"
    encrypted_qr = EncryptedQRCode()
    qr_data = encrypted_qr.create(TEST_KEY, TEST_MNEMONIC_ID, TEST_WORDS, I_VECTOR)
    print(qr_data)
    assert qr_data == CBC_ENCRYPTED_QR


def test_decode_ecb_encrypted_qr_code():
    from krux.encryption import EncryptedQRCode
    from embit import bip39

    encrypted_qr = EncryptedQRCode()
    public_data = encrypted_qr.public_data(ECB_ENCRYPTED_QR)
    assert public_data == ECB_QR_PUBLIC_DATA
    word_bytes = encrypted_qr.decrypt(TEST_KEY)
    words = bip39.mnemonic_from_bytes(word_bytes)
    assert words == TEST_WORDS


def test_decode_cbc_encrypted_qr_code():
    from krux.encryption import EncryptedQRCode
    from embit import bip39

    encrypted_qr = EncryptedQRCode()
    public_data = encrypted_qr.public_data(CBC_ENCRYPTED_QR)
    print(public_data)
    assert public_data == CBC_QR_PUBLIC_DATA
    word_bytes = encrypted_qr.decrypt(TEST_KEY)
    words = bip39.mnemonic_from_bytes(word_bytes)
    assert words == TEST_WORDS


from .shared_mocks import mock_context


def create_ctx(mocker, btn_seq, touch_seq=None):
    """Helper to create mocked context obj"""
    ctx = mock_context(mocker)
    ctx.power_manager.battery_charge_remaining.return_value = 1
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=btn_seq)

    if touch_seq:
        ctx.input.touch = mocker.MagicMock(
            current_index=mocker.MagicMock(side_effect=touch_seq)
        )
    return ctx


def test_load_key_from_keypad(m5stickv, mocker):
    from krux.pages.encryption_key import EncryptionKey
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        [BUTTON_ENTER]  # choose to type key
        + [BUTTON_PAGE]  # go to letter b
        + [BUTTON_ENTER]  # enter letter b
        + [BUTTON_PAGE_PREV] * 2  # move to "Go"
        + [BUTTON_ENTER]  # Go
        + [BUTTON_ENTER]  # Confirm
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    key_generator = EncryptionKey(ctx)
    key = key_generator.encryption_key()
    assert key == "b"


def test_load_key_from_qr_code(m5stickv, mocker):
    from krux.pages.encryption_key import EncryptionKey, ENCRYPTION_KEY_MAX_LEN
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    BTN_SEQUENCE = (
        [BUTTON_PAGE]  # move to QR code key
        + [BUTTON_ENTER]  # choose QR code key
        + [BUTTON_ENTER]  # Confirm
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    key_generator = EncryptionKey(ctx)
    mocker.patch.object(
        key_generator,
        "capture_qr_code",
        mocker.MagicMock(return_value=(("qr key", None))),
    )
    key = key_generator.encryption_key()
    assert key == "qr key"

    # Repeat with too much characters >ENCRYPTION_KEY_MAX_LEN
    BTN_SEQUENCE = [BUTTON_PAGE] + [  # move to QR code key
        BUTTON_ENTER
    ]  # choose QR code key
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    key_generator = EncryptionKey(ctx)
    too_long_text = "l" * (ENCRYPTION_KEY_MAX_LEN + 1)
    mocker.patch.object(
        key_generator,
        "capture_qr_code",
        mocker.MagicMock(return_value=((too_long_text, None))),
    )
    key = key_generator.encryption_key()
    assert key == None
