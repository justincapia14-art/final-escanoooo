#intermediate_level_blocks.py
import pygame

MAZE_MAP = [
    "B                                       ",
    " B                                      ",
    "  B                                     ",
    "   B                        B           ",
    "    B                       B           ",
    "  BBBBBBBBBBBBBBBBBBBBBBBBBBB   BBBBBBBB",
    "                                      BB",
    "        BBBBBBBBBBB                     ",
    "           BBBB   BBBBB   B    BBB      ",
    "           BBBB           BB            ",
    "           BBBB           BB            ",
    "BBBBBBBBBBBBBBB           BBBBBBB  BBBBB",
    "                                        ",
    "                   BBBBBBBBBBB  BBBBB   ",
    "   B  BBBBBBB                     BBB   ",
    "B                  B    B               ",
    "        B                              B",
    "    BB  BBBBBBBBBBBB         BBBB  BBBBB",
    " B  BB                 BBB              ",
    "    BB                            B     ",
    "                                        ",
    "BBBBBB        BBBB         BBBBBBB  BBBB",
    "                       BBB              ",
    "                                        ",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"
]

def intermediate_get_platforms():
    platforms = []
    
    for row_index, row in enumerate(MAZE_MAP):
        for col_index, tile in enumerate(row):
            if tile == 'B' or tile == 'G':
                x = col_index * 20
                y = row_index * 20
                platforms.append(pygame.Rect(x, y, 20, 20))
                
    return platforms


def intermediate_draw_platforms(screen, ground1, ground2, brick1, brick2):
    for row_index, row in enumerate(MAZE_MAP):
        for col_index, tile in enumerate(row):
            x = col_index * 20
            y = row_index * 20
            
            if tile == 'B':
                screen.blit(brick1, (x, y))
            elif tile == 'G':
                screen.blit(ground2, (x, y))
                # if col_index % 2 == 0:
                #     screen.blit(ground2, (x, y))
                # else:
                #     screen.blit(ground2, (x, y))