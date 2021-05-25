#!/usr/bin/python
# coding: utf-8
import sys
from .greek_tools import (
    preprocess_word,
    strip_accents,
    in_dict_lower,
    dump,
    split_text_token,
    delete_non_greek_tokens,
    is_uc_word,
    is_greek_char,
    is_greek_string,
)

# I think this is not used, and we have the function below
# from read_dict5 import makeDict
import lxml
from lxml import etree
import re
import os
import codecs
import unicodedata


def add_word(word_count, word):

    word_no_punct = split_text_token(word)[1]
    word_no_punct = preprocess_word(word_no_punct)
    if len(word_no_punct) > 0:
        word = word_no_punct
    if True:  # is_greek_string(word):
        if word not in word_count:
            word_count[word] = 1
        else:
            word_count[word] += 1
    return word_count


def get_hocr_words(treeIn, word_count):
    words = treeIn.xpath(
        "//html:span[@class='ocr_word'] | //span[@class='ocr_word']",
        namespaces={"html": "http://www.w3.org/1999/xhtml"},
    )
    # word_count = {}
    for word in words:
        dhf = word.get("data-dehyphenatedform")
        if dhf == "" or word.text == None:
            next
        elif dhf != None:
            add_word(word_count, dhf)
            # print "# appending dhf", dhf
        elif word.text[-1] != "-":  # ommit blown hyphenated forms
            add_word(word_count, word.text)
            # print "# apending word", word.text


def make_ligatures(word):
    for pair in [["ae", "æ"], ["ff", "ﬀ"], ["oe", "œ"], ["fl", "ﬂ"], ["fi", "ﬁ"]]:
        word = word.replace(pair[0], pair[1])
    return word


def makeDict(fileName, migne_mode=False):
    from . import greek_tools

    frequency_limit = 0
    words = []
    mine = codecs.open(fileName, "r", "utf-8")
    for line in mine:
        line = unicodedata.normalize("NFC", line)
        try:
            (word, freq) = line.split(",")
        except ValueError:
            word = line
            freq = "5"
        freq = int(freq.rstrip("\r\n"))
        if freq > frequency_limit:
            word_prep = preprocess_word(word.rstrip("\n\r\x11"))
            if migne_mode:
                word_prep = make_ligatures(word_prep)
            words.append(word_prep)
    ##    for word in words:
    ##        print word
    return words


def makeNoAccentDict(fileName):
    no_accent_dict = {}
    mine = codecs.open(fileName, "r", "utf-8")
    for line in mine:
        (no_accent, word) = line.split(",")
        word = word.rstrip("\r\n")
        no_accent = no_accent.rstrip("\n\r\x11")
        no_accent_dict[no_accent] = word
    return no_accent_dict


def inNoAccentDict(word, no_acent_dict):
    try:
        output = no_accent_dict[strip_accents(word)]
        return output
    except:
        return False


def findOccurences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]


def bothHalvesInDict(my_dict, str1, str2):
    return ((str1 in my_dict) or in_dict_lower(my_dict, str1)) and (
        (str2 in my_dict) or in_dict_lower(my_dict, str2)
    )


