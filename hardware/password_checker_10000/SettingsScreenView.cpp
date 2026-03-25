#include <gui/settingsscreen_screen/SettingsScreenView.hpp>
#include <cstring>

static const int len = 42;
static const char secret[] = "dctf{REDACTED_REDACTED_REDACTED_REDACTED_}";
static const int iters = 10000;

SettingsScreenView::SettingsScreenView()
    : inputLen(0)
{
    memset(inputBuf, 0, sizeof(inputBuf));
}

void SettingsScreenView::setupScreen()
{
    SettingsScreenViewBase::setupScreen();
    started = false;
}

void SettingsScreenView::handleTickEvent()
{
    if (!started) {
        started = true;
        presenter->cdcSendDot(':');
        receivePassword();
        checkPassword();
    }
}

void SettingsScreenView::tearDownScreen()
{
    SettingsScreenViewBase::tearDownScreen();
}

void SettingsScreenView::receivePassword()
{
    inputLen = 0;
    memset(inputBuf, 0, sizeof(inputBuf));
    while (inputLen < len) {
        uint8_t c;
        if (presenter->cdcReceive(&c, 1) > 0) {
            inputBuf[inputLen++] = (char)c;
        }
    }
}

void SettingsScreenView::checkPassword()
{
    char password[len];

    for (int i = 0; i < inputLen && i < len; i++) {
        password[i] = inputBuf[i];
        volatile int b = -1;
        for (int r = 0; r < iters; r++) {
            b = memcmp(secret, password, len);
            if (b == 0) break;
        }
    }
    if (memcmp(inputBuf, secret, len) == 0) {
        application().gotoSettingsScreenWinScreenNoTransition();
    } else {
        while (presenter->cdcSendDot(':') != 0) {}
        receivePassword();
        checkPassword();
    }
}

