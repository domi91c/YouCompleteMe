# Copyright (C) 2015 YouCompleteMe contributors
#
# This file is part of YouCompleteMe.
#
# YouCompleteMe is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# YouCompleteMe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with YouCompleteMe.  If not, see <http://www.gnu.org/licenses/>.

from ycm.test_utils import MockVimModule, MockVimCommand
MockVimModule()

from ycm import vimsupport
from nose.tools import eq_
from hamcrest import assert_that, calling, raises, none
from mock import MagicMock, call, patch
import os
import json


def ReplaceChunk_SingleLine_Repl_1_test():
  # Replace with longer range
  #                  12345678901234567
  result_buffer = [ "This is a string" ]
  start, end = _BuildLocations( 1, 1, 1, 5 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start,
                                                          end,
                                                          'How long',
                                                          0,
                                                          0,
                                                          result_buffer )

  eq_( [ "How long is a string" ], result_buffer )
  eq_( line_offset, 0 )
  eq_( char_offset, 4 )

  # and replace again, using delta
  start, end = _BuildLocations( 1, 10, 1, 11 )
  ( new_line_offset, new_char_offset ) = vimsupport.ReplaceChunk(
                                                          start,
                                                          end,
                                                          ' piece of ',
                                                          line_offset,
                                                          char_offset,
                                                          result_buffer )

  line_offset += new_line_offset
  char_offset += new_char_offset

  eq_( [ 'How long is a piece of string' ], result_buffer )
  eq_( new_line_offset, 0 )
  eq_( new_char_offset, 9 )
  eq_( line_offset, 0 )
  eq_( char_offset, 13 )

  # and once more, for luck
  start, end = _BuildLocations( 1, 11, 1, 17 )

  ( new_line_offset, new_char_offset ) = vimsupport.ReplaceChunk(
                                                          start,
                                                          end,
                                                          'pie',
                                                          line_offset,
                                                          char_offset,
                                                          result_buffer )

  line_offset += new_line_offset
  char_offset += new_char_offset

  eq_( ['How long is a piece of pie' ], result_buffer )
  eq_( new_line_offset, 0 )
  eq_( new_char_offset, -3 )
  eq_( line_offset, 0 )
  eq_( char_offset, 10 )


def ReplaceChunk_SingleLine_Repl_2_test():
  # Replace with shorter range
  #                  12345678901234567
  result_buffer = [ "This is a string" ]
  start, end = _BuildLocations( 1, 11, 1, 17 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start,
                                                          end,
                                                          'test',
                                                          0,
                                                          0,
                                                          result_buffer )

  eq_( [ "This is a test" ], result_buffer )
  eq_( line_offset, 0 )
  eq_( char_offset, -2 )


def ReplaceChunk_SingleLine_Repl_3_test():
  # Replace with equal range
  #                  12345678901234567
  result_buffer = [ "This is a string" ]
  start, end = _BuildLocations( 1, 6, 1, 8 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start,
                                                          end,
                                                          'be',
                                                          0,
                                                          0,
                                                          result_buffer )

  eq_( [ "This be a string" ], result_buffer )
  eq_( line_offset, 0 )
  eq_( char_offset, 0 )


def ReplaceChunk_SingleLine_Add_1_test():
  # Insert at start
  result_buffer = [ "is a string" ]
  start, end = _BuildLocations( 1, 1, 1, 1 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start,
                                                          end,
                                                          'This ',
                                                          0,
                                                          0,
                                                          result_buffer )

  eq_( [ "This is a string" ], result_buffer )
  eq_( line_offset, 0 )
  eq_( char_offset, 5 )


def ReplaceChunk_SingleLine_Add_2_test():
  # Insert at end
  result_buffer = [ "This is a " ]
  start, end = _BuildLocations( 1, 11, 1, 11 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start,
                                                          end,
                                                          'string',
                                                          0,
                                                          0,
                                                          result_buffer )

  eq_( [ "This is a string" ], result_buffer )
  eq_( line_offset, 0 )
  eq_( char_offset, 6 )


def ReplaceChunk_SingleLine_Add_3_test():
  # Insert in the middle
  result_buffer = [ "This is a string" ]
  start, end = _BuildLocations( 1, 8, 1, 8 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start,
                                                          end,
                                                          ' not',
                                                          0,
                                                          0,
                                                          result_buffer )

  eq_( [ "This is not a string" ], result_buffer )
  eq_( line_offset, 0 )
  eq_( char_offset, 4 )


