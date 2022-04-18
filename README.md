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
  * diceroll() -- used by empyre, casino, etc
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
      - [ ] sometimes echos keypresses between the mask char. timing! 
    * bbsengine.runcallback()
      - [ ] if callback is ".member", remove leading ".", eval() rest, then run it if it's callable. does not work when function is inside bbsengine
    * database
      - [ ] do not point views like empyre.player to engine.node, as this can disrupt production services when the engine.node view is updated.
        * currently, any prg that depends on engine.node needs to be re-created, greatly increasing complexity of an engine.node update.
        * [ ] move coalese() calls and left joins in view engine.node to table engine.__node
        * [ ] step through all projects and make the views point to engine.__node instead of engine.node
        * [ ] use 'matrialized views' in some cases
    * [ ] detect terminal width, possibly use horizontal menu
    * [ ] if a menuitem is disabled, skip it when using arrow keys
    * [ ] add 'currentsig' attribute to member
    * [ ] 'R' (read) -- check type and permissions, handle accordingly even when node type is not a 'post'
    * [ ] datestamp() does not handle timezone (%Z blank)
    * [x] fix inputsig()
    * [x] !ttyio5 vars do not work
      * Menu() in ttyio4 works, Menu() in ttyio5 does not.
      * getvariable() always fails using ttyio5.
      * scope?
      * fix was to import ttyio5 in bbsengine5 instead of ttyio4
    * [ ] add database handle cache, port from bbsengine4 (@done 20220201)
    * [x] add setarea()
    * [ ] Menu
       * [ ] commands inside descriptions break layout (len of desc wo commands)
       * [ ] allow each menuitem to assign a hotkey, overrides default of A-P (@since 20211216)
    * inputfilename()
      - [ ] tab-complete in inputfilename() is broken. chdir to expanded args.basedir? (@since 20211205)
      - inputfilename() works if subdir is not diff. any way to chdir()?
      - resolve relative paths as input (combine w cwd, make sure completer works) (@since 20211216)
    * getdate()
      - calls time.tzset() explicitly
    * LocalTimezone - not used anywhere in bbsengine5
    * datestamp() does not handle timezones correctly (@since 20211216)
      - does not show empyre.newsentrys with timezone, even tho it is stored correctly (@since 20211216)
- shell
    * [ ] turn off tab-complete after a command has been entered. remove delims? (@since 20211211)
    * [ ] confirm no bash chars can be entered at the bbs prompt (@since 20211211) @security
    * [x] handle setarea() correctly (@since 20211211) (@done 20211214)
    * [ ] somehow remove requirement of bbsengine.initscreen() at each run through the while loop (@since 20211214)
    * [ ] import given module, call main(). does this keep it runnable from a shell (tcsh) prompt? (@since 20211214)
    * [ ] in 'socrates.addpost', how to call main() (aka initscreen()) if needed (@since 20211214)
    * [ ] if callback is 'socrates', import module and call socrates.main() (@since 20211214)
    * [ ] if callback is 'socrates.addpost', import module and call 'addpost' (@since 20211214)
    * [ ] in __main__, be sure to initscreen() (@since 20211214)
    * [ ] use 'cmd2' (@since 20220130)
       * [ ] cmd2 uses 'poutput' with very similar function to ttyio.echo()
    * [ ] change-sig in shell (@since 20220130)
    * https://github.com/python-cmd2/cmd2/issues/194
    * if point and buffer len are the same, increment idle timer
    * https://stackoverflow.com/questions/301134/how-to-import-a-module-given-its-name-as-string?rq=1
    * https://stackoverflow.com/questions/7719466/i-have-a-string-whose-content-is-a-function-name-how-to-refer-to-the-correspond
    * https://www.google.com/search?q=cmd2+disable+built-in+alias&oq=cmd2+disable+built-in+alias&aqs=chrome..69i57.10208j0j7&sourceid=chrome&ie=UTF-8
    * environment vars:
       * START: room where a member appears after login (@since 20220306)
       * HOME: the room where 'home' command takes you (@since 20220306)
       * TITLE, MOUT, MIN, MMOUT, MMIN, MDEST, MCLONE, MVIS, and MINVIS
    * update PYTHONPATH based on member.flags (wiz, dead, etc)
    * static command tables need a way to check access, do not show commands a member does not have access to ("engine", etc)
    * try to import cmd_<command> file based on PYTHONPATH
    * check for callable cmd_foo.cmd_foo()
    * check current environment for the command
      * exits
    * present(), environment(), exits()
    * store engine.member.env(ironment) instead of 'currentroom'
    * __init__()
    * reset()
    * handle commands. search for _*.py
    * [ ] generic object
      * set/get attributes. (@since 20220331)
      * id()
      * move()
      * remove()
      * clean_up()
      * receive_object()
      * release_object()
      * check_light()
    * [ ] room object
      * query_exit_dirs()
      * id()
      * reset()
      * query_ambient_light() calls weather_d
      * receive_objects() returns 1

