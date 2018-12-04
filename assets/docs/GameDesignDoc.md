Sprites:
    Body block: Yellow ellipse, anchor for arms and legs
    Defensive block: Blue circle, elbows and knees
    Offensive block: Red square, fists and feet

Interactions:
    Only interaction is between offensive blocks and the defensive and body blocks.
        * When an offensive block hits either of the other types with sufficient force, the other block gets a health value decreased
        * If a defensive block (knees, elbows) reaches 0 hp, then that limb gets removed.
        * When all limbs are destroyed or the body reaches 0, then the other player wins.

Birth and Death of sprites:
    All sprites are born during start of the game.
    Sprites die when they reach 0 hp, or their corresponding limb part gets destroyed.

State changes:
    When a player defeats the other, a game end screen declaring the winner is displayed, then the game resets