#!/usr/bin/env python

# Copyright 2011 Jante LLC and University of Kansas
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = "Aaron Steele, Dave Vieglais, and John Wieczorek"

"""This module supports converting a Darwin Core Archive into a single CSV file.

The Darwin Core Archive format is specified here:
http://rs.tdwg.org/dwc/terms/guides/text/index.htm

Only the data contained within the <core> element are converted to a CSV file. 
All <extension> elements are currently ignored.

"""
import csv
import logging
from optparse import OptionParser
from urlparse import urlparse
from xml.dom.minidom import parse, parseString

class FieldType(object):
    """Represents a <field> element in a Darwin Core Archive metafile.

    The <field> element is a complexType named fieldType and it is defined here:
    http://rs.tdwg.org/dwc/text/tdwg_dwc_text.xsd

    All attributes are read-only. The vocabulary attribute is ignored. Instances
    of FieldType are comparable by their index value.

    Attributes:
        term: A required string that defines the field term.
        index: An optional integer that defines the field index.
        default: An optional string that defines the field default value.
    """

    def __init__(self, term, index=None, default=None):
        """Constructs a new FieldType instance.

        Args:
            term: A required string that defines the field term.
            index: An optional integer that defines the field index.
            default: An optional string that defines the field default value.
        """
        term = urlparse(term).path
        self._term = term.split('/')[-1]
        if index == '' or index is None:
            self._index = None
        else:
            self._index = int(index)
        self._default = default

    def __cmp__(self, other):
        """Compares the index of this FieldType to another FieldType."""
        if self.index > other.index:
            return 1
        elif self.index < other.index:
            return -1
        else:
            return 0

    def __str__(self):
        """Returns the attributes of this FieldType as a dictionary string."""
        return str(self.__dict__)

    # Defines read-only properties for term, index, and default attributes:
    def get_term(self):
        return self._term
    term = property(get_term)
    def get_index(self):
        return self._index
    index = property(get_index)
    def get_default(self):
        return self._default
    default = property(get_default)

class CoreFileType(object):
    """Represents a <core> element in a Darwin Core Archive metafile.

    The <core> element is a complexType named coreFileType and it is defined here:
    http://rs.tdwg.org/dwc/text/tdwg_dwc_text.xsd

    All attributes are read-only. 

    Attributes:
        rowType: A string that defines the row type.
        fieldsTerminatedBy: A string that defines the field separator.
        linesTerminatedBy: A string that defines the new line character.
        fieldsEnclosedBy: A string that defines the character enclosing fields.
        encoding: A string that defines the character encoding.
        ignoreHeaderLines: An integer specifying how many lines to skip.
        dateFormat: A string the defines the date format.
        locations: A list of strings that define file locations.
        fields: A list of FieldType objects with index values.
        defaults: A list of FieldType objects without index values.
    """
    
    def __init__(self, metafile):
        """Constructs a new CoreFileType instance.

        Args:
            metafile: A string that contains the contents of a metafile.
        """
        dom = parseString(metafile)
        core = dom.getElementsByTagName('core')[0]
        
        # Extracts core attributes:
        self._rowType = core.getAttribute('rowType')
        self._fieldsTerminatedBy = core.getAttribute('fieldsTerminatedBy') or ','
        self._linesTerminatedBy = core.getAttribute('linesTerminatedBy') or '\n'
        self._fieldsEnclosedBy = core.getAttribute('fieldsEnclosedBy') or '"'
        self._encoding = core.getAttribute('encoding')
        self._ignoreHeaderLines = int(core.getAttribute('ignoreHeaderLines'))
        self._dateFormat = core.getAttribute('dateFormat')

        # Extracts core file locations:
        locations = core.getElementsByTagName('location')
        self._locations = [x.childNodes[0].data for x in locations]

        # Extracts and sorts core fields with index values:
        fields = [FieldType(x.getAttribute('term') or None, 
                            index=x.getAttribute('index') or None, 
                            default=x.getAttribute('default') or None)
                  for x in core.getElementsByTagName('field')]
        self._fields = [x for x in fields if x.index is not None]
        self._fields.sort()

        # Extracts and sorts core fields without index values:
        self._defaults = [x for x in fields if x.index is None]
        self._defaults.sort()
    
    def __str__(self):
        return str(self.__dict__)
    
    # Creates read-only properties for all class attributes:
    def get_defaults(self):
        return self._defaults
    defaults = property(get_defaults)
    def get_fields(self):
        return self._fields
    fields = property(get_fields)
    def get_locations(self):
        return self._locations
    locations = property(get_locations)
    def get_dateFormat(self):
        return self._dateFormat
    dateFormat = property(get_dateFormat)
    def get_encoding(self):
        return self._encoding
    encoding = property(get_encoding)
    def get_fieldsEnclosedBy(self):
        return self._fieldsEnclosedBy
    fieldsEnclosedBy = property(get_fieldsEnclosedBy)
    def get_fieldsTerminatedBy(self):
        return self._fieldsTerminatedBy
    fieldsTerminatedBy = property(get_fieldsTerminatedBy)
    def get_ignoreHeaderLines(self):
        return self._ignoreHeaderLines
    ignoreHeaderLines = property(get_ignoreHeaderLines)
    def get_linesTerminatedBy(self):
        return self._linesTerminatedBy
    linesTerminatedBy = property(get_linesTerminatedBy)
    def get_rowType(self):
        return self._rowType
    rowType = property(get_rowType)

def writecsv(metafile, destination):
    """Writes a single CSV file from data defined by a Darwin Core Archive metafile.
    
    Args:
        metafile: A string path to a Darwin Core Archive metafile.
        destination: A string path to where CSV results will be written.
    """
    core = CoreFileType(open(metafile, 'r').read())

    # Builds the CSV header fieldnames:
    field_terms = [x.term for x in core.fields]
    default_field_terms = [x.term for x in core.defaults]
    fieldnames = field_terms + default_field_terms

    # Creates the CSV writer and writes the header row:
    dw = csv.DictWriter(open(destination, 'w'), fieldnames, quoting=csv.QUOTE_ALL)
    dw.writerow(dict((x, x) for x in fieldnames)) 

    # Formatting params for input CSV files:
    delimiter = core.fieldsTerminatedBy
    lineterminator = core.linesTerminatedBy
    quotechar = core.fieldsEnclosedBy
    
    # Writes CSV data for each input CSV file:
    for location in core.locations:
        f = open(location, 'r')
        dr = csv.DictReader(f, 
                            fieldnames, 
                            delimiter=delimiter, 
                            lineterminator=lineterminator, 
                            quotechar=quotechar,
                            skipinitialspace=True)

        # Skips over nodata lines:
        for x in range(0, core.ignoreHeaderLines):
            dr.next()

        for row in dr:

            # Adds the default values for any default terms:
            for d in core.defaults:
                row[d.term] = d.default

            # Writes the row:
            dw.writerow(row)
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)    
    
    # Parses command line parameters:
    parser = OptionParser()
    parser.add_option("-m", "--metafile", dest="metafile",
                      help="The Darwin Core Archive metafile",
                      default=None)
    parser.add_option("-d", "--destination", dest="destination",
                      help="The destination CSV file",
                      default=None)
    (options, args) = parser.parse_args()
    metafile = options.metafile
    destination = options.destination
    logging.info('Metafile: %s\nDestination: %s' % (metafile, destination))
    
    # Writes the CSV file:
    writecsv(metafile, destination)

    logging.info('Darwin Core Archive successfully converted.')

