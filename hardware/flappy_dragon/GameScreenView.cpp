#include <gui/gamescreen_screen/GameScreenView.hpp>
#include "stm32h7xx.h"

const int topCorrection = 5;
const int spriteMoveLength = 8;
const int evilSpeed = 2;
const int screenMidpoint = SCREEN_HEIGHT / 2;
const int numEvilMoves = 11;
const int centerBeamPositions[numEvilMoves] = {20, -40, 40, -30, 20, -20, 60, -80, 80, -80, 40};
const int BASE_CLOCK = 480000000;
const int blinkFor = 60;

int tickCount;
int relativeMovesLeft;
int evilMoveIndex;
int timesBurned;
int startingCooldown;
bool enemiesApproaching;
bool challengeFinished;
bool enemiesClear;


GameScreenView::GameScreenView()
{

}

void GameScreenView::setupScreen()
{
    GameScreenViewBase::setupScreen();
    enemiesApproaching = true;
    challengeFinished = false;
    enemiesClear = false;
    relativeMovesLeft = 0;
    evilMoveIndex = 0;
    tickCount = 0;
    buttonUpHeld = false;
    buttonDownHeld = false;
    timesBurned = 0;
    blinkCounter = 0;
    startingCooldown = 40;
}

void GameScreenView::tearDownScreen()
{
    GameScreenViewBase::tearDownScreen();
}

void GameScreenView::buttonUpClicked()
{
    int x = sprite.getX();
    if (x < 220 && !challengeFinished) sprite.moveTo(x + spriteMoveLength, sprite.getY());
}

void GameScreenView::buttonDownClicked()
{
    int x = sprite.getX();
    if (x > 20 && !challengeFinished) sprite.moveTo(x - spriteMoveLength, sprite.getY());
}

void GameScreenView::moveBackground() {
    int16_t y = background.getY() - 1;
    if (y <= -BACKGROUND_LENGTH) y = 0;
    background.moveTo(0, y);
}

void GameScreenView::moveFireballs() {
    int16_t y = fireballsTop.getY() + 1;
    if (y >= FIREBALL_Y + FIREBALL_PERIOD) y = FIREBALL_Y;
    fireballsTop.moveTo(fireballsTop.getX(), y);
    fireballsBot.moveTo(fireballsBot.getX(), y);
}

void GameScreenView::moveEnemiesAndFireballs(int topRelX, int botRelX) {
    fireballsTop.moveRelative(topRelX*evilSpeed, 0);
    evilTop.moveRelative(topRelX*evilSpeed, 0);
    fireballsBot.moveRelative(botRelX*evilSpeed, 0);
    evilBot.moveRelative(botRelX*evilSpeed, 0);
}

void GameScreenView::moveEnemies() {
    if (relativeMovesLeft == 0) {
        if (evilMoveIndex < numEvilMoves) {
            relativeMovesLeft = centerBeamPositions[evilMoveIndex];
            evilMoveIndex++;
        } else {
            challengeFinished = true;
        }
    } else if (relativeMovesLeft < 0) {
        moveEnemiesAndFireballs(-1, -1);
        relativeMovesLeft++;
    } else if (relativeMovesLeft > 0) {
        moveEnemiesAndFireballs(+1, +1);
        relativeMovesLeft--;
    }
}

void GameScreenView::moveEnemiesAway() {
    if (enemiesClear) {
        win();
    } else {
        moveEnemiesAndFireballs(+1, -1);
        if (evilTop.getX() > SCREEN_HEIGHT + 10 && evilBot.getX() < -SPRITE_HEIGHT - 10) enemiesClear = true;
    }
}

void GameScreenView::approachEnemies() {
    int16_t xTop = fireballsTop.getX();
    int16_t xBot = fireballsBot.getX();
    bool approached = true;
    if (xTop > FIREBALL_TOP_INIT_X) {
        approached = false;
        moveEnemiesAndFireballs(-1, 0);
    }
    if (xBot < FIREBALL_BOT_INIT_X) {
        approached = false;
        moveEnemiesAndFireballs(0, +1);
    }
    if (approached) enemiesApproaching = false;
}

void GameScreenView::lose() {
    application().gotoGameScreenLoseScreenNoTransition();
}

void GameScreenView::win() {
    application().gotoGameScreenWinScreenNoTransition();
}

void GameScreenView::checkCollisions() {
    if (blinkCounter > 0) return;
    int xBot = fireballsBot.getX() + FIREBALL_HEIGHT / 2;
    int xTop = fireballsTop.getX() - FIREBALL_HEIGHT / 2;
    int xSpriteBot = sprite.getX();
    int xSpriteTop = xSpriteBot + SPRITE_HEIGHT;
    if (xSpriteBot <= xBot || xSpriteTop - topCorrection >= xTop) {
        blinkCounter = blinkFor;
    }
}

void GameScreenView::handleClickEvent(const touchgfx::ClickEvent& event) {
    if (event.getType() == touchgfx::ClickEvent::PRESSED) {
        if (buttonUp.getAbsoluteRect().intersect(event.getX(), event.getY())) {
            buttonUpHeld = true;
        }
        if (buttonDown.getAbsoluteRect().intersect(event.getX(), event.getY())) {
            buttonDownHeld = true;
        }
    } else {
        buttonUpHeld = false;
        buttonDownHeld = false;
    }
    GameScreenViewBase::handleClickEvent(event);
}

void GameScreenView::handleTickEvent() {
    uint32_t ratio = BASE_CLOCK / SystemCoreClock;
    tickCount++;
    if (blinkCounter > 0) {
        sprite.setVisible(blinkCounter % 8 < 4);
        sprite.invalidate();
        blinkCounter--;
        if (blinkCounter == 0) {
            lose();
        }
        return;
    }
    if (startingCooldown > 0) {
        startingCooldown--;
    }
    if (buttonUpHeld) buttonUpClicked();
    if (buttonDownHeld) buttonDownClicked();
    if (tickCount >= ratio) {
        tickCount = 0;
        moveBackground();
        moveFireballs();
        if (startingCooldown <= 0) {
            if (enemiesApproaching) {
                approachEnemies();
            } else {
                moveEnemies();
            }
        }
        if (challengeFinished) {
            moveEnemiesAway();
        } else {
            checkCollisions();
        }        
    }
}
