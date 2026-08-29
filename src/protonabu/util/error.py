""" Module: Error
    - Intent: Field-oriented exception
    - Author: Avner Ben
        - Created: 23-Apr-2024
            - Adapted from legacy teaching example
        - Improved: 28-Aug-2026
            - Moved here Internal Error, Fact File Error, Parsing Error
"""

import re
from pathlib import Path
from typing import Any, Optional

class Error(Exception):
    """ Protonabu Exception
    """

    def __init__(self, 
        # - Input: message
        message: Any, 
        # - Input: fields
        #   - Contains: "Name"
        #   - Contains: "Value"
        fields: Optional[list[tuple[str, Any]]] = None
    ):
        """ to INITIALIZE Protonabu Exception
            - Exported
        """
        # [Esc Done]: Another Error
        if isinstance(message, Error):
            # to copy internals from another Error
            self.origMessage = message.origMessage
            self.message = message.message
            self.fields = list(message.fields)
            # [Opt; Scan]: to copy field to error message
            if fields:
                for field in fields:
                    # [Esc Once]: "Invalid argument"
                    if len(field) != 2 or not field[0]: continue
                    # [Msg]: to set field in error message
                    self.set(*field)
            return
        msg_str = str(message).rstrip()
        # [Opt]: to append exclamation mark to error message
        if not msg_str.endswith(('!', '?', '.')):
            msg_str += '!'
        self.message = msg_str
        # to preserve the original error message
        self.origMessage = msg_str
        self.fields = []
        # [Esc Done]: No fields provided
        if not fields: return
        # [Scan]: to append field to Protonabu Exception
        for field in fields:
            # [Esc Once]: "Invalid argument"
            if len(field) != 2 or not field[0]: continue
            # [Msg]: to set field in error message
            self.set(*field)

    def set(self, key: str, value: Any, overwrite: bool = False):
        """ to set field in error message
            - Exported
            - Input: name
            - Input: value
        """
        # [Scan]: to find existing field
        for i, (k, v) in enumerate(self.fields):
            # [Esc Done]: "Found requested field"
            if k.lower() == key.lower():
                # [Opt Overwrite]: to overwrite Error Message field
                if overwrite:
                    self.fields[i] = (key, value)
                return
        # [Opt]: to set error field value to unknown
        if not value:
            value = '(?)'
        self.fields.append((key, value))
        self.message += f'\n{key}: {str(value)}'

    def get(self, inKey: str) -> Optional[str]:
        """ to get field from error message
            - Exported
            - Input: field name
            - Output: field value
        """
        # [Scan]: to compare field with error message
        for key, value in self.fields:
            # [Esc Done]: "Found requested field"
            if key.lower() == inKey.lower(): return value
        # [Esc Exhausted]: "Not Found"
        return None

    def __iter__(self):
        """ to iterate over error fields
        """
        # to EXTRACT error message from Protonabu Exception
        yield '', self.message
        # to EXTRACT error field from Protonabu Exception
        yield from self.fields

    def __str__(self):
        return self.message

class InternalError(Error):
    """ Internal Protonabu Exception
        - Intent: to prefix error message with INTERNAL
    """
    def __init__(self, message: str, fields: Optional[list[tuple[str, Any]]] = None):
        """ to INITIALIZE internal Protonabu Exception
            - Exported
        """
        # [Msg]: to INITIALIZE Protonabu Exception
        super().__init__(f'INTERNAL: {message}', fields)

class FactFileError(Error):
    """ Fact File Error
    """
    def __init__(self, 
         filename: Any, 
         lineNumber: Any = None, 
         msg: str = '', 
         fields: Optional[list[tuple[str, Any]]] = None
    ):
        """ to INITIALIZE Fact File Error
            - Exported
            - Input: filename or fact object
            - Input: line number or message
            - Input: message
            - Input: fields
        """
        # [Opt]: to handle positional arg polymorphism
        if isinstance(lineNumber, str) and not msg:
            msg = lineNumber
            lineNumber = None
        # [Opt]: to handle fact object
        if not isinstance(filename, (str, Path)):
            obj = filename
            # [Opt]: to get filename from fact object
            filename = getattr(obj, 'fileName', getattr(obj, 'filename', getattr(obj, 'file_name', getattr(obj, 'file', str(obj)))))
            # [Opt]: to get line number from fact object
            if lineNumber is None:
                lineNumber = getattr(obj, 'lineNumber', getattr(obj, 'lineNum', getattr(obj, 'line_number', getattr(obj, 'line', 0))))
        # [Opt]: to set line number to 0
        if lineNumber is None:
            lineNumber = 0
        # [Msg]: to INITIALIZE Protonabu Exception
        super().__init__(msg, fields)
        # [to format file and line number
        file_str = f'{filename}:{lineNumber}' if lineNumber else str(filename)
        # to set file and line number
        self.set('file', file_str, overwrite=True)

class ParsingError(Error):
    """ Parsing Error
        - Intent: Parser-oriented syntax exception
    """
    def __init__(self, 
        message: Any, 
        where: Optional[str] = None,
        fields: Optional[list[tuple[str, Any]]] = None
    ):
        """ to INITIALIZE Parsing Error
            - Exported
            - Input: message or ParseException
            - Input [Opt]: where
            - Input [Opt]: fields
        """
        # [Opt]: to format message from ParseException
        if hasattr(message, 'column') or hasattr(message, 'loc') or 'ParseException' in type(message).__name__:
            raw_msg = str(message)
            msg = 'Excess information in line' if raw_msg.startswith('Expected end of text') else 'Invalid syntax'
            matched = re.search(r'column:(\d+)', raw_msg)
            # [Opt]: to append column location
            if matched:
                msg += f' (at column {matched.group(1)}'
                # [Opt]: to append location name
                if where:
                    msg += f' in {where}'
                msg += ')'
            elif where:
                msg += f' in {where}'
        elif isinstance(message, str):
            msg = message
            # [Opt]: to append location name
            if where:
                msg += f' in {where}'
        else:
            msg = str(message)
        # [Msg]: to INITIALIZE Protonabu Exception
        super().__init__(msg, fields)