def ReplaceChunk_SingleLine_Del_1_test():
  # Delete from start
  result_buffer = [ "This is a string" ]
  start, end = _BuildLocations( 1, 1, 1, 6 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start,
                                                          end,
                                                          '',
                                                          0,
                                                          0,
                                                          result_buffer )

  eq_( [ "is a string" ], result_buffer )
  eq_( line_offset, 0 )
  eq_( char_offset, -5 )


def ReplaceChunk_SingleLine_Del_2_test():
  # Delete from end
  result_buffer = [ "This is a string" ]
  start, end = _BuildLocations( 1, 10, 1, 18 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start,
                                                          end,
                                                          '',
                                                          0,
                                                          0,
                                                          result_buffer )

  eq_( [ "This is a" ], result_buffer )
  eq_( line_offset, 0 )
  eq_( char_offset, -8 )


def ReplaceChunk_SingleLine_Del_3_test():
  # Delete from middle
  result_buffer = [ "This is not a string" ]
  start, end = _BuildLocations( 1, 9, 1, 13 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start,
                                                          end,
                                                          '',
                                                          0,
                                                          0,
                                                          result_buffer )

  eq_( [ "This is a string" ], result_buffer )
  eq_( line_offset, 0 )
  eq_( char_offset, -4 )


def ReplaceChunk_RemoveSingleLine_test():
  result_buffer = [ "aAa", "aBa", "aCa" ]
  start, end = _BuildLocations( 2, 1, 3, 1 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start, end, '',
                                                          0, 0, result_buffer )
  expected_buffer = [ "aAa", "aCa" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, -1 )
  eq_( char_offset, 0 )


def ReplaceChunk_SingleToMultipleLines_test():
  result_buffer = [ "aAa",
                    "aBa",
                    "aCa" ]
  start, end = _BuildLocations( 2, 2, 2, 2 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start, end, 'Eb\nbF',
                                                          0, 0, result_buffer )
  expected_buffer = [ "aAa",
                      "aEb",
                      "bFBa",
                      "aCa" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, 1 )
  eq_( char_offset, 1 )

  # now make another change to the "2nd" line
  start, end = _BuildLocations( 2, 3, 2, 4 )
  ( new_line_offset, new_char_offset ) = vimsupport.ReplaceChunk(
                                                           start,
                                                           end,
                                                           'cccc',
                                                           line_offset,
                                                           char_offset,
                                                           result_buffer )

  line_offset += new_line_offset
  char_offset += new_char_offset

  eq_( [ "aAa", "aEb", "bFBcccc", "aCa" ], result_buffer )
  eq_( line_offset, 1 )
  eq_( char_offset, 4 )


def ReplaceChunk_SingleToMultipleLines2_test():
  result_buffer = [ "aAa", "aBa", "aCa" ]
  start, end = _BuildLocations( 2, 2, 2, 2 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start,
                                                          end,
                                                          'Eb\nbFb\nG',
                                                          0,
                                                          0,
                                                          result_buffer )
  expected_buffer = [ "aAa", "aEb", "bFb", "GBa", "aCa" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, 2 )
  eq_( char_offset, 0 )


def ReplaceChunk_SingleToMultipleLines3_test():
  result_buffer = [ "aAa", "aBa", "aCa" ]
  start, end = _BuildLocations( 2, 2, 2, 2 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start,
                                                          end,
                                                          'Eb\nbFb\nbGb',
                                                          0,
                                                          0,
                                                          result_buffer )
  expected_buffer = [ "aAa", "aEb", "bFb", "bGbBa", "aCa" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, 2 )
  eq_( char_offset, 2 )


def ReplaceChunk_SingleToMultipleLinesReplace_test():
  result_buffer = [ "aAa", "aBa", "aCa" ]
  start, end = _BuildLocations( 1, 2, 1, 4 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start,
                                                          end,
                                                          'Eb\nbFb\nbGb',
                                                          0,
                                                          0,
                                                          result_buffer )
  expected_buffer = [ "aEb", "bFb", "bGb", "aBa", "aCa" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, 2 )
  eq_( char_offset, 0 )


def ReplaceChunk_SingleToMultipleLinesReplace_2_test():
  result_buffer = [ "aAa",
                    "aBa",
                    "aCa" ]
  start, end = _BuildLocations( 1, 2, 1, 4 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start,
                                                          end,
                                                          'Eb\nbFb\nbGb',
                                                          0,
                                                          0,
                                                          result_buffer )
  expected_buffer = [ "aEb",
                      "bFb",
                      "bGb",
                      "aBa",
                      "aCa" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, 2 )
  eq_( char_offset, 0 )

  # now do a subsequent change (insert at end of line "1")
  start, end = _BuildLocations( 1, 4, 1, 4 )
  ( new_line_offset, new_char_offset ) = vimsupport.ReplaceChunk(
                                                          start,
                                                          end,
                                                          'cccc',
                                                          line_offset,
                                                          char_offset,
                                                          result_buffer )

  line_offset += new_line_offset
  char_offset += new_char_offset

  eq_( [ "aEb",
         "bFb",
         "bGbcccc",
         "aBa",
         "aCa" ], result_buffer )

  eq_( line_offset, 2 )
  eq_( char_offset, 4 )


