from .. import create_ctx
from .test_home import tdata
import pytest


@pytest.fixture
def mock_save_file(mocker):
    mocker.patch(
        "krux.pages.home_pages.pub_key_view.PubkeyView.has_sd_card", return_value=True
    )
    return mocker.patch("krux.pages.file_operations.SaveFile.save_file")


@pytest.fixture
def mock_seed_qr_view(mocker):
    return mocker.patch("krux.pages.qr_view.SeedQRView")


def test_public_key_show_text(mocker, m5stickv, tdata):
    from krux.pages.home_pages.pub_key_view import PubkeyView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    btn_sequence = [
        BUTTON_ENTER,  # Enter XPUB - text
        BUTTON_PAGE,  # move to Back
        BUTTON_ENTER,  # Press Back
        *([BUTTON_PAGE] * 2),  # move to ZPUB/YPUB - text
        BUTTON_ENTER,  # Enter ZPUB/YPUB - text
        BUTTON_PAGE,  # move to Back
        BUTTON_ENTER,  # Press Back
        BUTTON_PAGE_PREV,  # Move to Back
        BUTTON_ENTER,  # exit
    ]

    cases = [
        # Case parameters: [Wallet, Printer, Button Sequence, Show XPUB, Show ZPUB, Show YPUB, Test SD Save]
        # 0 - Singlesig - Show all text and QR codes
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            btn_sequence,
        ),
        # 1 - Multisig - Show all text and QR codes
        (
            Wallet(tdata.MULTISIG_12_WORD_KEY),
            btn_sequence,
        ),
        # 2 - Singlesig Nested Segwit - Show all text and QR codes
        (
            Wallet(tdata.NESTEDSW1_KEY),
            btn_sequence,
        ),
    ]

    for case in cases:

        ctx = create_ctx(mocker, case[1], case[0], None)
        pub_key_viewer = PubkeyView(ctx)

        mocker.patch.object(ctx.display, "FONT_HEIGHT", 14)
        mocker.spy(ctx.display, "clear")
        mocker.spy(ctx.display, "draw_hcentered_text")

        pub_key_viewer.public_key()

        # Build expected QR view calls
        clear_calls = []
        draw_text_calls = []

        clear_calls.append(mocker.call())
        draw_text_calls.append(
            mocker.call(
                "\n\n"
                + ctx.wallet.key.derivation_str(pretty=True)
                + "\n\n"
                + ctx.wallet.key.account_pubkey_str(None),
                offset_y=ctx.display.FONT_HEIGHT,
                info_box=True,
            ),
        )
        ctx.display.clear.assert_has_calls(clear_calls, any_order=True)
        ctx.display.draw_hcentered_text.assert_has_calls(
            draw_text_calls, any_order=True
        )


def test_public_key_show_qrcode(
    mocker,
    m5stickv,
    tdata,
    mock_seed_qr_view,
):
    from krux.pages.home_pages.pub_key_view import PubkeyView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.key import TYPE_MULTISIG

    btn_sequence = [
        BUTTON_PAGE,  # move to XPUB - QR Code
        BUTTON_ENTER,  # Enter XPUB - QR Code
        BUTTON_ENTER,  # exit the qrcode and enter in QR Menu
        BUTTON_PAGE_PREV,  # move to Back to Menu
        BUTTON_ENTER,  # Press Back to Menu
        *([BUTTON_PAGE] * 3),  # move to ZPUB/YPUB - QR Code
        BUTTON_ENTER,  # Enter ZPUB/YPUB - QR code
        BUTTON_ENTER,  # exit the qrcode and enter in QR Menu
        BUTTON_PAGE_PREV,  # move to Back to Menu
        BUTTON_ENTER,  # Press Back to Menu
        BUTTON_PAGE_PREV,  # Move Back
        BUTTON_ENTER,  # Press Back to leave
    ]

    cases = [
        # Case parameters: [Wallet, Printer, Button Sequence, Show XPUB, Show ZPUB, Show YPUB, Test SD Save]
        # 0 - Singlesig - Show all text and QR codes
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            btn_sequence,
            True,
            True,
            False,
        ),
        # 1 - Multisig - Show all text and QR codes
        (
            Wallet(tdata.MULTISIG_12_WORD_KEY),
            btn_sequence,
            True,
            True,
            False,
        ),
        # 2 - Singlesig Nested Segwit - Show all text and QR codes
        (
            Wallet(tdata.NESTEDSW1_KEY),
            btn_sequence,
            False,
            False,
            True,
        ),
    ]

    for case in cases:

        ctx = create_ctx(mocker, case[1], case[0], None)
        pub_key_viewer = PubkeyView(ctx)

        pub_key_viewer.public_key()

        # Build expected QR view calls
        qr_view_calls = []

        if case[2]:  # Show XPUB
            qr_view_calls.append(
                mocker.call(
                    ctx,
                    data=ctx.wallet.key.key_expression(None),
                    title="XPUB",
                ),
            )

        if case[3]:  # Show ZPUB
            version = "Zpub" if ctx.wallet.key.policy_type == TYPE_MULTISIG else "zpub"
            zpub = ctx.wallet.key.key_expression(ctx.wallet.key.network[version])
            qr_view_calls.append(
                mocker.call(
                    ctx,
                    data=zpub,
                    title="ZPUB",
                ),
            )

        if case[4]:  # Show YPUB
            version = "Ypub" if ctx.wallet.key.policy_type == TYPE_MULTISIG else "ypub"
            ypub = ctx.wallet.key.key_expression(ctx.wallet.key.network[version])
            qr_view_calls.append(
                mocker.call(
                    ctx,
                    data=ypub,
                    title="YPUB",
                ),
            )

        mock_seed_qr_view.assert_has_calls(qr_view_calls, any_order=True)
        assert ctx.input.wait_for_button.call_count == len(case[1])


