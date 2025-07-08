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


@pytest.fixture
def mock_display(mocker):
    return mocker.patch("krux.display.Display.draw_hcentered_text")


def test_public_key_view(
    mocker, m5stickv, tdata, mock_seed_qr_view, mock_save_file, mock_display
):
    from krux.pages.home_pages.pub_key_view import PubkeyView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_NONE
    from krux.key import TYPE_MULTISIG

    cases = [
        # Case parameters: [Wallet, Printer, Button Sequence, Show XPUB, Show ZPUB, Show YPUB, Test SD Save]
        # 0 - Singlesig - Show all text and QR codes
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            None,
            [
                BUTTON_ENTER,  # Enter XPUB - Text
                BUTTON_PAGE,  # move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE,  # move to XPUB - QR Code
                BUTTON_ENTER,  # Enter XPUB - QR Code
                BUTTON_ENTER,  # Enter QR Menu
                BUTTON_PAGE_PREV,  # move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE,  # move to XPUB - QR Code
                BUTTON_PAGE,  # move to ZPUB - Text
                BUTTON_PAGE,  # move to ZPUB - QR Code
                BUTTON_ENTER,  # Enter ZPUB - QR Code
                BUTTON_ENTER,  # Enter QR Menu
                BUTTON_PAGE_PREV,  # move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
            True,
            True,
            False,
            False,  # Test SD Save
        ),
        # 1 - Multisig - Show all text and QR codes
        (
            Wallet(tdata.MULTISIG_12_WORD_KEY),
            None,
            [
                BUTTON_ENTER,  # Enter XPUB - Text
                BUTTON_PAGE,  # move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE,  # move to XPUB - QR Code
                BUTTON_ENTER,  # Enter XPUB - QR Code
                BUTTON_ENTER,  # Enter QR Menu
                BUTTON_PAGE_PREV,  # move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE,  # move to XPUB - QR Code
                BUTTON_PAGE,  # move to ZPUB - Text
                BUTTON_PAGE,  # move to ZPUB - QR Code
                BUTTON_ENTER,  # Enter ZPUB - QR Code
                BUTTON_ENTER,  # Enter QR Menu
                BUTTON_PAGE_PREV,  # move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
            True,
            True,
            False,
            False,  # Test SD Save
        ),
        # 2 - Singlesig Nested Segwit - Show all text and QR codes
        (
            Wallet(tdata.NESTEDSW1_KEY),
            None,
            [
                BUTTON_ENTER,  # Enter XPUB - Text
                BUTTON_PAGE,  # move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE,  # move to XPUB - QR Code
                BUTTON_ENTER,  # Enter XPUB - QR Code
                BUTTON_ENTER,  # exit the qrcode and enter in QR Menu
                BUTTON_PAGE_PREV,  # move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                *([BUTTON_PAGE] * 2),  # move to YPUB - text
                BUTTON_ENTER,  # Enter YPUB - text
                BUTTON_PAGE,  # move to Back
                BUTTON_ENTER,  # press Back
                *([BUTTON_PAGE] * 3),  # move to YPUB - QR Code
                BUTTON_ENTER,  # Enter YPUB - QR code
                BUTTON_ENTER,  # exit the qrcode and enter in QR Menu
                BUTTON_PAGE_PREV,  # move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
            False,
            False,
            True,
            False,  # Test SD Save
        ),
        # 3 - Multisig P2SH_P2WSH - UNREACHABLE CODE PATH
        (
            Wallet(tdata.MULTISIG_12_WORD_KEY),  # P2SH_P2WSH not implemented yet
            None,
            [
                BUTTON_ENTER,  # Enter XPUB - Text
                BUTTON_PAGE,  # move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE,  # move to XPUB - QR Code
                BUTTON_ENTER,  # Enter XPUB - QR Code
                BUTTON_ENTER,  # exit the qrcode and enter in QR Menu
                BUTTON_PAGE_PREV,  # move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE,  # move to XPUB - QR Code
                BUTTON_PAGE,  # move to ZPUB - Text
                BUTTON_PAGE,  # move to ZPUB - QR Code
                BUTTON_ENTER,  # Enter ZPUB - QR Code
                BUTTON_ENTER,  # Enter QR Menu
                BUTTON_PAGE_PREV,  # move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
            True,  # Show XPUB
            True,  # Show ZPUB
            False,  # Show YPUB
            False,  # Test SD Save
        ),
        # 4 - Singlesig - Save XPUB and ZPUB to SD card
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            None,
            [
                BUTTON_ENTER,  # Enter XPUB - Text
                BUTTON_ENTER,  # Enter Save to SD (first save operation)
                BUTTON_PAGE,  # move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE,  # move to XPUB - QR Code
                BUTTON_ENTER,  # Enter XPUB - QR Code
                BUTTON_ENTER,  # Enter QR Menu
                BUTTON_PAGE_PREV,  # move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE,  # move to XPUB - QR Code
                BUTTON_PAGE,  # move to ZPUB - Text
                BUTTON_ENTER,  # Enter ZPUB - Text
                BUTTON_ENTER,  # Enter Save to SD (second save operation)
                BUTTON_PAGE,  # move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE,  # move to ZPUB - QR Code
                BUTTON_ENTER,  # Enter ZPUB - QR Code
                BUTTON_ENTER,  # Enter QR Menu
                BUTTON_PAGE_PREV,  # move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
            True,
            True,
            False,
            True,  # Test SD Save
        ),
        # 5 - Multisig - Save XPUB and ZPUB to SD card
        (
            Wallet(tdata.MULTISIG_12_WORD_KEY),
            None,
            [
                BUTTON_ENTER,  # Enter XPUB - Text
                BUTTON_ENTER,  # Enter Save to SD
                BUTTON_PAGE,  # move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE,  # move to XPUB - QR Code
                BUTTON_ENTER,  # Enter XPUB - QR Code
                BUTTON_ENTER,  # Enter QR Menu
                BUTTON_PAGE_PREV,  # move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE,  # move to XPUB - QR Code
                BUTTON_PAGE,  # move to ZPUB - Text
                BUTTON_ENTER,  # Enter ZPUB - Text
                BUTTON_ENTER,  # Enter Save to SD
                BUTTON_PAGE,  # move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE,  # move to ZPUB - QR Code
                BUTTON_ENTER,  # Enter ZPUB - QR Code
                BUTTON_ENTER,  # Enter QR Menu
                BUTTON_PAGE_PREV,  # move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
            True,
            True,
            False,
            True,  # Test SD Save
        ),
        # 6 - Nested Segwit - Save XPUB and YPUB to SD card
        (
            Wallet(tdata.NESTEDSW1_KEY),
            None,
            [
                BUTTON_ENTER,  # Enter XPUB - Text
                BUTTON_ENTER,  # Enter Save to SD
                BUTTON_PAGE,  # move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE,  # move to XPUB - QR Code
                BUTTON_ENTER,  # Enter XPUB - QR Code
                BUTTON_ENTER,  # Enter QR Menu
                BUTTON_PAGE_PREV,  # move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                *([BUTTON_PAGE] * 2),  # move to YPUB - Text
                BUTTON_ENTER,  # Enter YPUB - Text
                BUTTON_ENTER,  # Enter Save to SD
                BUTTON_PAGE,  # move to Back
                BUTTON_ENTER,  # Press Back
                *([BUTTON_PAGE] * 3),  # move to YPUB - QR Code
                BUTTON_ENTER,  # Enter YPUB - QR Code
                BUTTON_ENTER,  # Enter QR Menu
                BUTTON_PAGE_PREV,  # move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
            True,
            False,
            True,
            True,  # Test SD Save
        ),
    ]

    for case in cases:
        ctx = create_ctx(mocker, case[2], case[0], case[1])
        pub_key_viewer = PubkeyView(ctx)

        pub_key_viewer.public_key()

        # Build expected QR view calls
        qr_view_calls = []
        print_qr_calls = []
        sd_card_save_calls = []

        if case[3]:  # Show XPUB
            xpub = ctx.wallet.key.key_expression(None)
            qr_view_calls.append(
                mocker.call(
                    ctx,
                    data=xpub,
                    title="XPUB",
                ),
            )
            if case[1]:  # If printer is available
                print_qr_calls.append(
                    mocker.call(
                        xpub,
                        FORMAT_NONE,
                        "XPUB",
                    ),
                )

            if case[6]:  # Test SD Save
                sd_card_save_calls.append(
                    mocker.call(
                        xpub,
                        "XPUB",
                        "XPUB",
                        "XPUB:",
                        ".pub",
                        save_as_binary=False,
                    )
                )

        if case[4]:  # Show ZPUB
            version = "Zpub" if ctx.wallet.key.policy_type == TYPE_MULTISIG else "zpub"
            zpub = ctx.wallet.key.key_expression(ctx.wallet.key.network[version])
            qr_view_calls.append(
                mocker.call(
                    ctx,
                    data=zpub,
                    title="ZPUB",
                ),
            )
            if case[1]:  # If printer is available
                print_qr_calls.append(
                    mocker.call(
                        zpub,
                        FORMAT_NONE,
                        "ZPUB",
                    ),
                )

            if case[6]:  # Test SD Save
                sd_card_save_calls.append(
                    mocker.call(
                        zpub,
                        "ZPUB",
                        "ZPUB",
                        "ZPUB:",
                        ".pub",
                        save_as_binary=False,
                    )
                )

        if case[5]:  # Show YPUB
            version = "Ypub" if ctx.wallet.key.policy_type == TYPE_MULTISIG else "ypub"
            ypub = ctx.wallet.key.key_expression(ctx.wallet.key.network[version])
            qr_view_calls.append(
                mocker.call(
                    ctx,
                    data=ypub,
                    title="YPUB",
                ),
            )
            if case[1]:  # If printer is available
                print_qr_calls.append(
                    mocker.call(
                        ypub,
                        FORMAT_NONE,
                        "YPUB",
                    ),
                )

            if case[6]:  # Test SD Save
                sd_card_save_calls.append(
                    mocker.call(
                        ypub,
                        "YPUB",
                        "YPUB",
                        "YPUB:",
                        ".pub",
                        save_as_binary=False,
                    )
                )

        if qr_view_calls:
            assert mock_seed_qr_view.called

        if case[1] and print_qr_calls:
            ctx.printer.print_qr.assert_has_calls(print_qr_calls, any_order=True)

        if case[6]:
            mock_save_file.assert_has_calls(sd_card_save_calls, any_order=False)

        assert ctx.input.wait_for_button.call_count == len(case[2])