def ReplaceChunk_MultipleLinesToSingleLine_test():
  result_buffer = [ "aAa", "aBa", "aCaaaa" ]
  start, end = _BuildLocations( 2, 2, 3, 2 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start, end, 'E',
                                                          0, 0, result_buffer )
  expected_buffer = [ "aAa", "aECaaaa" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, -1 )
  eq_( char_offset, 1 )

  # make another modification applying offsets
  start, end = _BuildLocations( 3, 3, 3, 4 )
  ( new_line_offset, new_char_offset ) = vimsupport.ReplaceChunk(
                                                          start,
                                                          end,
                                                          'cccc',
                                                          line_offset,
                                                          char_offset,
                                                          result_buffer )

  line_offset += new_line_offset
  char_offset += new_char_offset

  eq_( [ "aAa", "aECccccaaa" ], result_buffer )
  eq_( line_offset, -1 )
  eq_( char_offset, 4 )

  # and another, for luck
  start, end = _BuildLocations( 3, 4, 3, 5 )
  ( new_line_offset, new_char_offset ) = vimsupport.ReplaceChunk(
                                                          start,
                                                          end,
                                                          'dd\ndd',
                                                          line_offset,
                                                          char_offset,
                                                          result_buffer )

  line_offset += new_line_offset
  char_offset += new_char_offset

  eq_( [ "aAa", "aECccccdd", "ddaa" ], result_buffer )
  eq_( line_offset, 0 )
  eq_( char_offset, -2 )


def ReplaceChunk_MultipleLinesToSameMultipleLines_test():
  result_buffer = [ "aAa", "aBa", "aCa", "aDe" ]
  start, end = _BuildLocations( 2, 2, 3, 2 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start, end, 'Eb\nbF',
                                                          0, 0, result_buffer )
  expected_buffer = [ "aAa", "aEb", "bFCa", "aDe" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, 0 )
  eq_( char_offset, 1 )


def ReplaceChunk_MultipleLinesToMoreMultipleLines_test():
  result_buffer = [ "aAa", "aBa", "aCa", "aDe" ]
  start, end = _BuildLocations( 2, 2, 3, 2 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start,
                                                          end,
                                                          'Eb\nbFb\nbG',
                                                          0,
                                                          0,
                                                          result_buffer )
  expected_buffer = [ "aAa", "aEb", "bFb", "bGCa", "aDe" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, 1 )
  eq_( char_offset, 1 )


def ReplaceChunk_MultipleLinesToLessMultipleLines_test():
  result_buffer = [ "aAa", "aBa", "aCa", "aDe" ]
  start, end = _BuildLocations( 1, 2, 3, 2 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start, end, 'Eb\nbF',
                                                          0, 0, result_buffer )
  expected_buffer = [ "aEb", "bFCa", "aDe" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, -1 )
  eq_( char_offset, 1 )


def ReplaceChunk_MultipleLinesToEvenLessMultipleLines_test():
  result_buffer = [ "aAa", "aBa", "aCa", "aDe" ]
  start, end = _BuildLocations( 1, 2, 4, 2 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start, end, 'Eb\nbF',
                                                          0, 0, result_buffer )
  expected_buffer = [ "aEb", "bFDe" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, -2 )
  eq_( char_offset, 1 )


def ReplaceChunk_SpanBufferEdge_test():
  result_buffer = [ "aAa", "aBa", "aCa" ]
  start, end = _BuildLocations( 1, 1, 1, 3 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start, end, 'bDb',
                                                          0, 0, result_buffer )
  expected_buffer = [ "bDba", "aBa", "aCa" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, 0 )
  eq_( char_offset, 1 )


def ReplaceChunk_DeleteTextInLine_test():
  result_buffer = [ "aAa", "aBa", "aCa" ]
  start, end = _BuildLocations( 2, 2, 2, 3 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start, end, '',
                                                          0, 0, result_buffer )
  expected_buffer = [ "aAa", "aa", "aCa" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, 0 )
  eq_( char_offset, -1 )


