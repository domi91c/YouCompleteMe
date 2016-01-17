# Copyright (C) 2016 YouCompleteMe Contributors
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

from ycm.test_utils import MockVimModule
MockVimModule()

import json
from mock import patch, call
from ycm.client.command_request import CommandRequest


class GoToResponse_QuickFix_test:
  """This class tests the generation of QuickFix lists for GoTo responses which
  return multiple locations, such as the Python completer and JavaScript
  completer. It mostly proves that we use 1-based indexing for the column
  number."""

  def setUp( self ):
    self._request = CommandRequest( [ 'GoToTest' ] )


  def tearDown( self ):
    self._request = None


  def GoTo_EmptyList_test( self ):
    self._CheckGoToList( [], [] )


  def GoTo_SingleItem_List_test( self ):
    self._CheckGoToList( [ {
      'filepath':     'dummy_file',
      'line_num':     10,
      'column_num':   1,
      'description': 'this is some text',
    } ], [ {
      'filename':    'dummy_file',
      'text':        'this is some text',
      'lnum':        10,
      'col':         1
    } ] )


  def GoTo_MultiItem_List_test( self ):
    self._CheckGoToList( [ {
      'filepath':     'dummy_file',
      'line_num':     10,
      'column_num':   1,
      'description': 'this is some other text',
    }, {
      'filepath':     'dummy_file2',
      'line_num':     1,
      'column_num':   21,
      'description': 'this is some text',
    } ], [ {
      'filename':    'dummy_file',
      'text':        'this is some other text',
      'lnum':        10,
      'col':         1
    }, {
      'filename':    'dummy_file2',
      'text':        'this is some text',
      'lnum':        1,
      'col':         21
    } ] )


  @patch( 'vim.eval' )
  def _CheckGoToList( self, completer_response, expected_qf_list, vim_eval ):
    self._request._response = completer_response

    self._request.RunPostCommandActionsIfNeeded()

    vim_eval.assert_has_calls( [
      call( 'setqflist( {0} )'.format( json.dumps( expected_qf_list ) ) ),
      call( 'youcompleteme#OpenGoToList()' ),
    ] )


