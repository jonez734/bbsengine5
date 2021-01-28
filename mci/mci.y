%{
/* c code here */
%}

%union {
    struct _command Command;
    struct _word Word;
    struct _whitespace Whitespace;
}

%token tCOMMAND
%token tWORD
%token tWHITESPACE
