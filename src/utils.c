#include <stdio.h>

#include "defs.h"
#include "data.h"
#include "protos.h"

#include <sys/time.h>
#include <string.h>
struct timeval tv;
struct timezone tz;

//#define NDEBUG
//#include <assert.h>

/*
 ****************************************************************************
 * Utilities *
 ****************************************************************************
 */

void PrintBoard ()
{
    char pieceName[] = "PNBRQKpnbrqk";
    int i;
    for (i = 0; i < 64; i++)
    {
        if ((i & 7) == 0)
        {
            printf ("   +---+---+---+---+---+---+---+---+\n");
            if (i <= 56)
            {
                printf (" %d |", 8 - (((unsigned) i) >> 3));
            }
        }

        if (piece[i] == EMPTY && ((((unsigned) i) >> 3) % 2 == 0 && i % 2 == 0))
            printf ("   |");
        else if (piece[i] == EMPTY
                 && ((((unsigned) i) >> 3) % 2 != 0 && i % 2 != 0))
            printf ("   |");
        else if (piece[i] == EMPTY)
            printf (" · |");
        else if (piece[i] == EPS_SQ)
            printf (" * |");
        else
        {
            if (color[i] == WHITE)
                printf (" %c |", pieceName[piece[i]]);
            else
                printf ("<%c>|", pieceName[piece[i] + 6]);
        }
        if ((i & 7) == 7)
            printf ("\n");
    }
    printf
    ("   +---+---+---+---+---+---+---+---+\n     a   b   c   d   e   f   g   h\n");
}


/* Returns the number of posible positions to a given depth. Based on the
 perft function on Danasah */
U64 perft (int depth)
{
    int i;
    int movecnt;			/* The number of available moves */
    U64 nodes = 0;

    if (!depth)
        return 1;

    MOVE moveBuf[200];		/* List of movements */

    /* Generate and count all moves for current position */
    movecnt = GenMoves (side, moveBuf);

    /* Once we have all the moves available, we loop through them */
    for (i = 0; i < movecnt; ++i)
    {
        /* Not a legal move? Then we unmake it and continue to the next one in the list */
        if (!MakeMove (moveBuf[i]))
        {
            TakeBack ();
            continue;
        }

        /* This 'if' takes us to the deep of the position */
        nodes += perft (depth - 1);
        TakeBack ();
    }

    return nodes;
}

/*get_ms() nos indica la hora actual en milisegundos desde el 1 de enero de 1970*/
int get_ms()
{
	gettimeofday (&tv, &tz);
	return(tv.tv_sec * 1000 + (tv.tv_usec / 1000));
}