- editor
    * figure out a way to run a restricted 'gedit' (@since 20220210)
- notes
    * bbsengine5.runcallback() does not handle local functions (f.e. member) as strings. scope issues. use ref instead if same module.
    * import runcallback from bbsengine5 solves the problem nicely.
    * https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    * https://stackoverflow.com/questions/1301493/setting-timezone-in-python
    * https://www.kite.com/python/answers/how-to-set-the-timezone-of-a-datetime-in-python
    * https://howchoo.com/g/ywi5m2vkodk/working-with-datetime-objects-and-timezones-in-python
    * https://www.w3resource.com/python-exercises/date-time-exercise/python-date-time-exercise-54.php
    * https://stackoverflow.com/questions/5873857/how-to-set-timezone-in-python-using-os-environ
    * https://ispycode.com/Blog/python/2016-08/Set-Timezone-Using-TZ-Environment-Variable
    * https://docs.python.org/3/library/datetime.html

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
- [ ] in Menu, add a way to allow commands (color changes) in the status message (@since 20211216)
- [x] setarea(), poparea() (@since 20211216 @done 20211216)
    * now has an 'areastack'.
    * poparea() is used to pop an area off of the stack and to set the bottombar to the last item in the stack.
    * updatebottombar() call hard-codes color and spacing. change this so it is configurable for errors and warnings.
    * {var:engine.areacolor}
    * setarea() has a 'stack' kwarg for when it is not desired to add an area to areastack (default True) (@since 20211214 @done 20211214)
- [ ] initscreen()
     * --when initializing, use {curpos} instead of {cursorup:3} (@since 20211211)--
- [ ] diceroll() should accept 'count' of 1 as mode 'single'
- [x] handle Menu submenus correctly (@since 20211122 @done 20211201)
     * uses a global var called 'menuitemresults'
     * must use a globally unique menuitem name
- links
    * https://github.com/pam-pgsql/pam-pgsql
    * https://www.google.com/search?q=postgresql+login+pam&sxsrf=AOaemvKs_26EZuP883j53y8Qi4erqQvRCg%3A1639349094908&ei=Znu2YbTiNq2GwbkPvJOCeA&ved=0ahUKEwi0rdujq9_0AhUtQzABHbyJAA8Q4dUDCA4&uact=5&oq=postgresql+login+pam&gs_lcp=Cgdnd3Mtd2l6EAMyBggAEBYQHjIGCAAQFhAeOgcIIxCwAxAnOgcIABBHELADOgYIABAIEB46CAgAEAgQChAeOgYIABAHEB46BQgAEJECOgUIABCABDoECAAQCjoECCMQJzoICAAQgAQQsQNKBAhBGABKBAhGGABQrwFYhK_vJGC8sO8kaAJwAngBgAHtAYgBiQ6SAQYxMC43LjGYAQCgAQHIAQnAAQE&sclient=gws-wiz
- [x] setarea() needs a way to set a consistent rightbuf (@since 20211216 @done 20211216)
    * member.name, member.credits everywhere in bbs.py
    * player.name, player.coins in empyre
    * left and right side can be str or callable
    * right is optional (None), left is not
    * each prg needs to define a setarea() that handles the rightside
