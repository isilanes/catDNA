#include "defs.h"
#include "data.h"
#include <time.h>

/* Contador para la regla de los 50 movimientos */
int fifty;

int side;         /* side to move, value = BLACK or WHITE */
int computer_side;
int max_depth;    /* max depth to search */
HISTO hist[6000]; /* game length < 6000 */

char fenstring[256];

/* For castle rights we use a bitfield, like in TSCP
 *
 * 0001 -> White can short castle
 * 0010 -> White can long castle
 * 0100 -> Black can short castle
 * 1000 -> Black can long castle
 *
 * 15 = 1111 = 1*2^3 + 1*2^2 + 1*2^1 + 1*2^0
 *
 */
int castle = 15; /* At start position all castle types ar available */


/* The next mask is applied like this
 *
 * castle &= castle_mask[from] & castle_mask[dest]
 *
 * When from and dest are whatever pieces, then nothing happens, otherwise
 * the values are chosen in such a way that if for example the white king moves
 * to f1 then
 *
 * castle = castle & (12 & 15)
 * 1111 & (1100 & 1111) == 1111 & 1100 == 1100
 *
 * and white's lost all its castle rights
 *
 * */
int castle_mask[64] = {
    7, 15, 15, 15, 3, 15, 15, 11,
    15, 15, 15, 15, 15, 15, 15, 15,
    15, 15, 15, 15, 15, 15, 15, 15,
    15, 15, 15, 15, 15, 15, 15, 15,
    15, 15, 15, 15, 15, 15, 15, 15,
    15, 15, 15, 15, 15, 15, 15, 15,
    15, 15, 15, 15, 15, 15, 15, 15,
    13, 15, 15, 15, 12, 15, 15, 14
};

int hdp; /* current move order */
//int allmoves = 0;

/* For searching */
U64 nodes;			/* Count all visited nodes when searching */
int ply;			/* ply of search */
U64 count_evaluations;
int count_checks;
U64 count_MakeMove;
U64 countquiesCalls;
U64 countCapCalls;
U64 countSearchCalls;

/* The values of the pieces in centipawns */
int value_piece[6] =
{   VALUE_PAWN, VALUE_KNIGHT, VALUE_BISHOP, VALUE_ROOK, VALUE_QUEEN,
    VALUE_KING
};


/* Board representation */
int color[64];
int piece[64];
clock_t max_time = 9999999;
clock_t stop_time;
clock_t half_time;
clock_t total_time;
int must_stop;

/* Piece in each square */
int init_piece[64] = {
    ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK,
    PAWN, PAWN, PAWN, PAWN, PAWN, PAWN, PAWN, PAWN,
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
    PAWN, PAWN, PAWN, PAWN, PAWN, PAWN, PAWN, PAWN,
    ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK
};

/* Color of each square */
int init_color[64] = {
    BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK,
    BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK,
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
    WHITE, WHITE, WHITE, WHITE, WHITE, WHITE, WHITE, WHITE,
    WHITE, WHITE, WHITE, WHITE, WHITE, WHITE, WHITE, WHITE
};

/* Correlation tables or order N (corrN) */

