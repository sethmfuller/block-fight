# Block Fight

## Due: Tuesday (11/4/2018)

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
        - Defensive blocks (hit box)
        - Offensive blocks
            - Weapons
            - Punches

- Criteria
    - Head (hit 10 times before loose)
    - Body (hit 25 time before loose)

- Basic actions
    - Walk
    - Move arms
    - Punch (move-arms/punnch)
    - Kick (walk/kick)
    - (later shoot)

## Libraries:

* [Pygame - Python engine](https://www.pygame.org/news)
* [Pymunk - Physics engine](http://www.pymunk.org/en/latest/)
