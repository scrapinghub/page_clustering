import scrapely.htmlpage as hp
import numpy as np


def is_tag(fragment):
    """Check if a fragment is also an HTML tag"""
    return isinstance(fragment, hp.HtmlTag)


def is_closing(fragment):
    return fragment.tag_type == hp.HtmlTagType.CLOSE_TAG


def is_non_closing_tag(fragment):
    return is_tag(fragment) and not is_closing(fragment)


def get_class(fragment):
    """Return a set with class attributes for a given fragment"""
    if is_tag(fragment):
        return frozenset((fragment.attributes.get('class') or '').split())
    else:
        return frozenset()


def tag_to_token(fragment):
    return (fragment.tag, get_class(fragment))


class TagFrequency(object):
    def __init__(self):
        self.dictionary = {}
        self.dimension = 0

    def __call__(self, page):
        to_index = []
        for fragment in filter(is_non_closing_tag, page.parsed_body):
            token = tag_to_token(fragment)
            index = self.dictionary.get(token)
            if index is not None:
                to_index.append(index)
            else:
                to_index.append(self.dimension)
                self.dictionary[token] = self.dimension
                self.dimension += 1
        vector = np.zeros((len(self.dictionary),))
        for index in to_index:
            vector[index] += 1
        return np.array(vector)
