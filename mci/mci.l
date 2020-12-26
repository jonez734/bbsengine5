%%

"{" {
      return tOPEN;
}
   
"}" {
      return tCLOSE;
}

"black" |
"red" |
"yellow" |
"green" |
"blue" |
"cyan" |
"magenta" |
"white"
{
    return tCOLOR;
}

"kolorific"
{
    return tKOLORIFICOPEN;
}
"/kolorific"
{
    return tKOLORIFICCLOSE;
}

"negative"
{
    return tNEGATIVEOPEN;
}
"/negative"
{
    return tNEGATIVECLOSE;
}


%%