def test_public_key_save_text(
    mocker,
    m5stickv,
    tdata,
    mock_save_file,
):
    from krux.pages.home_pages.pub_key_view import PubkeyView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.key import TYPE_MULTISIG

    btn_sequence = [
        BUTTON_ENTER,  # Enter XPUB - Text
        BUTTON_ENTER,  # Enter Save to SD Card
        BUTTON_ENTER,  # Accept Save to SD Card
        BUTTON_PAGE_PREV,  # Move to Go
        BUTTON_ENTER,  # Press Go
        *([BUTTON_PAGE] * 2),  # Move to ZPUB/YPUB - text
        BUTTON_ENTER,  # Enter ZPUB/YPUB - text
        BUTTON_ENTER,  # Enter Save to SD card
        BUTTON_ENTER,  # Accept Save to SD Card
        BUTTON_PAGE_PREV,  # Move to Go
        BUTTON_ENTER,  # Press Go
        BUTTON_PAGE_PREV,  # Move Back
        BUTTON_ENTER,  # Press Back to leave
    ]

    cases = [
        # Case parameters: [Wallet, Printer, Button Sequence, Show XPUB, Show ZPUB, Show YPUB]
        # 0 - Singlesig - Save XPUB and ZPUB to SD card
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            btn_sequence,
            True,
            True,
            False,
        ),
        # 1 - Multisig - Save XPUB and ZPUB to SD card
        (
            Wallet(tdata.MULTISIG_12_WORD_KEY),
            btn_sequence,
            True,
            True,
            False,
        ),
        # 2 - Nested Segwit - Save XPUB and YPUB to SD card
        (
            Wallet(tdata.NESTEDSW1_KEY),
            btn_sequence,
            True,
            False,
            True,
        ),
    ]

    num = 0
    for case in cases:
        print(f"Running case {num}")
        num += 1
        ctx = create_ctx(mocker, case[1], case[0], None)
        pub_key_viewer = PubkeyView(ctx)

        mocker.patch.object(ctx.display, "FONT_HEIGHT", 14)
        mocker.spy(ctx.display, "clear")
        mocker.spy(ctx.display, "draw_hcentered_text")

        pub_key_viewer.public_key()

        # Build expected QR view calls
        clear_calls = []
        draw_text_calls = []
        sd_card_save_calls = []

        clear_calls.append(mocker.call())
        if case[2]:  # Show XPUB
            sd_card_save_calls.append(
                mocker.call(
                    ctx.wallet.key.key_expression(None),
                    "XPUB",
                    "XPUB",
                    "XPUB:",
                    ".pub",
                    save_as_binary=False,
                )
            )

        if case[3]:  # Show ZPUB
            version = "Zpub" if ctx.wallet.key.policy_type == TYPE_MULTISIG else "zpub"
            sd_card_save_calls.append(
                mocker.call(
                    ctx.wallet.key.key_expression(ctx.wallet.key.network[version]),
                    "ZPUB",
                    "ZPUB",
                    "ZPUB:",
                    ".pub",
                    save_as_binary=False,
                )
            )

        if case[4]:  # Show YPUB
            version = "Ypub" if ctx.wallet.key.policy_type == TYPE_MULTISIG else "ypub"
            sd_card_save_calls.append(
                mocker.call(
                    ctx.wallet.key.key_expression(ctx.wallet.key.network[version]),
                    "YPUB",
                    "YPUB",
                    "YPUB:",
                    ".pub",
                    save_as_binary=False,
                )
            )

        draw_text_calls.append(
            mocker.call(
                "\n\n"
                + ctx.wallet.key.derivation_str(pretty=True)
                + "\n\n"
                + ctx.wallet.key.account_pubkey_str(None),
                offset_y=ctx.display.FONT_HEIGHT,
                info_box=True,
            ),
        )

        mock_save_file.assert_has_calls(sd_card_save_calls, any_order=True)
        ctx.display.clear.assert_has_calls(clear_calls, any_order=True)
        ctx.display.draw_hcentered_text.assert_has_calls(
            draw_text_calls, any_order=True
        )
        assert ctx.input.wait_for_button.call_count == len(case[1])
