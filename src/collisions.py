"""Direction-aware collisions and the original three paddle hit zones."""

from .config import HEIGHT, WIDTH


def bounce_walls(ball):
    """Bounce on top/bottom and clamp penetration to prevent repeated flips."""
    if ball.position.y <= ball.radius and ball.velocity.y < 0:
        ball.position.y = ball.radius
        ball.velocity.y = abs(ball.velocity.y)
        return True
    if ball.position.y >= HEIGHT - ball.radius and ball.velocity.y > 0:
        ball.position.y = HEIGHT - ball.radius
        ball.velocity.y = -abs(ball.velocity.y)
        return True
    return False


def bounce_paddle(ball, paddle, zoned=True):
    """Return a hit zone or None; each approach can produce only one bounce."""
    if not ball.rect.colliderect(paddle.rect):
        return None
    velocity = ball.velocity
    player = paddle.player
    approaching = (velocity.x < 0, velocity.x > 0, velocity.y < 0, velocity.y > 0)
    if not approaching[player]:
        return None
    if player == 0:
        ball.position.x = paddle.rect.right + ball.radius
        velocity.x = abs(velocity.x)
    elif player == 1:
        ball.position.x = paddle.rect.left - ball.radius
        velocity.x = -abs(velocity.x)
    elif player == 2:
        ball.position.y = paddle.rect.bottom + ball.radius
        velocity.y = abs(velocity.y)
    else:
        ball.position.y = paddle.rect.top - ball.radius
        velocity.y = -abs(velocity.y)

    if not zoned:
        return "plain"
    relative = (ball.position.y - paddle.rect.top) / paddle.rect.height
    if relative < 0.35:
        zone = "upper"
    elif relative < 0.65:
        zone = "center"
    else:
        zone = "lower"

    # Apply the same bounded speed magnitudes on both sides. The legacy
    # signed comparisons accidentally made the right paddle behave differently.
    sign = 1 if player == 0 else -1
    speed = abs(velocity.x)
    if zone == "center":
        velocity.x = sign * max(200, speed - 100) if speed > 200 else sign * speed
    else:
        velocity.x = sign * min(500, speed + 100) if speed < 500 else sign * speed
        if abs(velocity.y) < 1000:
            velocity.y = max(-1000, min(1000, velocity.y + (200 if zone == "upper" else -200)))
    return zone


def exit_side(ball):
    """Match the original scoring trigger: the ball centre leaves the field."""
    if ball.position.x <= 0:
        return "left"
    if ball.position.x >= WIDTH:
        return "right"
    if ball.position.y <= 0:
        return "top"
    if ball.position.y >= HEIGHT:
        return "bottom"
    return None
