import enchant
from enchant.checker import SpellChecker

_reference = 'https://pypi.python.org/pypi/pyenchant/1.6.5'
__author__ = 'maria'


class EnchantSpellChecker:
    def __init__(self):
        self.d = None   # for the current dictionary
        self.spell_checker = None
        self.errors_in_text = []
        self.correct_list = []

    def dict_exists(self, dict_lang):
        if dict_lang == 'en':
            dict_lang = 'en_US'
            if enchant.dict_exists(dict_lang):
                self.d = enchant.request_dict(dict_lang)
                self.spell_checker = SpellChecker(self.d.tag)
                return True
        else:
            print "No available dictionary"
            return False

    def spell_checker_for_text(self, text):
        self.spell_checker.set_text(text)
        for err in self.spell_checker:
            # print "ERROR:", err.word
            self.errors_in_text.append(err.word)
        # for word in self.errors_in_text:
        # print self.spell_checker.suggest(word)
        return self.errors_in_text

    def correct_list(self):
        for word in self.errors_in_text:
            self.correct_list.append(self.spell_checker.correct(word))
        return self.correct_list

    def correct_word(self, word):
        self.spell_checker.set_text(word)
        self.spell_checker.word = word
        return self.spell_checker.suggest()

    # so as not to create a new spellchecker object for every tweet
    def clean_up(self):
        self.d = None   # for the current dictionary
        self.spell_checker = None
        self.errors_in_text = []
        self.correct_list = []

    def spell_checker_for_word(self, word):
        error = None
        self.spell_checker.set_text(word)
        for err in self.spell_checker:
            error = err.word
        return error

#######################################################################################################################
#test
#print enchant.list_languages()

'''d = EnchantSpellChecker()
if d.dict_exists("en")==True:
    #d.spell_checker_for_text("this is jsts a testd heeellooo")
    #print d.correct_word("heellloooo")
    #print d.spell_checker_for_word('heeeelloooo')
    #d.spell_checker_for_word('this')
    print d.spell_checker_for_word('hemp')'''