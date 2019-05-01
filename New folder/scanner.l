%{
	#include <stdio.h>
	#include <stdlib.h>
	#include <string.h>
	#include <assert.h>
	#include <stdlib.h>

	#include "parser.tab.h"
	char *p;
%}

Blank [ \t\v\n\f]+

Number [0-9]
Alphabet [a-zA-Z_]
%%


"//".*                                    { /* DO NOTHING */ }
[/][*][^*]*[*]+([^*/][^*]*[*]+)*[/]       { /* DO NOTHING */ }

{Blank} {;}
"int" 	 { printf("INT "); return(INT); }
"int16"  { printf("INT16 "); return(INT16); }
"string" { printf("STRING "); return(STRING); }
"if"	{ printf("IF "); return(IF); }
"elif"	{ printf("ELIF "); return(ELIF); }
"else"	{ printf("ELSE "); return(ELSE);	}

"for"	{ printf("FOR "); return(FOR); }
"do"	{ printf("DO "); return(DO); }
"while"	{ printf("WHILE "); return(WHILE); }

"print"		{ printf("PRINT "); return(PRINT); }
"println"	{ printf("PRINT_LN "); return(PRINT_LN); }

"<" 	{ printf("< "); return(L_OP); }
">" 	{ printf("> "); return(G_OP); }
"<=" 	{ printf("<= "); return(LE_OP); }
">=" 	{ printf(">= "); return(GE_OP); }
"==" 	{ printf("== "); return(EQ_OP); }
"!=" 	{ printf("!= "); return(NE_OP); }

"++" 	{ printf("++ "); return(INC_OP); }
"--" 	{ printf("-- "); return(DEC_OP); }

{Alphabet}?\"(\\.|[^\\"])*\" { 
		p=(char *)calloc(strlen(yytext)+1,sizeof(char)); 
		strcpy(p,yytext);
        yylval=p;
		printf("DQ_MSG ");
		return(DQ_MSG); }
{Alphabet}+ {  
		p=(char *)calloc(strlen(yytext)+1,sizeof(char)); 
		strcpy(p,yytext);
        yylval=p; 
		printf("ID "); 
		return(IDENTIFIER); 
}

{Number}+ { 
		p=(char *)calloc(strlen(yytext)+1,sizeof(char)); 
		strcpy(p,yytext);
        yylval=p;
		printf("CONST10 ");
		return(CONSTANT10); }
		
0[xX][a-fA-F0-9]+ { 
		p=(char *)calloc(strlen(yytext)+1,sizeof(char)); 
		strcpy(p,yytext);
        yylval=p;
		printf("CONST16 "); 
		return(CONSTANT16); }

"=" 	{ yylval = yytext[0]; printf("= "); return('='); }
"-" 	{ yylval = yytext[0]; printf("- "); return('-'); }
"+" 	{ yylval = yytext[0]; printf("+ "); return('+'); }
"*" 	{ yylval = yytext[0]; printf("* "); return('*'); }
"/" 	{ yylval = yytext[0]; printf("/ "); return('/'); }
"%" 	{ yylval = yytext[0]; printf("% "); return('%'); }

"(" 	{ printf("( "); return('('); }
")" 	{ printf(") "); return(')'); }
"["		{ printf("[ "); return('['); }
"]"		{ printf("] "); return(']'); }
"{"		{ printf("{ "); return('{'); }
"}"		{ printf("} "); return('}'); }

","		{ printf(", "); return(','); }
";" 	{ printf("; "); return(';'); }

.  {printf("Unexpected Input %c\n",yytext[0]);}
%%