int corr1[64][6][2] = {
    {
        {0,0},
        {0,1},
        {0,0},
        {385,0},
        {7,0},
        {0,0}
    },
    {
        {0,0},
        {0,0},
        {99,0},
        {42,0},
        {0,0},
        {98,0}
    },
    {
        {0,0},
        {203,0},
        {0,0},
        {109,0},
        {2,1},
        {79,0}
    },
    {
        {0,0},
        {2,0},
        {0,0},
        {155,3},
        {231,0},
        {0,0}
    },
    {
        {0,0},
        {3,0},
        {0,0},
        {159,1},
        {28,2},
        {206,0}
    },
    {
        {0,0},
        {207,0},
        {0,0},
        {146,1},
        {0,0},
        {0,0}
    },
    {
        {0,0},
        {0,0},
        {57,0},
        {41,0},
        {0,4},
        {430,0}
    },
    {
        {0,0},
        {0,0},
        {0,0},
        {284,0},
        {0,0},
        {75,0}
    },
    {
        {587,2},
        {0,1},
        {0,0},
        {6,0},
        {0,2},
        {0,5}
    },
    {
        {543,0},
        {4,0},
        {0,0},
        {1,16},
        {6,7},
        {6,6}
    },
    {
        {471,1},
        {3,9},
        {0,0},
        {16,0},
        {17,1},
        {0,0}
    },
    {
        {41,0},
        {45,0},
        {32,1},
        {1,2},
        {71,3},
        {3,0}
    },
    {
        {145,0},
        {36,10},
        {21,1},
        {9,3},
        {38,1},
        {23,0}
    },
    {
        {522,0},
        {3,0},
        {8,0},
        {0,10},
        {9,2},
        {27,0}
    },
    {
        {440,2},
        {106,0},
        {0,0},
        {0,7},
        {22,2},
        {19,2}
    },
    {
        {565,0},
        {0,2},
        {0,0},
        {2,1},
        {0,3},
        {0,1}
    },
    {
        {60,2},
        {14,0},
        {0,0},
        {1,0},
        {5,0},
        {0,5}
    },
    {
        {200,1},
        {12,11},
        {7,2},
        {0,0},
        {10,3},
        {0,3}
    },
    {
        {118,7},
        {1,2},
        {183,2},
        {3,0},
        {28,5},
        {1,0}
    },
    {
        {25,2},
        {10,1},
        {5,0},
        {0,0},
        {31,4},
        {23,0}
    },
    {
        {49,8},
        {148,0},
        {29,2},
        {24,0},
        {5,2},
        {34,4}
    },
    {
        {219,8},
        {9,0},
        {222,0},
        {13,0},
        {3,0},
        {14,1}
    },
    {
        {278,1},
        {4,1},
        {16,0},
        {5,2},
        {19,1},
        {22,0}
    },
    {
        {103,0},
        {24,0},
        {0,0},
        {0,0},
        {0,1},
        {6,1}
    },
    {
        {105,24},
        {4,14},
        {12,4},
        {0,5},
        {2,2},
        {0,2}
    },
    {
        {76,70},
        {0,14},
        {0,3},
        {6,6},
        {17,7},
        {0,9}
    },
    {
        {72,82},
        {47,1},
        {2,8},
        {7,0},
        {25,6},
        {7,4}
    },
    {
        {214,57},
        {19,0},
        {137,5},
        {10,3},
        {16,15},
        {7,0}
    },
    {
        {384,16},
        {23,15},
        {23,5},
        {0,3},
        {14,3},
        {54,2}
    },
    {
        {52,25},
        {26,6},
        {0,1},
        {37,0},
        {12,10},
        {5,3}
    },
    {
        {131,53},
        {6,22},
        {4,0},
        {5,1},
        {4,3},
        {0,2}
    },
    {
        {101,27},
        {20,0},
        {3,0},
        {3,0},
        {6,2},
        {1,1}
    },
    {
        {52,179},
        {3,2},
        {0,71},
        {4,0},
        {1,25},
        {0,2}
    },
    {
        {46,151},
        {38,8},
        {11,0},
        {1,1},
        {0,4},
        {0,1}
    },
    {
        {59,93},
        {0,12},
        {2,8},
        {5,0},
        {23,6},
        {1,4}
    },
    {
        {93,176},
        {21,7},
        {57,21},
        {7,3},
        {10,1},
        {18,6}
    },
    {
        {108,179},
        {24,14},
        {23,21},
        {3,6},
        {8,20},
        {21,8}
    },
    {
        {52,150},
        {12,13},
        {60,7},
        {0,0},
        {11,1},
        {0,10}
    },
    {
        {40,87},
        {58,1},
        {6,2},
        {7,2},
        {13,1},
        {2,12}
    },
    {
        {26,103},
        {5,3},
        {1,1},
        {9,6},
        {7,10},
        {4,5}
    },
    {
        {7,331},
        {4,3},
        {1,3},
        {15,21},
        {5,4},
        {0,5}
    },
    {
        {70,93},
        {0,4},
        {0,40},
        {12,0},
        {4,13},
        {0,7}
    },
    {
        {10,133},
        {1,37},
        {12,86},
        {8,0},
        {14,3},
        {9,11}
    },
    {
        {41,292},
        {14,27},
        {29,2},
        {14,3},
        {5,2},
        {0,7}
    },
    {
        {14,234},
        {11,31},
        {18,1},
        {9,5},
        {7,1},
        {1,17}
    },
    {
        {20,95},
        {1,20},
        {4,234},
        {2,6},
        {9,9},
        {12,17}
    },
    {
        {12,207},
        {8,7},
        {0,3},
        {1,1},
        {5,15},
        {8,20}
    },
    {
        {40,286},
        {1,4},
        {0,0},
        {7,0},
        {7,4},
        {0,19}
    },
    {
        {14,372},
        {0,0},
        {0,0},
        {62,2},
        {0,17},
        {0,2}
    },
    {
        {6,344},
        {1,96},
        {0,0},
        {16,21},
        {4,12},
        {0,0}
    },
    {
        {26,172},
        {3,0},
        {6,0},
        {63,5},
        {2,119},
        {0,1}
    },
    {
        {14,71},
        {16,44},
        {3,101},
        {27,8},
        {4,15},
        {0,10}
    },
    {
        {5,95},
        {1,98},
        {6,32},
        {36,4},
        {9,14},
        {0,30}
    },
    {
        {5,538},
        {0,0},
        {0,0},
        {8,27},
        {12,2},
        {0,26}
    },
    {
        {1,446},
        {0,93},
        {13,0},
        {12,11},
        {1,2},
        {0,23}
    },
    {
        {0,456},
        {0,1},
        {0,0},
        {23,1},
        {4,1},
        {0,26}
    },
    {
        {0,0},
        {0,14},
        {0,0},
        {10,495},
        {4,2},
        {0,0}
    },
    {
        {0,0},
        {0,0},
        {0,165},
        {11,50},
        {4,8},
        {0,10}
    },
    {
        {0,0},
        {0,266},
        {0,0},
        {11,62},
        {6,4},
        {0,12}
    },
    {
        {0,0},
        {0,11},
        {8,0},
        {0,146},
        {3,284},
        {0,17}
    },
    {
        {0,0},
        {0,0},
        {0,21},
        {7,158},
        {2,13},
        {0,375}
    },
    {
        {0,0},
        {0,323},
        {1,14},
        {0,196},
        {9,1},
        {0,31}
    },
    {
        {0,0},
        {3,0},
        {0,81},
        {2,25},
        {4,0},
        {0,388}
    },
    {
        {0,0},
        {0,3},
        {0,0},
        {13,382},
        {1,0},
        {0,63}
    },
};
