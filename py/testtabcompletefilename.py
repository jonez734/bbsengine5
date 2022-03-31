def completeFilename(args=None, prefix=""):
    pass
    # Used to complete ~ and ~user strings
    def complete_users() -> List[str]:

        # We are returning ~user strings that resolve to directories,
        # so don't append a space or quote in the case of a single result.
        self.allow_appended_space = False
        self.allow_closing_quote = False

        users = []

        # Windows lacks the pwd module so we can't get a list of users.
        # Instead we will return a result once the user enters text that
        # resolves to an existing home directory.
        if sys.platform.startswith('win'):
            expanded_path = os.path.expanduser(text)
            if os.path.isdir(expanded_path):
                user = text
                if add_trailing_sep_if_dir:
                    user += os.path.sep
                users.append(user)
        else:
            import pwd

            # Iterate through a list of users from the password database
            for cur_pw in pwd.getpwall():

                # Check if the user has an existing home dir
                if os.path.isdir(cur_pw.pw_dir):

                    # Add a ~ to the user to match against text
                    cur_user = '~' + cur_pw.pw_name
                    if cur_user.startswith(text):
                        if add_trailing_sep_if_dir:
                            cur_user += os.path.sep
                        users.append(cur_user)

        return users