def ReplaceChunk_AddTextInLine_test():
  result_buffer = [ "aAa", "aBa", "aCa" ]
  start, end = _BuildLocations( 2, 2, 2, 2 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start, end, 'bDb',
                                                          0, 0, result_buffer )
  expected_buffer = [ "aAa", "abDbBa", "aCa" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, 0 )
  eq_( char_offset, 3 )


def ReplaceChunk_ReplaceTextInLine_test():
  result_buffer = [ "aAa", "aBa", "aCa" ]
  start, end = _BuildLocations( 2, 2, 2, 3 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start, end, 'bDb',
                                                          0, 0, result_buffer )
  expected_buffer = [ "aAa", "abDba", "aCa" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, 0 )
  eq_( char_offset, 2 )


def ReplaceChunk_SingleLineOffsetWorks_test():
  result_buffer = [ "aAa", "aBa", "aCa" ]
  start, end = _BuildLocations( 1, 1, 1, 2 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start, end, 'bDb',
                                                          1, 1, result_buffer )
  expected_buffer = [ "aAa", "abDba", "aCa" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, 0 )
  eq_( char_offset, 2 )


def ReplaceChunk_SingleLineToMultipleLinesOffsetWorks_test():
  result_buffer = [ "aAa", "aBa", "aCa" ]
  start, end = _BuildLocations( 1, 1, 1, 2 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start, end, 'Db\nE',
                                                          1, 1, result_buffer )
  expected_buffer = [ "aAa", "aDb", "Ea", "aCa" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, 1 )
  eq_( char_offset, -1 )


def ReplaceChunk_MultipleLinesToSingleLineOffsetWorks_test():
  result_buffer = [ "aAa", "aBa", "aCa" ]
  start, end = _BuildLocations( 1, 1, 2, 2 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start, end, 'bDb',
                                                          1, 1, result_buffer )
  expected_buffer = [ "aAa", "abDbCa" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, -1 )
  eq_( char_offset, 3 )


def ReplaceChunk_MultipleLineOffsetWorks_test():
  result_buffer = [ "aAa", "aBa", "aCa" ]
  start, end = _BuildLocations( 3, 1, 4, 3 )
  ( line_offset, char_offset ) = vimsupport.ReplaceChunk( start,
                                                          end,
                                                          'bDb\nbEb\nbFb',
                                                          -1,
                                                          1,
                                                          result_buffer )
  expected_buffer = [ "aAa", "abDb", "bEb", "bFba" ]
  eq_( expected_buffer, result_buffer )
  eq_( line_offset, 1 )
  eq_( char_offset, 1 )


def _BuildLocations( start_line, start_column, end_line, end_column ):
  return {
    'line_num'  : start_line,
    'column_num': start_column,
  }, {
    'line_num'  : end_line,
    'column_num': end_column,
  }


def ReplaceChunksInBuffer_SortedChunks_test():
  chunks = [
    _BuildChunk( 1, 4, 1, 4, '('),
    _BuildChunk( 1, 11, 1, 11, ')' )
  ]

  result_buffer = [ "CT<10 >> 2> ct" ]
  vimsupport.ReplaceChunksInBuffer( chunks, result_buffer, None )

  expected_buffer = [ "CT<(10 >> 2)> ct" ]
  eq_( expected_buffer, result_buffer )


def ReplaceChunksInBuffer_UnsortedChunks_test():
  chunks = [
    _BuildChunk( 1, 11, 1, 11, ')'),
    _BuildChunk( 1, 4, 1, 4, '(' )
  ]

  result_buffer = [ "CT<10 >> 2> ct" ]
  vimsupport.ReplaceChunksInBuffer( chunks, result_buffer, None )

  expected_buffer = [ "CT<(10 >> 2)> ct" ]
  eq_( expected_buffer, result_buffer )


class MockBuffer( ):
  """An object that looks like a vim.buffer object, enough for ReplaceChunk to
  generate a location list"""

  def __init__( self, lines, name, number ):
    self.lines = lines
    self.name = name
    self.number = number


  def __getitem__( self, index ):
    return self.lines[ index ]


  def __len__( self ):
    return len( self.lines )


  def __setitem__( self, key, value ):
    return self.lines.__setitem__( key, value )