- [ ] {wait} command does not execute at the right time (@since 20220112)

```[~/<1>bbsengine5/py] [DING!] [jam@cyclops] % python
Python 3.9.9 (main, Nov 19 2021, 00:00:00) 
[GCC 10.3.1 20210422 (Red Hat 10.3.1-1)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import importlib
>>> x = importlib("weather")
>>> x = importlib.import_module("weather")
>>> callable(x.main)
True
>>> eval("main")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<string>", line 1, in <module>
NameError: name 'main' is not defined
>>> eval("main", x)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: globals must be a dict
>>> eval("main", {"x":x})
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<string>", line 1, in <module>
NameError: name 'main' is not defined
>>> eval("x.main", {"x":x})
<function main at 0x7f188ee140d0>
```

- 'groups' (@since 20220110)
    * every member can be a member of many groups. 
    * admin flag
    * see sampic
- [ ] port bbsengine4 sigcompleter and verifysigpath() re: top.eros.* (@since 20220122)

== facebook integration ==
===

- [ ] javascript-based facebook login (@since 20220108)
- https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow

- https://www.the-art-of-web.com/system/apache-pgsql-authentication/ (@since 20220116)
- [ ] anywhere that uses inputsig() should deny access to 'top.eros.*' without a special flag set, just like sigcomplete() does.
  i.e. you cannot directly type 'top.eros' wo EROS flag set. verify function should reject.
- [ ] map between current version and (zoidweb4,...) (@since 20220121)
    * versions seq, has "zoidweb4", "zoidweb5", etc keys w proper values
    * seamless integration w vulcan and sophia

- [ ] address issue of :emoji: in bbsengine.title()  (uses centering, which breaks) (@since 20220402)
    * short by 2 bytes per emoji use.... sometimes
    * https://stackoverflow.com/questions/30775689/python-length-of-unicode-string-confusion
    * https://bytes.com/topic/python/answers/537499-how-find-number-characters-unicode-string
- [x] remove dbh.commit() call in updatenodesigs() in an effort to fix a bug in socrates.addpost() @since 20220221 @done 20220223
- [ ] setarea() (@since 20220223)
    * [x] fix handling of rightbuf so it works w emojis
    * [ ] fix handling of leftbuf so it works w emojis
- [ ] upgrade setup.py from distutils to setuptools (@since 20220301)
- [ ] setarea() (@since 20220302)
    * [x] ljust() - emojis work now (@since 20220302 @done 20220302)
    * [ ] :anchor: is correct, :ballot-box: is not (off by one space) (@since 20220302)

- [ ] move ljust() and center() to ttyio5 (@since 20220303)
- [ ] be sure to update Menu() re: ttyio.center()
- [x] inputsig() (specifically bbsengine.verifysig()) does not correctly handle multiple sigs (@since 20220315 @done 20220322)
- [ ] lpmuds downloads: http://lpmuds.net/downloads.html (@since 20220316)
- [ ] add attributes (jsonb) to engine.sig
- [ ] in inputsig(), check 'default' type: list = join(), str = as written, None = empty string (@since 20220318)
- [ ] mud: commodore pet keyboards are notorious for jamming, double keys, etc. cyberpunk (@since 20220320 pscug)
- [ ] https://youtu.be/kl6rsi7BEtk (@since 20220320 pscug)
- [x] verifysigpath() should call buildsiglist() @since 20220321 @done 20220322
- [x] verifysigpath() should check for top.eros.* access (@since 20220321) (@done 20220322)
- migrate to setuptools from disutils
    * https://www.google.com/search?q=python+migrate+distutils.core&sxsrf=APq-WBtUHvrBsMQpXS_jUsz2a5wQKDdjQw%3A1647915905395&ei=gTM5YpjPF8SMggfLz6jgCQ&ved=0ahUKEwjYk6SR1dj2AhVEhuAKHcsnCpwQ4dUDCA4&uact=5&oq=python+migrate+distutils.core&gs_lcp=Cgdnd3Mtd2l6EAM6BwgAEEcQsAM6BQghEKABSgQIQRgASgQIRhgAUIEdWKQlYIwyaAFwAXgAgAF4iAHZA5IBAzMuMpgBAKABAcgBCMABAQ&sclient=gws-wiz
    * https://www.google.com/search?q=python3+setuptools&oq=python3+setuptools&aqs=chrome..69i57j0i512l2j0i22i30l7.11022j0j7&sourceid=chrome&ie=UTF-8
    * https://setuptools.pypa.io/en/latest/setuptools.html
    * https://www.google.com/search?q=python3+setuptools&oq=python3+setup&aqs=chrome.0.69i59j69i57j0i512l2j0i20i263i512j0i512l3j0i10i433l2.1962j0j7&sourceid=chrome&ie=UTF-8
    * https://packaging.python.org/en/latest/tutorials/packaging-projects/
    * use setuptools.setup() instead of disutils.setup() (@since 20220324)
