#include <stdio.h>
#include "defs.h"
#include "data.h"
#include "protos.h"
#include "corr.h"

/*
 *
 * --- Evaluation for current position --- *
 *
 */

/* The evaluation function */
int Eval (alpha, beta)
{
    /* How many evaluations in total */
    count_evaluations++;

    /* The score of the position */
    int score = 0;

    // Scan all squares looking for pieces, and modify score accordingly.
    int i;
    for (i = 0; i < 64; ++i)
    {
        if ( piece[i] < 6 ) // if there is some piece in this square
        {
            /* level-0 correlation: each piece has a value */
            //score += corr0[piece[i]];
            score += corr0[2];
            
            /* level-1 correlation: each square/piece/color combination has a value */
            //score += corr1[i][piece[i]][color[i]];
        }
    };

    /* Finally we return the score, taking into account the side to move */

    if (side == WHITE)
    {
        return score;
    }
    else
    {
        return -score;
    }
};