@patch( 'ycm.vimsupport.GetBufferNumberForFilename', return_value=1 )
@patch( 'ycm.vimsupport.BufferIsVisible', return_value=True )
@patch( 'ycm.vimsupport.OpenFilename' )
@patch( 'ycm.vimsupport.EchoTextVimWidth' )
@patch( 'vim.eval' )
@patch( 'vim.command' )
def ReplaceChunks_SingleFile_Open_test( vim_command,
                                        vim_eval,
                                        echo_text_vim_width,
                                        open_filename,
                                        buffer_is_visible,
                                        get_buffer_number_for_filename ):

  chunks = [
    _BuildChunk( 1,1, 2, 1, 'replacement', 'single_file' )
  ]

  result_buffer = MockBuffer( [
    'line1',
    'line2',
    'line3',
  ], 'single_file', 1 )

  with patch( 'vim.buffers', [ None, result_buffer, None ] ):
    vimsupport.ReplaceChunks( chunks )

  # Ensure that we applied the replacement correctly
  eq_( result_buffer.lines, [
    'replacementline2',
    'line3',
  ] )

  # GetBufferNumberForFilename is called twice:
  #  - once to the check if we would require opening the file (so that we can
  #    raise a warning)
  #  - once whilst applying the changes
  get_buffer_number_for_filename.assert_has_calls( [
      call( 'single_file', False ),
      call( 'single_file', False ),
  ] )

  # BufferIsVisible is called twice for the same reasons as above
  buffer_is_visible.assert_has_calls( [
      call( 1 ),
      call( 1 ),
  ] )

  # we don't attempt to open any files
  open_filename.assert_not_called()

  # But we do set the quickfix list
  vim_eval.assert_has_calls( [
      call( 'setqflist( {0} )'.format( json.dumps( [ {
        'bufnr': 1,
        'filename': 'single_file',
        'lnum': 1,
        'col': 1,
        'text': 'replacement',
        'type': 'F'
      } ] ) ) ),
  ] )
  vim_command.assert_has_calls( [
      call( 'copen 5' )
  ] )

  # And it is ReplaceChunks that prints the message showing the number of
  # changes
  echo_text_vim_width.assert_has_calls( [
      call( 'Applied 1 changes' ),
  ] )


@patch( 'ycm.vimsupport.GetBufferNumberForFilename', side_effect=[ -1, -1, 1 ] )
@patch( 'ycm.vimsupport.BufferIsVisible', side_effect=[ False, False, True ] )
@patch( 'ycm.vimsupport.OpenFilename' )
@patch( 'ycm.vimsupport.EchoTextVimWidth' )
@patch( 'ycm.vimsupport.Confirm', return_value=True )
@patch( 'vim.eval', return_value=10 )
@patch( 'vim.command' )
def ReplaceChunks_SingleFile_NotOpen_test( vim_command,
                                           vim_eval,
                                           confirm,
                                           echo_text_vim_width,
                                           open_filename,
                                           buffer_is_visible,
                                           get_buffer_number_for_filename ):

  chunks = [
    _BuildChunk( 1,1, 2, 1, 'replacement', 'single_file' )
  ]

  result_buffer = MockBuffer( [
    'line1',
    'line2',
    'line3',
  ], 'single_file', 1 )

  with patch( 'vim.buffers', [ None, result_buffer, None ] ):
    vimsupport.ReplaceChunks( chunks )

  # We checked if it was OK to open the file
  confirm.assert_has_calls( [
    call( 'The requested operation will apply changes to 1 files '
          'which are not currently open. This will therefore open '
          '1 new splits in the current window. '
          'Do you wish to continue?' )
  ] )

  # Ensure that we applied the replacement correctly
  eq_( result_buffer.lines, [
    'replacementline2',
    'line3',
  ] )

  # GetBufferNumberForFilename is called 3 times. The return values are set in
  # the @patch call above:
  #  - once to the check if we would require opening the file (so that we can
  #    raise a warning) (-1 return)
  #  - once whilst applying the changes (-1 return)
  #  - finally after calling OpenFilename (1 return)
  get_buffer_number_for_filename.assert_has_calls( [
      call( 'single_file', False ),
      call( 'single_file', False ),
      call( 'single_file', False ),
  ] )

  # BufferIsVisible is called 3 times for the same reasons as above, with the
  # return of each one
  buffer_is_visible.assert_has_calls( [
    call( -1 ),
    call( -1 ),
    call( 1 ),
  ] )

  # We open 'single_file' as expected.
  open_filename.assert_called_with( 'single_file', {
    'focus': False,
    'fix': True,
    'size': 10
  } )

  # And update the quickfix list
  vim_eval.assert_has_calls( [
    call( '&previewheight' ),
    call( 'setqflist( {0} )'.format( json.dumps( [ {
      'bufnr': 1,
      'filename': 'single_file',
      'lnum': 1,
      'col': 1,
      'text': 'replacement',
      'type': 'F'
    } ] ) ) ),
  ] )
  vim_command.assert_has_calls( [
    call( 'copen 5' )
  ] )

  # And it is ReplaceChunks that prints the message showing the number of
  # changes
  echo_text_vim_width.assert_has_calls( [
    call( 'Applied 1 changes' ),
  ] )


