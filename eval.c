#include <stdio.h>
#include "defs.h"
#include "data.h"
#include "protos.h"

/*
 *
 * --- Evaluation for current position --- *
 *
 */

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

/* The evaluation function */
int Eval (alpha, beta)
{
    /* How many evaluations in total */
    count_evaluations++;

    /* The score of the position */
    int score = 0;

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

    int i;
    for (i = 0; i < 64; ++i)
    {
        /* Just counting the wood on the board */
        if (color[i] == WHITE)
        {
            switch(piece[i])
            {
            case PAWN:
                whitePawns++;
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
                break;
            }
        }
        else if (color[i] == BLACK)
        {
            switch(piece[i])
            {
            case PAWN:
                blackPawns++;
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

    /* level-1 correlation: each square/piece/color combination has a score */
    for (i = 0; i < 64; ++i)
    {
        score += corr1[i][piece[i]][color[i]];
    };

    /*
     * 1-level correlation: each piece/color/square(i)|piece/color/square(j) has a score, 
     * where for each i there is a single corresponding j.
     */

    /* Finally we return the score, taking into account the side to move */

    if (side == WHITE)
    {
        return score;
    }
    else
    {
        return -score;
    }
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
