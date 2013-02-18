#include <stdio.h>
#include "defs.h"
#include "data.h"
#include "protos.h"

/*
 ****************************************************************************
 * Evaluation for current position - main "brain" function *
 ****************************************************************************
 */

/* Bonus and malus */
/*#define	ROOK_OPEN_COL               25
#define PAIR_BISHOPS                25
#define ADV_TURN_TO_MOVE            10
#define DOUBLED_PAWN_MALUS          15
#define DOUBLED_PAWN_CASTLE_MALUS   25
#define MISSING_PAWN_CASTLE_MALUS   20
#define HOLE_C3_C6_F3_F6            30
#define HOLE_B3_B6_G3_G6            30
#define TRAPPED_ROOK_PENALTY        70*/

/* Arrays for scaling mobility values */
int mob_rook[16] = {
    -6, -3, 0, 2, 4, 6, 8, 10, 12, 14, 15, 16, 17, 18, 19, 20
};
int mob_knight[9] = {
    -10, -4, 2, 8, 14, 18, 22, 24, 25
};
int mob_bishop[16] = {
    -5, -2, 0, 3, 6, 10, 14, 20, 24, 28, 31, 35, 40, 42, 45, 47
};
int range_bishop[16] = {
    -6, -3, 0, 2, 4, 6, 8, 10, 12, 14, 15, 16, 17, 18, 19, 20
};

/* For scaling passed pawns depending on the row */
int passed_pawn_white[7] = {0, 10, 12, 15, 35, 55, 70};
int passed_pawn_black[7] = {70, 55, 35, 15, 12, 10, 0};

/* Kings' safety */
int posWhiteKing = 0;
int colWhiteKing = 0;
int posBlackKing = 0;
int colBlackKing = 0;

/* To count the material */
int whitePawns = 0;
int whiteKnights = 0;
int whiteBishops = 0;
int whiteRooks = 0;
int whiteQueens = 0;
int blackPawns = 0;
int blackKnights = 0;
int blackBishops = 0;
int blackRooks = 0;
int blackQueens = 0;


/* Pawn's info */
int whitePawnsInfo[8] = {0, 0, 0, 0, 0, 0, 0, 0};
int blackPawnsInfo[8] = {0, 0, 0, 0, 0, 0, 0, 0};


/* The evaluation function */
int Eval (alpha, beta)
{
    /* A traditional counter */
    int i;

    /* Set some values to 0 */
    /* Pawn's info */
    for (i=0; i<8; ++i)
    {
        whitePawnsInfo[i] = 0;
        blackPawnsInfo[i] = 0;
    }

    /* The vars for counting the material */
    whitePawns = 0;
    whiteKnights = 0;
    whiteBishops = 0;
    whiteRooks = 0;
    whiteQueens = 0;
    blackPawns = 0;
    blackKnights = 0;
    blackBishops = 0;
    blackRooks = 0;
    blackQueens = 0;

    count_evaluations++;

    /* The score of the position */
    int score = 0;

    for (i = 0; i < 64; ++i)
    {
        /* Just counting the wood on the board */
        if (color[i] == WHITE)
        {
            switch(piece[i])
            {
            case PAWN:
                whitePawns++;
                whitePawnsInfo[(int)Col(i)] += 1<<Row(i);
                break;
            case KNIGHT:
                whiteKnights++;
                break;
            case BISHOP:
                whiteBishops++;
                break;
            case ROOK:
                whiteRooks++;
                break;
            case QUEEN:
                whiteQueens++;
                break;
            case KING:
                posWhiteKing = i;
                colWhiteKing = Col(i);
                break;
            }
        }
        else if (color[i] == BLACK)
        {
            switch(piece[i])
            {
            case PAWN:
                blackPawns++;
                blackPawnsInfo[(int)Col(i)] += 1<<Row(i);
                break;
            case KNIGHT:
                blackKnights++;
                break;
            case BISHOP:
                blackBishops++;
                break;
            case ROOK:
                blackRooks++;
                break;
            case QUEEN:
                blackQueens++;
                break;
            case KING:
                posBlackKing = i;
                colBlackKing = Col(i);
                break;
            }
        }
    }

    /* After counting the material we update the score */
    score = whitePawns * value_piece[PAWN] +
            whiteKnights * value_piece[KNIGHT] +
            whiteBishops * value_piece[BISHOP] +
            whiteRooks * value_piece[ROOK] +
            whiteQueens * value_piece[QUEEN] -
            blackPawns * value_piece[PAWN] -
            blackKnights * value_piece[KNIGHT] -
            blackBishops * value_piece[BISHOP] -
            blackRooks * value_piece[ROOK] -
            blackQueens * value_piece[QUEEN];

    /* Trying the lazy eval */
    int lazy = score;
    if (side == BLACK) lazy = -lazy;
    if ( ( lazy + 500 < alpha ) ||
         ( lazy - 500 > beta  ) )
    {
        return lazy;
    }

    /* Check all the squares searching for the pieces */
    for (i = 0; i < 64; i++)
    {
        if (color[i] == EMPTY)
            continue;
        if (color[i] == WHITE)
        {
            /* Now we add to the evaluation the value of the
             * piece square tables */
            switch (piece[i])
            {
            case PAWN:
                //score += pst_pawn_endgame[i];
                score += pst_pawn_midgame[i];
                break;
            case KNIGHT:
                score += pst_knight[i];
                break;
            case BISHOP:
                score += pst_bishop[i];
                break;
            case ROOK:
                score += pst_rook[i];
                break;
            case QUEEN:
                score += pst_queen[i];
                break;
            case KING:
                //score += pst_king_endgame[i];
                score += pst_king_midgame[i];
                break;
            }
        }

        /* Now the evaluation for black: note the change of
           the sign in the score */
        else
        {
            switch (piece[i])
            {
            case PAWN:
                //score -= pst_pawn_endgame[flip[i]];
                score -= pst_pawn_midgame[flip[i]];
                break;
            case KNIGHT:
                score -= pst_knight[flip[i]];
                break;
            case BISHOP:
                score -= pst_bishop[flip[i]];
                break;
            case ROOK:
                score -= pst_rook[flip[i]];
                break;
            case QUEEN:
                score -= pst_queen[flip[i]];
                break;
            case KING:
                //score -= pst_king_endgame[flip[i]];
                score -= pst_king_midgame[flip[i]];
                break;
            }
        }
    }

    /* Finally we return the score, taking into account the side to move
        We add an extra plus because in the same position the side to
        move has some extra advantage*/

    if (side == WHITE)
        return (score );
    return -score;
}

/* Returns 1 if no enough material on the board */
int NoMaterial()
{
    if (whitePawns == 0 && blackPawns == 0)
        if (whiteRooks == 0 && blackRooks == 0)
            if (whiteQueens == 0 && blackQueens == 0)
                if (whiteBishops <= 1 && blackBishops <= 1)
                    if (whiteKnights <= 1 && blackKnights <= 1)
                        if (whiteKnights == 0 || whiteBishops == 0)
                            if (blackKnights == 0 || blackBishops == 0)
                                return 1;
    return 0;
}