@patch( 'ycm.vimsupport.GetBufferNumberForFilename', side_effect=[ -1, -1, 1 ] )
@patch( 'ycm.vimsupport.BufferIsVisible', side_effect=[ False, False, True ] )
@patch( 'ycm.vimsupport.OpenFilename' )
@patch( 'ycm.vimsupport.EchoTextVimWidth' )
@patch( 'ycm.vimsupport.Confirm', return_value=False )
@patch( 'vim.eval', return_value=10 )
@patch( 'vim.command' )
def ReplaceChunks_User_Declines_To_Open_File_test(
                                           vim_command,
                                           vim_eval,
                                           confirm,
                                           echo_text_vim_width,
                                           open_filename,
                                           buffer_is_visible,
                                           get_buffer_number_for_filename ):

  # Same as above, except the user selects Cancel when asked if they should
  # allow us to open lots of (ahem, 1) file.

  chunks = [
    _BuildChunk( 1,1, 2, 1, 'replacement', 'single_file' )
  ]

  result_buffer = MockBuffer( [
    'line1',
    'line2',
    'line3',
  ], 'single_file', 1 )

  with patch( 'vim.buffers', [ None, result_buffer, None ] ):
    vimsupport.ReplaceChunks( chunks )

  # We checked if it was OK to open the file
  confirm.assert_has_calls( [
    call( 'The requested operation will apply changes to 1 files '
          'which are not currently open. This will therefore open '
          '1 new splits in the current window. '
          'Do you wish to continue?' )
  ] )

  # Ensure that buffer is not changed
  eq_( result_buffer.lines, [
    'line1',
    'line2',
    'line3',
  ] )

  # GetBufferNumberForFilename is called once. The return values are set in
  # the @patch call above:
  #  - once to the check if we would require opening the file (so that we can
  #    raise a warning) (-1 return)
  get_buffer_number_for_filename.assert_has_calls( [
      call( 'single_file', False ),
  ] )

  # BufferIsVisible is called 3 times for the same reasons as above, with the
  # return of each one
  buffer_is_visible.assert_has_calls( [
    call( -1 ),
  ] )

  # We don't attempt to open any files or update any quickfix list or anything
  # like that
  open_filename.assert_not_called()
  vim_eval.assert_not_called()
  vim_command.assert_not_called()
  echo_text_vim_width.assert_not_called()


@patch( 'ycm.vimsupport.GetBufferNumberForFilename', side_effect=[ -1, -1, 1 ] )
# Key difference is here: In the final check, BufferIsVisible returns False
@patch( 'ycm.vimsupport.BufferIsVisible', side_effect=[ False, False, False ] )
@patch( 'ycm.vimsupport.OpenFilename' )
@patch( 'ycm.vimsupport.EchoTextVimWidth' )
@patch( 'ycm.vimsupport.Confirm', return_value=True )
@patch( 'vim.eval', return_value=10 )
@patch( 'vim.command' )
def ReplaceChunks_User_Aborts_Opening_File_test(
                                           vim_command,
                                           vim_eval,
                                           confirm,
                                           echo_text_vim_width,
                                           open_filename,
                                           buffer_is_visible,
                                           get_buffer_number_for_filename ):

  # Same as above, except the user selects Abort or Quick during the
  # "swap-file-found" dialog

  chunks = [
    _BuildChunk( 1,1, 2, 1, 'replacement', 'single_file' )
  ]

  result_buffer = MockBuffer( [
    'line1',
    'line2',
    'line3',
  ], 'single_file', 1 )

  with patch( 'vim.buffers', [ None, result_buffer, None ] ):
    assert_that( calling( vimsupport.ReplaceChunks ).with_args( chunks ),
                 raises( RuntimeError,
                  'Unable to open file: single_file\nFixIt/Refactor operation '
                  'aborted prior to completion. Your files have not been '
                  'fully updated. Please use undo commands to revert the'
                  'applied changes.' ) )

  # We checked if it was OK to open the file
  confirm.assert_has_calls( [
    call( 'The requested operation will apply changes to 1 files '
          'which are not currently open. This will therefore open '
          '1 new splits in the current window. '
          'Do you wish to continue?' )
  ] )

  # Ensure that buffer is not changed
  eq_( result_buffer.lines, [
    'line1',
    'line2',
    'line3',
  ] )

  # We tried to open this file
  open_filename.assert_called_with( "single_file", {
    'focus': False,
    'fix': True,
    'size': 10
  } )
  vim_eval.assert_called_with( "&previewheight" )

  # But raised an exception before issuing the message at the end
  echo_text_vim_width.assert_not_called()


