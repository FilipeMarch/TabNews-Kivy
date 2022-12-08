from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.utils import platform
from kivy.clock import Clock

# from icecream import ic

import certifi
import asks
import ssl
import os
import re

import webbrowser

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDIcon
from kivymd.uix.behaviors import RectangularRippleBehavior


class RectangleIconButton(
    RectangularRippleBehavior, F.ButtonBehavior, MDBoxLayout, MDIcon
):
    pass


kv_path = os.path.join(os.getcwd(), "screens", "post_screen.kv")
if kv_path not in Builder.files:
    Builder.load_file(kv_path)


class PostScreen(F.Screen):
    app = App.get_running_app()
    screen_loaded = F.BooleanProperty(False)
    slug = F.StringProperty()
    author = F.StringProperty()
    date = F.StringProperty()
    tabcoins = F.NumericProperty()
    title = F.StringProperty()
    body = F.StringProperty()

    def on_enter(self):
        print("Entered Post Screen")
        if not self.author:
            self.author = "cleitonmedeiros"
            self.slug = "como-contribuir-para-o-tabnews"
            self.date = "11 horas atrás"
            self.tabcoins = 13
            self.title = "Como contribuir para o TabNews"
            self.body = self.markdown_to_bbcode(
                "```[code]py def main(): \n    print('Hello World')```[/code]"
            )
        self.app.nursery.start_soon(self.load_screen_data)

    async def load_screen_data(self):
        """
        Get the content from tabnews.com.br/slug and load it into the screen
        """
        url = "https://tabnews.com.br/"
        route = f"/api/v1/contents/{self.author}/{self.slug}"

        session = asks.Session(
            ssl_context=ssl.create_default_context(cafile=certifi.where())
        )
        try:
            response = await session.get(url + route)
        except:
            print("Error while requesting data from tabnews.com.br")
            return

        print(response.json())

        if response.status_code == 200:
            self.screen_loaded = True
            self.date = response.json()["created_at"][:10]
            self.tabcoins = response.json()["tabcoins"]
            self.title = response.json()["title"]
            self.body = self.markdown_to_bbcode(response.json()["body"])
            # self.body = response.json()["body"]

    def markdown_to_bbcode2(self, s):
        links = {}
        codes = []

        def gather_link(m):
            links[m.group(1)] = m.group(2)
            return ""

        def replace_link(m):
            return "[url=%s]%s[/url]" % (links[m.group(2) or m.group(1)], m.group(1))

        def gather_code(m):
            codes.append(m.group(3))
            return "[code=%d]" % len(codes)

        def replace_code(m):
            return "%s" % codes[int(m.group(1)) - 1]

        def translate(p="%s", g=1):
            def inline(m):
                s = m.group(g)
                s = re.sub(r"(`+)(\s*)(.*?)\2\1", gather_code, s)
                s = re.sub(r"\[(.*?)\]\[(.*?)\]", replace_link, s)
                s = re.sub(r"\[(.*?)\]\((.*?)\)", "[url=\\2]\\1[/url]", s)
                s = re.sub(r"<(https?:\S+)>", "[url=\\1]\\1[/url]", s)
                s = re.sub(r"\B([*_]{2})\b(.+?)\1\B", "[b]\\2[/b]", s)
                s = re.sub(r"\B([*_])\b(.+?)\1\B", "[i]\\2[/i]", s)
                return p % s

            return inline

        s = re.sub(r"(?m)^\[(.*?)]:\s*(\S+).*$", gather_link, s)
        s = re.sub(r"(?m)^    (.*)$", "~[code]\\1[/code]", s)
        s = re.sub(r"(?m)^(\S.*)\n=+\s*$", translate("~[size=200][b]%s[/b][/size]"), s)
        s = re.sub(r"(?m)^(\S.*)\n-+\s*$", translate("~[size=100][b]%s[/b][/size]"), s)
        s = re.sub(r"(?m)^#\s+(.*?)\s*#*$", translate("~[size=200][b]%s[/b][/size]"), s)
        s = re.sub(
            r"(?m)^##\s+(.*?)\s*#*$", translate("~[size=100][b]%s[/b][/size]"), s
        )
        s = re.sub(r"(?m)^###\s+(.*?)\s*#*$", translate("~[b]%s[/b]"), s)
        s = re.sub(r"(?m)^> (.*)$", translate("~[quote]%s[/quote]"), s)
        s = re.sub(r"(?m)^[-+*]\s+(.*)$", translate("~[list]\n[*]%s\n[/list]"), s)
        s = re.sub(r"(?m)^\d+\.\s+(.*)$", translate("~[list=1]\n[*]%s\n[/list]"), s)
        s = re.sub(r"(?m)^((?!~).*)$", translate(), s)
        s = re.sub(r"(?m)^~\[", "[", s)
        s = re.sub(r"\[/code]\n\[code(=.*?)?]", "\n", s)
        s = re.sub(r"\[/quote]\n\[quote]", "\n", s)
        s = re.sub(r"\[/list]\n\[list(=1)?]\n", "", s)
        s = re.sub(r"(?m)\[code=(\d+)]", replace_code, s)

        return s

    def markdown_to_bbcode(self, s):
        """Convert markdown tags to kivy style bbcode tags.
        Does not always work reliably. Best to not mix URLs and tags on the same line in markdown.

        :type s: str
        """

        def tags_in_excepted_portion(text, start_index, end_index, exception_regex):
            """Valid entrances are:
            _start without space between the _ and the first and last word.
            multilines are allowed. But one empty line gets out the italic mode._
            No effect inside URLs.
            """

            matches_iterator = re.finditer(exception_regex, text)

            for match in matches_iterator:
                match_start = match.start(0)
                match_end = match.end(0)

                if ((match_start <= start_index) and (start_index <= match_end)) or (
                    (match_start <= end_index) and (end_index <= match_end)
                ):
                    return True
            return False

        def single_tag_context_parser(
            text, regex_expression, bb_code_tag, replacement_size=1
        ):
            """Valid entrances are:
            _start without space between the _ and the first and last word.
            multilines are allowed. But one empty line get out the italic mode._
            No effect inside URLs.
            """

            # Used to count how many iterations are necessary on the worst case scenario.
            matches_iterator = re.finditer(regex_expression, text)

            # The exclusion pattern to remove wrong blocks from being parsed.
            next_search_position = 0

            # Iterate until all the initial matches list to finish.
            for element in matches_iterator:

                # To perform a new search on the new updated string.
                match = re.search(regex_expression, text[next_search_position:])

                # Exit the parsing iteration when not more matches are found.
                if match is None:
                    break

                start_index = match.start(0)
                end_index = match.end(0)

                start_index = start_index + next_search_position
                end_index = end_index + next_search_position

                next_search_position = start_index + replacement_size

                # Exclude from URLs.
                if tags_in_excepted_portion(
                    text,
                    start_index,
                    end_index,
                    # Also exclude gender asterisk in German.
                    r"(<(https?:\S+)>)|(\[(.*?)\]\((.*?)\))|\w+\*([^.\s\n]*\w+)",
                ):
                    continue

                if end_index + replacement_size > len(text):

                    text = (
                        text[0:start_index]
                        + "[{0}]".format(bb_code_tag)
                        + text[start_index + replacement_size : end_index]
                        + "[/{0}]".format(bb_code_tag)
                    )

                else:

                    text = (
                        text[0:start_index]
                        + "[{0}]".format(bb_code_tag)
                        + text[start_index + replacement_size : end_index]
                        + "[/{0}]".format(bb_code_tag)
                        + text[end_index + replacement_size :]
                    )
            return text

        def get_bulleted_list(text, regex_expression, bb_code_tag, replacement_size=1):
            return

        def translate(formatting_rule="%s", target_group=1):
            def inline(match_object):
                """Recursive function called by the `re.sub` for every non-overlapping occurrence of the pattern.

                :param match_object: An `sre.SRE_Match object` match object.
                """
                s = match_object.group(target_group)
                # Headers
                s = re.sub(
                    r"^#\s+(.*?)\s*$", "[size=24dp][b]\\1[/b][/size]", s
                )  # Header first level
                s = re.sub(
                    r"^##\s+(.*?)\s*$", "[size=20dp][b]\\1[/b][/size]", s
                )  # Header second level
                s = re.sub(r"^###\s+(.*?)\s*$", "[b]\\1[/b]", s)  # Header third level
                s = re.sub(
                    r"^####\s+(.*?)\s*$", "[i][b]\\1[/b][/i]", s
                )  # Header fourth level

                # > Quote
                s = re.sub(r"^> (.*)$", "[color=A9A9A9]\\1[/color]", s)
                # * List
                s = re.sub(r"^[-+*]\s+(.*)$", "• \\1", s)
                return formatting_rule % s

            return inline

        # Bold and italic.
        # It re-uses several expressions, needs to be parsed before everything else,
        # because it needs several hacks (?<=\s), as `_` symbol is often used in URLs.
        print("s antes: \n\n\n", s)
        s = single_tag_context_parser(
            s, r"\*\*[^ \n]([^\*]+?)[^ \n](?=\*\*)", "b", 2
        )  # **Bold**
        print("s depois: \n\n\n", s)
        s = single_tag_context_parser(
            s, r"{0}[^ \n]([^{0}]+?)[^ \n](?={0})".format("\*"), "i"
        )  # *Italic*
        s = single_tag_context_parser(
            s, r"__[^ \n]([^_]+?)[^ \n](?=__)", "b", 2
        )  # __Bold__
        s = single_tag_context_parser(
            s, r"{0}[^ \n]([^{0}]+?)[^ \n](?={0})".format("_"), "i"
        )  # _Italic_
        s = single_tag_context_parser(
            s, r"~~[^ \n]([\s\S]+?)[^ \n](?=~~)", "s", 2
        )  # ~Strikethrough~

        print("s fim: \n\n\n", s)

        # URLs. Kivy Label style.
        s = re.sub(r"<(https?:\S+)>", '[color=0000ff][ref="\\1"]\\1[/ref][/color]', s)
        s = re.sub(
            r"\[(.*?)\]\((.*?)\)", '[color=0000ff][ref="\\2"]\\1[/ref][/color]', s
        )

        s = re.sub(r"(?m)^((?!~).*)$", translate(), s)
        s = re.sub(r"\[/quote]\n\[quote]", "\n", s)

        print("s fim: \n\n\n", s[:150])
        return s

    def open_link(self, object, link_reference):
        print(f"Opening link: {link_reference}")
        if platform != "android":
            webbrowser.open(link_reference[1:-1])
        else:
            try:
                from jnius import autoclass
                from android import mActivity

                Intent = autoclass("android.content.Intent")
                Uri = autoclass("android.net.Uri")
                String = autoclass("java.lang.String")

                intent = Intent()
                intent.setAction(Intent.ACTION_VIEW)
                intent.setData(Uri.parse(String(link_reference[1:-1])))
                mActivity.startActivity(intent)

            except Exception as e:
                print(e)
