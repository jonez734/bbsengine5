%{
/* c code here */
%}

%union {
    struct _command Command;
    struct _word Word;
}

%token tCOMMAND
%token tWORD