@patch( 'ycm.vimsupport.GetBufferNumberForFilename', side_effect=[
          22, # first_file (check)
          -1, # another_file (check)
          22, # first_file (apply)
          -1, # another_file (apply)
          19, # another_file (check after open)
        ] )
@patch( 'ycm.vimsupport.BufferIsVisible', side_effect=[
          True,  # first_file (check)
          False, # second_file (check)
          True,  # first_file (apply)
          False, # second_file (apply)
          True,  # side_effect (check after open)
        ] )
@patch( 'ycm.vimsupport.OpenFilename' )
@patch( 'ycm.vimsupport.EchoTextVimWidth' )
@patch( 'ycm.vimsupport.Confirm', return_value=True )
@patch( 'vim.eval', return_value=10 )
@patch( 'vim.command' )
def ReplaceChunks_MultiFile_Open_test( vim_command,
                                       vim_eval,
                                       confirm,
                                       echo_text_vim_width,
                                       open_filename,
                                       buffer_is_visible,
                                       get_buffer_number_for_filename ):

  # Chunks are split across 2 files, one is already open, one isn't

  chunks = [
    _BuildChunk( 1,1, 2, 1, 'first_file_replacement ', '1_first_file' ),
    _BuildChunk( 2,1, 2, 1, 'second_file_replacement ', '2_another_file' ),
  ]

  first_file = MockBuffer( [
    'line1',
    'line2',
    'line3',
  ], '1_first_file', 22 )
  another_file = MockBuffer( [
    'another line1',
    'ACME line2',
  ], '2_another_file', 19 )

  vim_buffers = [ None ] * 23
  vim_buffers[ 22 ] = first_file
  vim_buffers[ 19 ] = another_file

  with patch( 'vim.buffers', vim_buffers ):
    vimsupport.ReplaceChunks( chunks )

  # We checked if it was OK to open the file
  confirm.assert_has_calls( [
    call( 'The requested operation will apply changes to 1 files '
          'which are not currently open. This will therefore open '
          '1 new splits in the current window. '
          'Do you wish to continue?' )
  ] )

  # Ensure that buffers are updated
  eq_( another_file.lines, [
    'another line1',
    'second_file_replacement ACME line2',
  ] )
  eq_( first_file.lines, [
    'first_file_replacement line2',
    'line3',
  ] )

  # We open '2_another_file' as expected.
  open_filename.assert_called_with( '2_another_file', {
    'focus': False,
    'fix': True,
    'size': 10
  } )

  # And update the quickfix list with each entry
  vim_eval.assert_has_calls( [
    call( '&previewheight' ),
    call( 'setqflist( {0} )'.format( json.dumps( [ {
      'bufnr': 22,
      'filename': '1_first_file',
      'lnum': 1,
      'col': 1,
      'text': 'first_file_replacement ',
      'type': 'F'
    }, {
      'bufnr': 19,
      'filename': '2_another_file',
      'lnum': 2,
      'col': 1,
      'text': 'second_file_replacement ',
      'type': 'F'
    } ] ) ) ),
  ] )
  vim_command.assert_has_calls( [
    call( 'copen 5' )
  ] )

  # And it is ReplaceChunks that prints the message showing the number of
  # changes
  echo_text_vim_width.assert_has_calls( [
    call( 'Applied 2 changes' ),
  ] )


def _BuildChunk( start_line,
                 start_column,
                 end_line,
                 end_column,
                 replacement_text, filepath='test_file_name' ):
  return {
    'range': {
      'start': {
        'filepath': filepath,
        'line_num': start_line,
        'column_num': start_column,
      },
      'end': {
        'filepath': filepath,
        'line_num': end_line,
        'column_num': end_column,
      },
    },
    'replacement_text': replacement_text
  }


@patch( 'vim.command' )
@patch( 'vim.current' )
def WriteToPreviewWindow_test( vim_current, vim_command ):
  vim_current.window.options.__getitem__ = MagicMock( return_value = True )

  vimsupport.WriteToPreviewWindow( "test" )

  vim_command.assert_has_calls( [
    call( 'silent! pclose!' ),
    call( 'silent! pedit! _TEMP_FILE_' ),
    call( 'silent! wincmd P' ),
    call( 'silent! wincmd p' ) ] )

  vim_current.buffer.__setitem__.assert_called_with(
      slice( None, None, None ), [ 'test' ] )

  vim_current.buffer.options.__setitem__.assert_has_calls( [
    call( 'buftype', 'nofile' ),
    call( 'swapfile', False ),
    call( 'modifiable', False ),
    call( 'modified', False ),
    call( 'readonly', True ),
  ], any_order = True )


