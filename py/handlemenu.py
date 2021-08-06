
#def handlemenu(args, items, oldrecord, currecord, prompt="option", defaulthotkey=""):
#  hotkeys = {}
#
#  hotkeystr = ""
#
#  for item in items:
#      label = item["label"].lower()
#      hotkey = item["hotkey"].lower() if "hotkey" in item else None
#      format = item["format"] if "format" in item else "%s"
#
#      hotkeys[hotkey] = item # ["longlabel"] if item.has_key("longlabel") else None
#      if hotkey is not None:
#          hotkeystr += hotkey
#
#      if hotkey == "q":
#          continue
#
#      if hotkey is not None and hotkey in label:
#          label = label.replace(hotkey.lower(), "[{autocyan}%s{/autocyan}]" % (hotkey.upper()), 1)
#      else:
#          label = "[{autocyan}%s{/autocyan}] %s" % (hotkey, label)
#
#      if "key" in item:
#          key = item["key"]
#          if key in oldrecord and key in currentrecord and oldrecord[key] != currecord[key]:
#              curval = format % currecord[key]
#              oldval = format % oldrecord[key]
#              buf = "%s: %s (was %s)" % (label, curval, oldval)
#          else:
#              curval = format % currecord[key]
#              buf = "%s: %s" % (label, curval)
#      elif "changed" in item:
#        if item["changed"] is True:
#          buf = "%s (changed)" % (label)
#      else:
#          buf = label
#
#      required = item["required"] if "required" in item else False
#      if required is True:
#        buf = "{autored}*{/autored} "+buf
#      ttyio.echo(buf)
#
#  if "q" in hotkeys:
#      ttyio.echo("{f6}[{autocyan}Q{/autocyan}]uit")
#
#  if oldrecord != currecord:
#      ttyio.echo("{f6}{autocyan}** NEEDS SAVE **{/autocyan}{f6}")
#  ch = ttyio.accept(prompt, hotkeystr, defaulthotkey).lower()
#  if ch == "":
#      return None
#
#  longlabel = hotkeys[ch]["longlabel"] if "longlabel" in hotkeys[ch] else None
#  if longlabel is not None:
#      ttyio.echo("{autocyan}%s{/autocyan} -- %s" % (ch.upper(), longlabel))
#  else:
#      ttyio.echo("{autocyan}%s{/autocyan}" % (ch.upper()))
#  res = hotkeys[ch] if ch in hotkeys else None
#  return res