def make_spellcheck_file(
    input_directory_path,
    dictionary_file_path,
    no_accent_dict_file_path,
    output_file_path,
    verbose,
):
    superscripts = "\u00B2\u00B3\u00B9\u2070\u2074\u2075\u2076\u2077\u2078\u2079"

    try:
        output_file_handle = open(output_file_path, "w")
        dir_in = input_directory_path
        # print dir_in
        dir_in_list = os.listdir(dir_in)
    # dir_out = sys.argv[2]
    except (IndexError, ValueError) as e:
        print(e)
        exit()
    if verbose:
        print("# making dicts")
    import time

    start_time = time.time()
    my_dict = makeDict(dictionary_file_path)
    dict_time = time.time() - start_time
    minutes = dict_time / 60.0
    my_dict = set(my_dict)
    no_accent_dict = makeNoAccentDict(no_accent_dict_file_path)
    if verbose:
        print("# dict building took", minutes, " minutes.")
    marker = "€"

    word_count = {}

    for file_name in dir_in_list:
        if file_name.endswith(".html"):
            simplified_name = file_name
            if file_name.startswith("output-"):
                simplified_name = file_name[7:]
            # print u"# " + simplified_name
            simplified_name = simplified_name.rsplit(".", 1)[0] + ".txt"
            # print u"new simplified name: " + simplified_name
            fileIn_name = os.path.join(dir_in, file_name)
            fileOut_name = os.path.join(dir_in, simplified_name)
            fileIn = codecs.open(fileIn_name, "r", "utf-8", errors="ignore")
            fileOut = open(fileOut_name, "w")
            # print u"# ", "checking", fileIn_name, "sending to ", fileOut_name
            try:
                treeIn = etree.parse(fileIn)
                get_hocr_words(treeIn, word_count)
            except (lxml.etree.XMLSyntaxError):
                if verbose:
                    print("XMLSyntaxError on printing " + simplified_name)
                pass

    total_count = 0
    total_biomass = 0
    counts = {}
    biomass = {}
    output_array = []
    output_dict = {}
    punct_split = "([\.,·;’\[\]\)\(])"
    punct_re = re.compile(punct_split)
    count = 0
    total = len(word_count)
    latin_suffixes = ["que", "ne", "ve"]
    for w in sorted(word_count, key=word_count.get, reverse=True):
        count = count + 1
        operation = "False"
        output = ""
        terminal_chars = "ς"
        if w in my_dict:
            operation = "True"
        elif in_dict_lower(my_dict, w) == True:
            operation = "TrueLower"
        elif inNoAccentDict(w, no_accent_dict):
            output = inNoAccentDict(w, no_accent_dict)
            operation = "NoAcc"
        elif len(punct_re.split(w)) == 3:
            punct_stripped = punct_re.sub("", w)
            if punct_stripped in my_dict or in_dict_lower(my_dict, punct_stripped):
                operation = "PunctStrip"
                output = punct_stripped
            else:
                split_on_punct = punct_re.split(w)
                if bothHalvesInDict(my_dict, split_on_punct[0], split_on_punct[2]):
                    output = (
                        split_on_punct[0] + split_on_punct[1] + " " + split_on_punct[2]
                    )
                    operation = "SplitOnPunct"

        if operation == "False":
            split = re.split(
                marker, re.sub("([" + terminal_chars + "])", r"\1" + marker, w)
            )
            if len(split) > 1:
                output = ""
                operation = "Split"
                for component in split:
                    if component != "":
                        if not (component in my_dict):
                            no_accent_component = inNoAccentDict(
                                component, no_accent_dict
                            )
                            if no_accent_component:
                                output = output + " " + no_accent_component
                                operation = "SplitNoAcc"
                            elif in_dict_lower(my_dict, component):
                                output = output + " " + component
                            else:
                                operation = "False"
                                output = ""
                                break
                        else:
                            output = output + " " + component

        if operation == "False":
            try:
                digit_groups = re.match(
                    '(^[·«„\[\("〈]*)([I\d'
                    + superscripts
                    + "]*?)([«»„.,!?;†·:〉\)\]"
                    + "]*$)",
                    w,
                    re.UNICODE,
                ).groups()
                output = (
                    digit_groups[0]
                    + re.sub("I", "1", digit_groups[1])
                    + digit_groups[2]
                )
                operation = "Numerical"
            except:
                pass
        for a_suffix in latin_suffixes:
            if w.endswith(a_suffix) and (
                w[: -1 * len(a_suffix)] in my_dict
                or in_dict_lower(my_dict, w[: -1 * len(a_suffix)])
            ):
                operation = "True"
        ##    if operation=="False" and re.match(u'[^\w\s]+',w,re.UNICODE):
        ##        operation = "Punctuation"
        if operation == "False" and (len(w) > 1):
            subs = [
                ["d", ["ὅ", "ό"]],
                ["δ", ["ὅ", "ὀ", "ό", "ὄ", "ὁ", "ό", "ο", "d"]],
                ["ῖ", ["ὶ"]],
                ["Τ", ["Υ"]],
                ["ἶ", ["ἷ"]],
                ["ἷ", ["ἶ"]],
                ["T", ["Υ"]],
                ["l", ["I", "ί", "ἰ", "ἱ", "Ἰ", "ἴ", "i", "ι"]],
                ["A", ["Α", "Ἀ", "Ἁ", "Λ"]],
                ["3", ["Β", "B"]],
                ["7", ["Τ", "ί", "Γ", "T"]],
                ["Ε", ["E", "Ἐ"]],
                ["Α", ["A", "Ἀ", "Δ"]],
                ["Ἀ", ["Ἄ", "Ἁ"]],
                ["Δ", ["Ἀ", "Α"]],
                ["α", ["z", "ο", "a", "σ"]],
                ["β", ["ἵ", "ῆ", "ἐ", "θ", "ψ"]],
                ["ἐ", ["ἑ", "ἔ", "ἔ", "έ"]],
                ["ἀ", ["ἁ", "ἅ", "ἂ", "ἄ"]],
                ["ἁ", ["ἀ"]],
                ["ἅ", ["ἄ", "ἂ"]],
                ["ἄ", ["θ", "ἀ", "ἁ"]],
                ["ὰ", ["ἄ", "ἂ", "t", "ἀ", "ᾶ"]],
                ["ά", ["ἀ", "ἄ", "ἁ", "ό"]],
                ["ᾶ", ["ᾷ", "ἆ"]],
                ["ἔ", ["ἕ"]],
                ["ε", ["ὲ", "ἐ", "e", "s"]],
                ["ἐ", ["ἑ"]],
                ["ἑ", ["ἐ"]],
                ["έ", ["ἐ", "ἑ"]],
                ["ἱ", ["ἰ", "ἷ"]],
                ["ἴ", ["ἷ", "ἵ"]],
                ["ἰ", ["ἱ", "ἴ", "ὶ", "ί"]],
                ["ὶ", ["ἱ", "i"]],
                ["ι", ["ἰ", "ἱ", "ὶ", "ί", "i"]],
                ["ἠ", ["ἡ"]],
                ["ἡ", ["ἠ", "ἧ"]],
                ["ῆ", ["ὴ", "ἧ", "ῇ", "ή"]],
                ["ἤ", ["ἥ"]],
                ["ὴ", ["ή"]],
                ["ή", ["ὴ", "ῆ"]],
                ["θ", ["ﬁ"]],
                ["δ", ["θ"]],
                ["ο", ["ὸ", "c", "o", "σ"]],
                ["ὀ", ["ὁ"]],
                ["ὁ", ["ὀ"]],
                ["ό", ["ὁ", "ὀ"]],
                ["ὸ", ["b", "ὁ", "δ"]],
                ["ὅ", ["ὄ"]],
                ["ϲ", ["c"]],
                ["λ", ["ἵ"]],
                ["ῦ", ["ὺ"]],
                ["v", ["v"]],
                ["v", ["ν", "υ"]],
                ["Τ", ["Ἰ", "Ἴ", "T", "Γ", "Υ"]],
                ["Z", ["Ζ"]],
                ["Ἰ", ["Ἴ", "Ἵ", "Ἱ"]],
                ["Ὁ", ["Ὅ"]],
                ["Κ", ["Χ", "K"]],
                ["Λ", ["Α", "Δ", "A"]],
                ["Μ", ["M"]],
                ["Π", ["Β"]],
                ["Χ", ["X"]],
                ["Ὡ", ["Ὠ"]],
                ["ή", ["ἡ"]],
                ["ῇ", ["ᾗ", "ᾖ"]],
                ["ἡ", ["ἥ"]],
                ["ἤ", ["ἥ"]],
                ["ῃ", ["η"]],
                ["η", ["ή", "ῃ"]],
                ["κ", ["x"]],
                ["ὕ", ["ὔ"]],
                ["ὔ", ["ὕ"]],
                ["ρ", ["ῥ", "p"]],
                ["ς", ["s"]],
                ["σ", ["κ"]],
                ["τ", ["r", "x"]],
                ["φ", ["ρ"]],
                ["t", ["λ", "ι", "ῖ", "ἰ", "ἱ", "ί"]],
                ["ύ", ["ὐ", "ὑ", "ό"]],
                ["ὐ", ["ύ", "ὑ"]],
                ["ὑ", ["ὐ"]],
                ["ώ", ["ῴ"]],
                ["ῶ", ["ὧ", "ώ"]],
                ["ὧ", ["ὡ"]],
                ["ὠ", ["ὡ"]],
                ["ὡ", ["ὠ", "ὼ"]],
                ["D", ["Π", "Β", "Ο", "U"]],
                ["B", ["Β"]],
                ["E", ["Ε", "Ἐ", "F"]],
                ["Ε", ["E", "Ἐ", "Ἑ"]],
                ["Ἐ", ["Ἑ", "Ἔ"]],
                ["B", ["H"]],
                ["H", ["Π", "Η", "Ἡ", "Ἡ"]],
                ["I", ["Ι", "J", "l", "Π"]],
                ["J", ["I"]],
                ["K", ["Κ"]],
                ["M", ["Μ"]],
                ["N", ["Ν"]],
                ["O", ["Ο", "0"]],
                ["0", ["O", "Ο"]],
                ["P", ["Ῥ", "Ρ"]],
                [
                    "Ρ",
                    [
                        "Ῥ",
                    ],
                ],
                ["R", ["H"]],
                ["Q", ["O"]],
                ["T", ["Τ", "Γ"]],
                ["X", ["Χ", "T"]],  # now Latin
                ["Z", ["Ζ"]],
                ["a", ["α", "e", "n", "s", "u"]],
                ["b", ["h"]],
                ["æ", ["œ"]],
                ["œ", ["æ"]],
                ["c", ["e", "o", "q", "ϲ"]],
                ["e", ["c", "o", "ε"]],
                ["f", ["i", "l", "ﬀ"]],
                ["g", ["y"]],
                ["ﬀ", ["ﬁ"]],
                ["ﬁ", ["ﬂ"]],
                ["ﬀi", ["fﬁ"]],
                ["h", ["b", "t"]],
                ["i", ["l", "ι", "ἱ", "ἰ"]],
                ["m", ["n"]],
                ["l", ["t", "ﬂ", "i"]],
                ["u", ["n", "o", "ν"]],
                ["n", ["u", "m", "a"]],
                ["o", ["ο", "q", "c"]],
                ["p", ["q", "ρ"]],
                ["q", ["c", "p"]],
                ["r", ["t", "v", "τ"]],
                ["s", ["ς"]],
                ["t", ["i", "r", "l"]],
                ["v", ["y", "r", "u", "æ", "ν"]],
                ["x", ["z"]],
                ["y", ["γ"]],
                ["fi", ["ﬁ"]],
                ["ﬁ", ["f"]],
                ["ae", ["æ"]],
                ["τ", ["ι"]],
                ["s", ["a", "n", "e"]],
                ["1", ["ί"]],
                ["1", ["l", "i", "I"]],
                ["8", ["s"]],
            ]
            for subst in subs:
                for replacement in subst[1]:
                    for instance in findOccurences(w, subst[0]):
                        # sub_attempt = re.sub(subst[0],replacement,w)
                        # sub_attempt = w.replace(subst[0],replacement)
                        # replace this instance with the target character
                        try:
                            sub_attempt = w[:instance] + replacement + w[instance + 1 :]
                        except UnicodeDecodeError as e:
                            print(e, w, replacement)
                        if sub_attempt in my_dict:
                            output = sub_attempt
                            try:
                                operation = "Sub " + subst[0] + "->" + replacement
                            except UnicodeDecodeError as e:
                                print(e, w, replacement)
                            break
                        elif in_dict_lower(my_dict, sub_attempt):
                            output = sub_attempt
                            try:
                                operation = "SubLower " + subst[0] + "->" + replacement
                            except UnicodeDecodeError as e:
                                print(e, w, replacement)
                            break
                        elif inNoAccentDict(sub_attempt, no_accent_dict) and (
                            len(sub_attempt) > 4 or w[0].isupper()
                        ):
                            output = inNoAccentDict(sub_attempt, no_accent_dict)
                            try:
                                operation = "SubNoAcc " + subst[0] + "->" + replacement
                            except UnicodeDecodeError as e:
                                print(e, w, replacement)
                            break
        if operation == "False":
            dup_letters_removed = re.sub(r"(.)\1{1,}", r"\1", w)
            if dup_letters_removed in my_dict:
                operation = "Dedup"
                output = dup_letters_removed
            elif in_dict_lower(my_dict, dup_letters_removed) == True:
                operation = "DedupLower"
                output = dup_letters_removed
            elif inNoAccentDict(dup_letters_removed, no_accent_dict):
                output = inNoAccentDict(dup_letters_removed, no_accent_dict)
                operation = "DedupNoAcc"
        if operation == "False":
            l = len(w)
            half = int(l / 2)
            for pointer in range(1, half - 3):
                if bothHalvesInDict(
                    my_dict, w[: half - pointer + 1], w[half - pointer + 1 :]
                ):
                    operation = "True"
                    output = w[: half - pointer + 1] + " " + w[half - pointer + 1 :]
                    break
                if bothHalvesInDict(my_dict, w[: pointer + half], w[pointer + half :]):
                    output = w[: pointer + half] + " " + w[pointer + half :]
                    operation = "True"
                    break
        output_file_handle.write(
            w
            + marker
            + output
            + marker
            + str(word_count[w])
            + marker
            + operation
            + "\n"
        )
        # print "# ", str(100.0 * count / total), "complete"
        # output_array.append((w,output,word_count[w],operation))
        if operation != "False":
            output_dict[w] = (output, word_count[w], operation)
        ##    if operation == "False":
        ##        try:
        ##            dump(w)
        ##        except:
        ##            print "Error in dump on word", w
        total_count = total_count + int(word_count[w])
        total_biomass = total_biomass + int(word_count[w]) * len(w)
        try:
            counts[operation] = counts[operation] + word_count[w]
            biomass[operation] = biomass[operation] + word_count[w] * len(w)
        except:
            counts[operation] = word_count[w]
            biomass[operation] = word_count[w] * len(w)
    output_file_handle.close()
    if verbose:
        print("Total words:", total_count)
    # print >> sys.stderr, counts
    total_fixed = 0
    total_biomass_fixed = 0
    for out in sorted(counts, key=counts.get, reverse=True):
        if verbose:
            print(out, counts[out], file=sys.stderr)
        if not out == "False":
            total_fixed = total_fixed + counts[out]
            total_biomass_fixed = total_biomass_fixed + biomass[out]
    try:
        if verbose:
            print("Total fixed by spellcheck: ", str(total_fixed))
            print("Percentage good:", str(total_fixed * 100.00 / total_count))
            print(
                "Biomass correct: ", str(total_biomass_fixed * 100.00 / total_biomass)
            )
    except ZeroDivisionError:
        print("Total spellcheck count is ZERO???")