- setuptools is *not* a direct replacement for distutils.core. ref: bbsengine5.py changes not installed properly (did not get used by ogun) (@since 20220327)
- [-] calls to setarea() wo emojis are 2 spaces too wide (@since 20220328)
- [-] calls to setarea() are one space too short (@since 20220328)
- use of emojis in bbsengine.setarea() or bbsengine.title() are currently not supported (@since 20220329)
- [x] add 'getdate' to 'requires' list in setup.py for bbsengine5 (required by datestamp()) (@since 20220330) (@done 20220330)
- [x] fix datestamp() so it accepts a str, and uses getdate.getdate() to handle it (@since 20220330, @done 20220330)
- [ ] https://restrictedpython.readthedocs.io/en/latest/ -- run untrusted python code in a trusted environment (@since 20220402)

== mud ==

- [ ] living
    * [ ] query_vision() (tmi-2), part of living (@since 20220402)
        * checks to see if object is "blind" or if living has no_vision set
        * if no environment(), cannot see anything, return False
        * if full_vision attribute is set, return True
        * if environment()->query_light > 0, return True
        * check inventory
    - [ ] coins_carried
    - [ ] total_wealth
    - [ ] credit
    - [ ] debit
- [ ] cyberpunk theme (@since 20220402)
    - [ ] "commodore pet keyboard" has average cps, and medium/low error
      rate. "clickety clackety" pscug (@since 20220402)
    - [ ] "professional" above average cps, low error rate
- store object path in member record (mud.town-square, mud.wizhall, etc) (@since 20220402)
- load ROOM, step through exits{} adding commands to shell
- /srv/bed/.. 
    * __init__.py, handles bed features along w mud features (@since 20220403)
    - shell
    - cmds
    - std
    - obj
    - wiz
    - ghost
- in Base, add set() and query() (@since 20220403)

== bed ==

- [ ] client and bed side for socrates, etc (@since 20220402)
- [ ] query_verb()
- [ ] this_player()?
- [ ] environment() -> returns 'super' of object arg
- [ ] all_inventory()
- [ ] how does a Base know what room it is in? (@since 20220402)
- [ ] inpythonpath() - return true if $PYTHONPATH includes given arg (@since 20220402)
- [ ] in SHELL, I type a command, $PYTHONPATH is searched for cmd_<verb>.py, imported, and run (@since 20220402)
- [ ] add mud/ to PYTHONPATH (@since 20220422)
- [ ] consider updating/removing bbsengine.ResultIter with: https://www.programiz.com/python-programming/methods/built-in/iter (@since 20220403)
- [x] port bbsengine4.checkeros() to bbsengine5 (@since 20220406 @done 20220406)
- [ ] update verifysigpath() to use checkeros() (@since 20220406)
- https://github.com/seanmiddleditch/libtelnet
- https://www.postgresql.org/docs/current/auth-pam.html
- https://www-uxsup.csx.cam.ac.uk/pub/doc/suse/sles9/adminguide-sles9/ch20s02.html
- https://serverfault.com/questions/1056644/sshd-on-fedora-recent-changes-to-usepam-break-existing-security-permitrootpass
- https://linuxhint.com/linux_pam_tutorial/