@patch( 'vim.current' )
def WriteToPreviewWindow_MultiLine_test( vim_current ):
  vim_current.window.options.__getitem__ = MagicMock( return_value = True )
  vimsupport.WriteToPreviewWindow( "test\ntest2" )

  vim_current.buffer.__setitem__.assert_called_with(
      slice( None, None, None ), [ 'test', 'test2' ] )


@patch( 'vim.command' )
@patch( 'vim.current' )
def WriteToPreviewWindow_JumpFail_test( vim_current, vim_command ):
  vim_current.window.options.__getitem__ = MagicMock( return_value = False )

  vimsupport.WriteToPreviewWindow( "test" )

  vim_command.assert_has_calls( [
    call( 'silent! pclose!' ),
    call( 'silent! pedit! _TEMP_FILE_' ),
    call( 'silent! wincmd P' ),
    call( "echom 'test'" ),
  ] )

  vim_current.buffer.__setitem__.assert_not_called()
  vim_current.buffer.options.__setitem__.assert_not_called()


@patch( 'vim.command' )
@patch( 'vim.current' )
def WriteToPreviewWindow_JumpFail_MultiLine_test( vim_current, vim_command ):

  vim_current.window.options.__getitem__ = MagicMock( return_value = False )

  vimsupport.WriteToPreviewWindow( "test\ntest2" )

  vim_command.assert_has_calls( [
    call( 'silent! pclose!' ),
    call( 'silent! pedit! _TEMP_FILE_' ),
    call( 'silent! wincmd P' ),
    call( "echom 'test'" ),
    call( "echom 'test2'" ),
  ] )

  vim_current.buffer.__setitem__.assert_not_called()
  vim_current.buffer.options.__setitem__.assert_not_called()


def CheckFilename_test():
  assert_that(
    calling( vimsupport.CheckFilename ).with_args( None ),
    raises( RuntimeError, "'None' is not a valid filename" )
  )

  assert_that(
    calling( vimsupport.CheckFilename ).with_args( 'nonexistent_file' ),
    raises( RuntimeError,
            "filename 'nonexistent_file' cannot be opened. "
            "\[Errno 2\] No such file or directory: 'nonexistent_file'" )
  )

  assert_that( vimsupport.CheckFilename( __file__ ), none() )


def BufferIsVisibleForFilename_test():
  buffers = [
    {
      'number': 1,
      'filename': os.path.realpath( 'visible_filename' ),
      'window': 1
    },
    {
      'number': 2,
      'filename': os.path.realpath( 'hidden_filename' ),
    }
  ]

  with patch( 'vim.buffers', buffers ):
    eq_( vimsupport.BufferIsVisibleForFilename( 'visible_filename' ), True )
    eq_( vimsupport.BufferIsVisibleForFilename( 'hidden_filename' ), False )
    eq_( vimsupport.BufferIsVisibleForFilename( 'another_filename' ), False )


@patch( 'vim.command', side_effect = MockVimCommand )
def CloseBuffersForFilename_test( vim_command ):
  buffers = [
    {
      'number': 2,
      'filename': os.path.realpath( 'some_filename' ),
    },
    {
      'number': 5,
      'filename': os.path.realpath( 'some_filename' ),
    },
    {
      'number': 1,
      'filename': os.path.realpath( 'another_filename' )
    }
  ]

  with patch( 'vim.buffers', buffers ):
    vimsupport.CloseBuffersForFilename( 'some_filename' )

  vim_command.assert_has_calls( [
    call( 'silent! bwipeout! 2' ),
    call( 'silent! bwipeout! 5' )
  ], any_order = True )


@patch( 'vim.command' )
@patch( 'vim.current' )
def OpenFilename_test( vim_current, vim_command ):
  # Options used to open a logfile
  options = {
    'size': vimsupport.GetIntValue( '&previewheight' ),
    'fix': True,
    'watch': True,
    'position': 'end'
  }

  vimsupport.OpenFilename( __file__, options )

  vim_command.assert_has_calls( [
    call( '12split {0}'.format( __file__ ) ),
    call( "exec "
          "'au BufEnter <buffer> :silent! checktime {0}'".format( __file__ ) ),
    call( 'silent! normal G zz' ),
    call( 'silent! wincmd p' )
  ] )

  vim_current.buffer.options.__setitem__.assert_has_calls( [
    call( 'autoread', True ),
  ] )

  vim_current.window.options.__setitem__.assert_has_calls( [
    call( 'winfixheight', True )
  ] )
