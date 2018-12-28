from termcolor import colored

from ..package_info import PACKAGE_INFO

_separator_1 = colored("##################################################", 'white')
_separator_2 = colored("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", 'white')

_logo = colored("""
 ___  ____ ___     ___ ____    ___ ____ ___  _ _  _
 |__] |___ |  \     |  |  |     |  |__| |__] |  \/
 |__] |___ |__/     |  |__|     |  |  | |__] | _/\_

""".strip(), 'green', attrs=['bold'])

_welcome_text = colored(f"""
 Welcome to {PACKAGE_INFO['PROGRAM_NAME']} {PACKAGE_INFO['VERSION']}!
 By {PACKAGE_INFO['AUTHOR']} ({PACKAGE_INFO['AUTHOR_EMAIL']})
 {PACKAGE_INFO['DATE']}
""", 'magenta')

# ^ The second and third lines of the logo need that extra space in the
# beggining to work well with colored()

BANNER=f"""
 {_separator_2}
 {_separator_1}
 {_logo}
 {_welcome_text}
 {_separator_1}
 {_separator_2}
"""
