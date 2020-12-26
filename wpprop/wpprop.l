%top {
// break the cyclic dependency between scanner and parser headers
// typedef union YYSTYPE YYSTYPE;
// typedef struct YYLTYPE YYLTYPE;
}

%{

#include <stdio.h>
#include "wpprop-parser.h"

%}

DIGIT [0-9]

%option noyywrap
%option prefix="wpprop_yy"
%option reentrant
%option nounput
%option warn 
/* %option nodefault */
%option stack
%option bison-bridge bison-locations

%option yylineno
/* %x STRING_ESCAPE */

%%

[ {
    return tOPEN;
}

] {
    return tCLOSE;
}

// need some logic that returns a token wo a close tag
link|image {
    return tPROP;
}
%%