class Response_Detection_test:

  def BasicResponse_test( self ):
    def _BasicResponseTest( command, response ):
      with patch( 'vim.command' ) as vim_command:
        request = CommandRequest( [ command ] )
        request._response = response
        request.RunPostCommandActionsIfNeeded()
        vim_command.assert_called_with( "echom '{0}'".format( response ) )

    tests = [
      [ 'AnythingYouLike',        True ],
      [ 'GoToEvenWorks',          10 ],
      [ 'FixItWorks',             'String!' ],
      [ 'and8434fd andy garbag!', 10.3 ],
    ]

    for test in tests:
      yield _BasicResponseTest, test[ 0 ], test[ 1 ]


  def FixIt_Response_Empty_test( self ):
    # Ensures we recognise and handle fixit responses which indicate that there
    # are no fixits available
    def EmptyFixItTest( command ):
      with patch( 'ycm.vimsupport.ReplaceChunks' ) as replace_chunks:
        with patch( 'ycm.vimsupport.EchoText' ) as echo_text:
          request = CommandRequest( [ command ] )
          request._response = {
            'fixits': []
          }
          request.RunPostCommandActionsIfNeeded()

          echo_text.assert_called_with( 'No fixits found for current line' )
          replace_chunks.assert_not_called()

    for test in [ 'FixIt', 'Refactor', 'GoToHell', 'any_old_garbade!!!21' ]:
      yield EmptyFixItTest, test


  def FixIt_Response_test( self ):
    # Ensures we recognise and handle fixit responses with some dummy chunk data
    def FixItTest( command, response, chunks ):
      with patch( 'ycm.vimsupport.ReplaceChunks' ) as replace_chunks:
        with patch( 'ycm.vimsupport.EchoText' ) as echo_text:
          request = CommandRequest( [ command ] )
          request._response = response
          request.RunPostCommandActionsIfNeeded()

          replace_chunks.assert_called_with( chunks )
          echo_text.assert_not_called()

    basic_fixit = {
      'fixits': [ {
        'chunks': [ {
          'dummy chunk contents': True
        } ]
      } ]
    }
    basic_fixit_chunks = basic_fixit[ 'fixits' ][ 0 ][ 'chunks' ]

    multi_fixit = {
      'fixits': [ {
        'chunks': [ {
          'dummy chunk contents': True
        } ]
      }, {
        'additional fixits are ignored currently': True
      } ]
    }
    multi_fixit_first_chunks = multi_fixit[ 'fixits' ][ 0 ][ 'chunks' ]

    tests = [
      [ 'AnythingYouLike',        basic_fixit, basic_fixit_chunks ],
      [ 'GoToEvenWorks',          basic_fixit, basic_fixit_chunks ],
      [ 'FixItWorks',             basic_fixit, basic_fixit_chunks ],
      [ 'and8434fd andy garbag!', basic_fixit, basic_fixit_chunks ],
      [ 'additional fixits ignored', multi_fixit, multi_fixit_first_chunks ],
    ]

    for test in tests:
      yield FixItTest, test[ 0 ], test[ 1 ], test[ 2 ]


  def Message_Response_test( self ):
    # Ensures we correctly recognise and handle responses with a message to show
    # to the user

    def MessageTest( command, message ):
      with patch( 'ycm.vimsupport.EchoText' ) as echo_text:
        request = CommandRequest( [ command ] )
        request._response = { 'message': message }
        request.RunPostCommandActionsIfNeeded()
        echo_text.assert_called_with( message )

    tests = [
      [ '___________', 'This is a message' ],
      [ '',            'this is also a message' ],
      [ 'GetType',     'std::string' ],
    ]

    for test in tests:
      yield MessageTest, test[ 0 ], test[ 1 ]


  def Detailed_Info_test( self ):
    # Ensures we correctly detect and handle detailed_info responses which are
    # used to display information in the preview window

    def DetailedInfoTest( command, info ):
      with patch( 'ycm.vimsupport.WriteToPreviewWindow' ) as write_to_preview:
        request = CommandRequest( [ command ] )
        request._response = { 'detailed_info': info }
        request.RunPostCommandActionsIfNeeded()
        write_to_preview.assert_called_with( info )

    tests = [
      [ '___________', 'This is a message' ],
      [ '',            'this is also a message' ],
      [ 'GetDoc',      'std::string\netc\netc' ],
    ]

    for test in tests:
      yield DetailedInfoTest, test[ 0 ], test[ 1 ]


  def GoTo_Single_test( self ):
    # Ensures we handle any unknown type of response as a GoTo response

    def GoToTest( command, response ):
      with patch( 'ycm.vimsupport.JumpToLocation' ) as jump_to_location:
        request = CommandRequest( [ command ] )
        request._response = response
        request.RunPostCommandActionsIfNeeded()
        jump_to_location.assert_called_with(
            response[ 'filepath' ],
            response[ 'line_num' ],
            response[ 'column_num' ] )

    def GoToListTest( command, response ):
      # Note: the detail of these called are tested by
      # GoToResponse_QuickFix_test, so here we just check that the right call is
      # made
      with patch( 'ycm.vimsupport.SetQuickFixList' ) as set_qf_list:
        with patch( 'vim.eval' ) as vim_eval:
          request = CommandRequest( [ command ] )
          request._response = response
          request.RunPostCommandActionsIfNeeded()
          assert set_qf_list.called
          assert vim_eval.called

    basic_goto = {
      'filepath': 'test',
      'line_num': 10,
      'column_num': 100,
    }

    tests = [
      [ GoToTest,     'AnythingYouLike', basic_goto ],
      [ GoToTest,     'GoTo',            basic_goto ],
      [ GoToTest,     'FindAThing',      basic_goto ],
      [ GoToTest,     'FixItGoto',       basic_goto ],
      [ GoToListTest, 'AnythingYouLike', [ basic_goto ] ],
      [ GoToListTest, 'GoTo',            []  ],
      [ GoToListTest, 'FixItGoto',       [ basic_goto, basic_goto ] ],
    ]

    for test in tests:
      yield test[ 0 ], test[ 1 ], test[ 2 ]
