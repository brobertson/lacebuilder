#!/usr/bin/python
# coding: utf-8
import lxml
from lxml import etree
import sys
import re
from .greek_tools import preprocess_word, dump, split_text_token
import codecs
import os

if __name__ == "__main__":
    spellcheck(sys.argv[1], sys.argv[2], sys.argv[3], True)

def spellcheck(spellcheck_file_path, dir_in_path, dir_out_path, verbose): 
    import unicodedata
    spellcheck_dict = {}
    euro_sign = str("\N{EURO SIGN}")
    if not os.path.isdir(dir_in_path) or not os.path.isdir(dir_out_path):
        print("one of the paths is not legit. Exiting ...")
        exit()
    with codecs.open(spellcheck_file_path, "r", "utf-8") as spellcheck_file:
        for line in spellcheck_file:
            line = line.strip()
            # print line
            # omit comment lines from processing
            if not (line[0] == "#"):
                try:
                    [original_form, replacement, frequency, spellcheck_mode] = line.split(
                        euro_sign
                    )
                    # print original_form, replacement, spellcheck_mode
                    if spellcheck_mode != "False":
                        spellcheck_dict[unicodedata.normalize("NFC", original_form)] = (
                            unicodedata.normalize("NFC", replacement),
                            frequency,
                            spellcheck_mode,
                        )
                except ValueError:
                    print(
                        "line '", line, "' could not be processed, skipping and continuing"
                    )
                    continue
    if (verbose):
        print("dictionary length: ", len(spellcheck_dict))
        print("reading dir ", dir_in_path)



    for file_name in os.listdir(dir_in_path):
        if file_name.endswith(".html"):
            simplified_name = file_name
            if file_name.startswith("output-"):
                simplified_name = file_name[7:]
            fileIn_name = os.path.join(dir_in_path, file_name)
            fileOut_name = os.path.join(dir_out_path, simplified_name)
            fileIn = codecs.open(fileIn_name, "r", "utf-8")
            if (verbose):
                print("checking", fileIn_name, "sending to ", fileOut_name)
            try:
                treeIn = etree.parse(fileIn)
                root = treeIn.getroot()
                htmlHead = treeIn.xpath(
                    "/html:html/html:head",
                    namespaces={"html": "http://www.w3.org/1999/xhtml"},
                )

                hocr_word_elements = treeIn.xpath(
                    "//html:span[@class='ocr_word'] | //span[@class='ocr_word']",
                    namespaces={"html": "http://www.w3.org/1999/xhtml"},
                )
                filtered_hocr_word_elements = list(
                    {x for x in hocr_word_elements if x.text != None}
                )
                for word_element in filtered_hocr_word_elements:
                    dhf = word_element.get("data-dehyphenatedform")
                    if (verbose):
                        print("dehyph form", dhf)
                    hyphenated_form = False
                    if dhf == None:
                        try:
                            word = unicodedata.normalize("NFC", word_element.text)
                        except TypeError:
                            word = unicodedata.normalize("NFC", str(word_element.text))

                    elif dhf == "":
                        # It is the tail of a dehyphenated form
                        continue
                    else:
                        try:
                            word = unicodedata.normalize("NFC", dhf)
                        except TypeError:
                            word = unicodedata.normalize("NFC", str(dhf))
                        if (verbose):
                            print("a hyhpenated word:", word)
                        hyphenated_form = True
                    try:
                        if (verbose):
                            print("Word:", word)
                        parts = split_text_token(word)
                        if (verbose):
                            print("Parts:", parts)
                        error_word = preprocess_word(parts[1])
                        if (verbose):
                            print("an error word:", error_word)
                        (replacement, frequency, spellcheck_mode) = spellcheck_dict[
                            error_word
                        ]
                        if spellcheck_mode == "True" or spellcheck_mode == "TrueLower":
                            replacement = parts[1]
                        # if there is no entry, then we will throw a Key Error and not do any of this:
                        if (verbose):
                            print(replacement, frequency, spellcheck_mode)
                        parts = (parts[0], replacement, parts[2])
                        if (verbose):
                            print("replaced", error_word, "with", replacement)
                        # dump(parts[1])
                        output = parts[0] + parts[1] + parts[2]
                        if hyphenated_form:
                            hyphen_position = (
                                int(word_element.get("data-hyphenposition")) - 1
                            )
                            end_no = word_element.get("data-hyphenendpair")
                            hyphen_end_element = treeIn.xpath(
                                "//html:span[@data-hyphenstartpair='"
                                + end_no
                                + "'] | //span[@data-hyphenstartpair='"
                                + end_no
                                + "']",
                                namespaces={"html": "http://www.w3.org/1999/xhtml"},
                            )
                            # hyphen_end_element = treeIn.get_element_by_id(word_element.get("hyphenEndId"))
                            word_element.set("data-dehyphenatedform", output)
                            word_element.text = output[0:hyphen_position] + "-"
                            if len(hyphen_end_element) == 1:
                                hyphen_end_element[0].text = output[hyphen_position:]
                                hyphen_end_element[0].set(
                                    "data-spellcheck-mode", spellcheck_mode
                                )
                            else:
                                print(
                                    "there are too many hyphen end elements ",
                                    end_id,
                                    "has",
                                    len(hyphen_end_element),
                                    "exiting..."
                                )
                                exit()
                        elif spellcheck_mode == "PunctStrip":
                            # if the mode is PunctStrip, then provide the original, since it might contain inner brackets, etc.
                            # Note, however, that we keep the dictionary form
                            word_element.set("data-spellchecked-form", replacement)
                        else:
                            word_element.text = output
                        word_element.set("data-spellcheck-mode", spellcheck_mode)
                        if word != output:
                            word_element.set("data-pre-spellcheck", word)
                    except KeyError:
                        if (verbose):
                            print("oops had a key error")
                        if error_word == "":
                            word_element.set("data-spellcheck-mode", "Numerical")
                        else:
                            word_element.set("data-spellcheck-mode", "None")
                    word_element.set("data-selected-form", word_element.text)
                    word_element.set("data-manually-confirmed", "false")
                    treeIn.write(fileOut_name, encoding="UTF-8", xml_declaration=True)
            except Exception  as e:
                print("failed to parse due to:", e)
