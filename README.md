# bbsengine5

- uses ttyio5
- database
  * databaseconnect()
  * insert()
  * update()
  * insertnode()
  * updatenode()
  * updateattributes()
  * updatenodesigs()
  * inputdate()
  * getsig()
  * getflag()
  * updateflag()
  * checkflag()
  * getcurrentmemberid()
  * getcurrentmemberlogin() -- used by empyre
  * getmembercredits()
  * getcurrentmembercredits() -- queries loginid then calls getmembercredits()
  * diceroll() -- used by empyre
    - https://www.statisticshowto.com/median/
- todo
  * [ ] runcallback() is not working in bbs.py (scope)
  * [ ] bbs.new(): fix handling of inputboolean() result (True/False/etc, not a string)
  * [x] remove 'member' function inside bbs.py, replace it w external script, 'engine'
  * [x] add 'prg' to engine.__node
  * [ ] fix member.buildrecord() such that it converts a dict to a json string
  * [ ] move collapselist() to bbsengine5 from ttyio4
  * [ ] handlemenu() / displaymenu()
    - [x] make each label the same width (ryan)
    - [x] add 'description' field to each option
    - [ ] using unhandled keys disrupts cursor position (F10)
    - [x] optional help for each menu item. F1 or ?
    - [x] use {var} to determine colors in displaymenu()
  * inputpassword()
    - [x] ctrl-u does not behave
    - [ ] key-repeat sometimes shows entered char, most times it's fine (race!) (stigg)
    - [ ] sometimes echos characters between the mask char. timing! 
  * bbsengine.runcallback()
    - [ ] if callback is ".member", remove leading ".", eval() rest, then run it if it's callable. does not work when function is inside
      bbsengine
  * database
    - [ ] do not point views like empyre.player to engine.node, as this can disrupt production services when the engine.node view is updated.
      * currently, any prg that depends on engine.node needs to be re-created, greatly increasing complexity of an engine.node update.
      * [ ] move coalese() calls and left joins in view engine.node to table engine.__node
      * [ ] step through all projects and make the views point to engine.__node instead of engine.node
      * [ ] use 'matrialized views' in some cases
  * [ ] detect terminal width, possibly use horizontal menu
  * [ ] if a menuitem is disabled, skip it when using arrow keys
  * [ ] change-sig in shell
  * [ ] add 'currentsig' attribute to member
  * [ ] 'R' (read) -- check type and permissions, handle accordingly even when node type is not a 'post'
  * [ ] datestamp() does not handle timezone (%Z blank)
    * https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    * https://stackoverflow.com/questions/1301493/setting-timezone-in-python
    * https://www.kite.com/python/answers/how-to-set-the-timezone-of-a-datetime-in-python
    * https://howchoo.com/g/ywi5m2vkodk/working-with-datetime-objects-and-timezones-in-python
    * https://www.w3resource.com/python-exercises/date-time-exercise/python-date-time-exercise-54.php
    * https://stackoverflow.com/questions/5873857/how-to-set-timezone-in-python-using-os-environ
    * https://ispycode.com/Blog/python/2016-08/Set-Timezone-Using-TZ-Environment-Variable
    * https://docs.python.org/3/library/datetime.html
  * [x] fix inputsig()
  * [x] !ttyio5 vars do not work
    * Menu() in ttyio4 works, Menu() in ttyio5 does not.
    * getvariable() always fails using ttyio5.
    * scope?
    * fix was to import ttyio5 in bbsengine5 instead of ttyio4
  * [ ] add database handle cache, port from bbsengine4
  * [x] add setarea()
  * [ ] Menu
     * [ ] commands inside descriptions break layout (len of desc wo commands)

- notes
  * bbsengine5.runcallback() does not handle local functions (f.e. member) as strings. scope issues. use ref instead if same module.
  * import runcallback from bbsengine5 solves the problem nicely.

- bbsengine.diceroll()
  * mean and average are the same thing
  * median

- inputsig()
  * add EROS to engine.flag
  * add EROS flag for 'jonez'

- node
    * e.__node instead of engine.node, makes updating engine.node easier
- [ ] use 'matrialized views' in some cases
- [ ] detect terminal width, possibly use horizontal menu
- [ ] if a menuitem is disabled, skip it when using arrow keys
- [ ] change-sig in shell
- [ ] add 'currentsig' attribute to member
- [ ] 'R' (read) -- check type and permissions, handle accordingly even when node type is not a 'post'
- Menu
    * [x] in some cases, glitch with {var:menu.boxcharcolor} (only right
      side of title)
- [ ] port bbsengine4/sql/moderator.sql
- notes
  * bbsengine5.runcallback() does not handle local functions (f.e. member) as strings. scope issues. use ref instead if same module.

- [9.9. Date/Time Functions and Operators](https://www.postgresql.org/docs/current/functions-datetime.html)
- [CodePen Animated SVG Avatar v2](https://codepen.io/dsenneff/pen/2c3e5bc86b372d5424b00edaf4990173)
- [pypager](https://github.com/prompt-toolkit/pypager)
- [ ] pager
    * check cursor position after every echo(), if it is ~lineheight, print a prompt.
- [X] inputsig() works great in bbsengine4, but bbsengine5 cannot handle 'top.entertainment.*'
- [ ] port sigcompleter class from bbsengine5 and change it to handle project names.
- [ ] update inputprojectname() to use projectnamecompleter
- [ ] Menu() should properly handle commands inside any string (length, right border is offset)
- [ ] stash cursor position when start of menu, stash cursor position when printing prompt, subtract, use that number for number of {cursorup}s. handles output of preprompthook()
- [ ] in Menu, add a way to allow commands (color changes) in the status message
- [ ] setarea(), poparea()
    * now has an 'areastack'.
    * poparea() is used pop an area off of the stack and to set the status (bottombar) to the last item in the stack.
    * updatebottombar() call hard-codes color and spacing. change this so it is configurable for errors and warnings.
- [ ] diceroll() should accept 'count' of 1 as mode 'single'
- [x] handle Menu submenus correctly (@since 20211122 @done 20211201)
     * uses a global var called 'menuitemresults'
     * must use a globally unique menuitem name
