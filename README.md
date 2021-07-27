# bbsengine5

- uses ttyio4
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
  * [ ] runcallback() is not working in bbs.py
  * [ ] bbs.new(): fix handling of inputboolean() result (True/False/etc, not a string)
  * [x] remove 'member' function inside bbs.py, replace it w external script, 'engine'
  * [x] inputpassword()
  * [x] add 'prg' to engine.__node
  * [ ] fix member.buildrecord() such that it converts a dict to a json string
  * [ ] move collapselist() to bbsengine5 from ttyio4
  * [ ] handlemenu() / displaymenu()
    - [x] make each label the same width (ryan)
    - [x] add 'description' field to each option
    - [ ] using unhandled keys disrupts cursor position (F10)
    - [x] optional help for each menu item. F1 or ?
    - [ ] use {var} to determine colors in displaymenu()
      - [ ] at most 3 passes to convert commands to ouptut
      - [ ] func which counts number of commands unprocessed
  * inputpassword()
    - [x] ctrl-u does not behave
    - [ ] key-repeat sometimes shows entered char, most times it's fine (race!) (stigg)
  * bbsengine.runcallback()
    - [ ] if callback is ".member", remove leading ".", eval() rest, then run it if it's callable.
  * database
    - [ ] do not point views like empyre.player to engine.node, as this can disrupt production services when the engine.node view is updated.
      * currently, any prg that depends on engine.node needs to be
        re-created, increasing complexity of an engine.node update.
      * [ ] move coalese() calls and left joins in view engine.node to table engine.__node
      * [ ] step through all projects and make the views point to engine.__node instead of engine.node
      * [ ] use 'matrialized views' in some cases

- notes
  * bbsengine5.runcallback() does not handle local functions (f.e. member) as strings. scope issues. use ref instead if same module.

- bbsengine.diceroll()
  * mean and average are the same thing
  * median
