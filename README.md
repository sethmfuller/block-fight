# Block Fight

## High-Level Requirements

- Two Players
- Socket network connection for multiplayer capability
- Each play is composed of sprite blocks
- Actions: Punch, shoot, kick
- Once player has only 1 block left, the other player wins.
- Players can shoot, punch, and kick blocks off the other player.
- Can walk and jump
- Blocks are sent a certain distance when knocked from a player
- Could have platforms with automated turrets


##

- Character is a tree of blocks

    - Abstract Block class
        - Defensive blocks
        - Offensive blocks
            - Weapons
            - Punches
