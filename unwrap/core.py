# -*- coding: utf-8 -*-
"""
Core classes.
"""
from __future__ import absolute_import, print_function, unicode_literals, division

import math


class Metric(object):
    """Metrics about a collection of values.

    Attributes:
        count: number of values used to compute the metrics.
        sum: sum of all values.
        avg: average of all values.
        dev: standard deviation of all values.
    """

    def __init__(self):
        self.count = 0
        self.sum = 0
        self._values = []

    def add(self, value):
        """Add a new value to the collection."""
        self.sum += value
        self.count += 1
        self._values.append(value)
        return self

    @property
    def avg(self):
        return self.sum / self.count if self.count else 0

    @property
    def dev(self):
        mean = self.avg
        return math.sqrt(sum((value - mean) ** 2 for value in self._values))


class Paragraph(object):
    """A single paragraph.

    Attributes:
        empty: if this paragraph has no text.
        text: paragraph's text.
        uncertain: indicates if paragraph's end boundary is uncertain.
    """

    def __init__(self):
        self._text = ""
        self.uncertain = False

    @property
    def empty(self):
        return not self._text

    @property
    def text(self):
        return self._text

    def add(self, line):
        """Add a new piece of text to the paragraph.

        The text will be added to the paragraph maintaining a single space
        separation from the current paragraph's content, unless the current
        content ends with an hyphen.

        Args:
            line: a piece of text (usually a line) to add to the paragraph.
        """
        separator = " "
        if self.empty:
            separator = ""
        elif self._text.endswith("-"): # TODO Check Unicode hyphen characters.
            separator = ""
            # TODO Try to handle cases where the hyphen was used to break long
            # words at end of lines. If the hyphen should be omitted, it may be
            # useful to replace it by a soft hyphen.
        self._text += separator + line
        return self


class Joiner(object):
    # TODO Support other Unicode characters.
    END_MARKS = [
        ".", "?", "!",
    ]
    POSSIBLE_END_MARKS = [
        "...", ":",
        ".\"", ".'", "?\"", "?'", "!\"", "!'",
        ")", "]", "}",
    ]

    NOT_LAST = 0
    MAYBE_LAST = 1
    LAST = 2

    def __init__(self, lines):
        self.lines = lines
        self._first = Metric()
        self._middle = Metric()

    def iterate(self, count=1):
        """Run one or more algorithm iterations to refine metrics."""
        for _ in range(count):
            for _ in self:
                pass

    def __iter__(self):
        """Iterate over the paragraphs."""
        if not self.lines:
            return

        paragraph = Paragraph()
        iterator = iter(self.lines)
        line = next(iterator).strip()
        while line is not None:
            # Peek next line
            try:
                next_line = next(iterator).strip()
            except StopIteration:
                next_line = None

            # Check for blank lines. Any blank line will indicate the end of a
            # paragraph. The blank line itself is also emitted.
            if not line:
                if paragraph.empty:
                    yield paragraph
                    paragraph = Paragraph()
                yield Paragraph()
            else:
                # If the paragraph is still empty, then this line is its first.
                is_first = paragraph.empty

                paragraph.add(line)

                # Check if it's the last line
                is_last, certain = self._is_last(line, next_line, is_first)
                if is_last:
                    paragraph.uncertain = not certain
                    yield paragraph
                    paragraph = Paragraph()
                else:
                    if is_first:
                        self._first.add(len(line))
                    else:
                        self._middle.add(len(line))

            line = next_line

    def _is_last(self, line, next_line, is_first):
        """Finds out if line is the last line of a paragraph or not.

        Args:
            line: the line to find if its the last.
            next_line: the following line.
            is_first: if line is the paragraph's first line.

        Returns:
            (bool, bool) If the line is the last, and if we are certain.
        """
        if not next_line:
            return True, True

        # Check metrics
        first = self._first.avg
        middle = self._middle.avg
        last_threshold = first - (middle - first)
        if middle - first > 2 * max(self._first.dev, self._middle.dev):
            # First-line metrics is useful, check if this next line can be a
            # first line.
            middle_threshold = (middle + first) / 2
            if len(next_line) > middle_threshold:
                # Next line is too long to be a first line.
                return False, True

            # Next line is not that long - it might be the last or a single-line
            # paragraph. Check punctuation between these lines.
            for mark in self.END_MARKS:
                if line.endswith(mark):
                    threshold = last_threshold if is_first else middle_threshold
                    return True, len(line) < threshold

            for mark in self.POSSIBLE_END_MARKS:
                if line.endswith(mark):
                    return True, len(line) < last_threshold
        else:
            # First-line metrics aren't useful, just check punctuation.
            for mark in self.END_MARKS + self.POSSIBLE_END_MARKS:
                if line.endswith(mark):
                    return True, len(line) < last_threshold

        return False, True

    @property
    def stats(self):
        return {
            "first avg": self._first.avg,
            "first dev": self._first.dev,
            "middle avg": self._middle.avg,
            "middle dev": self._middle.dev,
        }
