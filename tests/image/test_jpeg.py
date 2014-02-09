# encoding: utf-8

"""
Test suite for docx.image.jpeg module
"""

from __future__ import absolute_import, print_function

import pytest

from mock import call

from docx.compat import BytesIO
from docx.image.constants import JPEG_MARKER_CODE
from docx.image.helpers import BIG_ENDIAN, StreamReader
from docx.image.jpeg import (
    _App0Marker, Jfif, _JfifMarkers, _Marker, _MarkerFactory, _MarkerFinder,
    _MarkerParser, _SofMarker
)

from ..unitutil import class_mock, initializer_mock, instance_mock


class DescribeJfif(object):

    def it_can_construct_from_a_jfif_stream(self, from_stream_fixture):
        # fixture ----------------------
        (stream_, blob_, filename_, _JfifMarkers_, px_width, px_height,
         horz_dpi, vert_dpi) = from_stream_fixture
        # exercise ---------------------
        jfif = Jfif.from_stream(stream_, blob_, filename_)
        # verify -----------------------
        _JfifMarkers_.from_stream.assert_called_once_with(stream_)
        assert isinstance(jfif, Jfif)
        assert jfif.px_width == px_width
        assert jfif.px_height == px_height
        assert jfif.horz_dpi == horz_dpi
        assert jfif.vert_dpi == vert_dpi

    # fixtures -------------------------------------------------------

    @pytest.fixture
    def blob_(self, request):
        return instance_mock(request, bytes)

    @pytest.fixture
    def filename_(self, request):
        return instance_mock(request, str)

    @pytest.fixture
    def from_stream_fixture(
            self, stream_, blob_, filename_, _JfifMarkers_, jfif_markers_):
        px_width, px_height = 111, 222
        horz_dpi, vert_dpi = 333, 444
        jfif_markers_.sof.px_width = px_width
        jfif_markers_.sof.px_height = px_height
        jfif_markers_.app0.horz_dpi = horz_dpi
        jfif_markers_.app0.vert_dpi = vert_dpi
        return (
            stream_, blob_, filename_, _JfifMarkers_, px_width, px_height,
            horz_dpi, vert_dpi
        )

    @pytest.fixture
    def _JfifMarkers_(self, request, jfif_markers_):
        _JfifMarkers_ = class_mock(request, 'docx.image.jpeg._JfifMarkers')
        _JfifMarkers_.from_stream.return_value = jfif_markers_
        return _JfifMarkers_

    @pytest.fixture
    def jfif_markers_(self, request):
        return instance_mock(request, _JfifMarkers)

    @pytest.fixture
    def stream_(self, request):
        return instance_mock(request, BytesIO)


class Describe_JfifMarkers(object):

    def it_can_construct_from_a_jfif_stream(self, from_stream_fixture):
        stream_, _MarkerParser_, _JfifMarkers__init_, marker_lst = (
            from_stream_fixture
        )
        jfif_markers = _JfifMarkers.from_stream(stream_)
        _MarkerParser_.from_stream.assert_called_once_with(stream_)
        _JfifMarkers__init_.assert_called_once_with(marker_lst)
        assert isinstance(jfif_markers, _JfifMarkers)

    # fixtures -------------------------------------------------------

    @pytest.fixture
    def app0_(self, request):
        return instance_mock(
            request, _App0Marker, marker_code=JPEG_MARKER_CODE.APP0
        )

    @pytest.fixture
    def eoi_(self, request):
        return instance_mock(
            request, _SofMarker, marker_code=JPEG_MARKER_CODE.EOI
        )

    @pytest.fixture
    def from_stream_fixture(
            self, stream_, _MarkerParser_, _JfifMarkers__init_, soi_, app0_,
            sof_, sos_):
        marker_lst = [soi_, app0_, sof_, sos_]
        return stream_, _MarkerParser_, _JfifMarkers__init_, marker_lst

    @pytest.fixture
    def _JfifMarkers__init_(self, request):
        return initializer_mock(request, _JfifMarkers)

    @pytest.fixture
    def marker_parser_(self, request, markers_all_):
        marker_parser_ = instance_mock(request, _MarkerParser)
        marker_parser_.iter_markers.return_value = markers_all_
        return marker_parser_

    @pytest.fixture
    def _MarkerParser_(self, request, marker_parser_):
        _MarkerParser_ = class_mock(request, 'docx.image.jpeg._MarkerParser')
        _MarkerParser_.from_stream.return_value = marker_parser_
        return _MarkerParser_

    @pytest.fixture
    def markers_all_(self, request, soi_, app0_, sof_, sos_, eoi_):
        return [soi_, app0_, sof_, sos_, eoi_]

    @pytest.fixture
    def sof_(self, request):
        return instance_mock(
            request, _SofMarker, marker_code=JPEG_MARKER_CODE.SOF0
        )

    @pytest.fixture
    def soi_(self, request):
        return instance_mock(
            request, _Marker, marker_code=JPEG_MARKER_CODE.SOI
        )

    @pytest.fixture
    def sos_(self, request):
        return instance_mock(
            request, _Marker, marker_code=JPEG_MARKER_CODE.SOS
        )

    @pytest.fixture
    def stream_(self, request):
        return instance_mock(request, BytesIO)


class Describe_Marker(object):

    def it_can_construct_from_a_stream_and_offset(self, from_stream_fixture):
        stream, marker_code, offset, _Marker__init_, length = (
            from_stream_fixture
        )
        marker = _Marker.from_stream(stream, marker_code, offset)
        _Marker__init_.assert_called_once_with(marker_code, offset, length)
        assert isinstance(marker, _Marker)

    # fixtures -------------------------------------------------------

    @pytest.fixture(params=[
        (JPEG_MARKER_CODE.SOI,  2,  0),
        (JPEG_MARKER_CODE.APP0, 4, 16),
    ])
    def from_stream_fixture(self, request, _Marker__init_):
        marker_code, offset, length = request.param
        bytes_ = b'\xFF\xD8\xFF\xE0\x00\x10'
        stream_reader = StreamReader(BytesIO(bytes_), BIG_ENDIAN)
        return stream_reader, marker_code, offset, _Marker__init_, length

    @pytest.fixture
    def _Marker__init_(self, request):
        return initializer_mock(request, _Marker)


class Describe_App0Marker(object):

    def it_can_construct_from_a_stream_and_offset(self, from_stream_fixture):
        (stream, marker_code, offset, _App0Marker__init_, length,
         density_units, x_density, y_density) = from_stream_fixture
        app0_marker = _App0Marker.from_stream(stream, marker_code, offset)
        _App0Marker__init_.assert_called_once_with(
            marker_code, offset, length, density_units, x_density, y_density
        )
        assert isinstance(app0_marker, _App0Marker)

    # fixtures -------------------------------------------------------

    @pytest.fixture
    def from_stream_fixture(self, request, _App0Marker__init_):
        bytes_ = b'\x00\x10JFIF\x00\x01\x01\x01\x00\x2A\x00\x18'
        stream_reader = StreamReader(BytesIO(bytes_), BIG_ENDIAN)
        marker_code, offset, length = JPEG_MARKER_CODE.APP0, 0, 16
        density_units, x_density, y_density = 1, 42, 24
        return (
            stream_reader, marker_code, offset, _App0Marker__init_, length,
            density_units, x_density, y_density
        )

    @pytest.fixture
    def _App0Marker__init_(self, request):
        return initializer_mock(request, _App0Marker)


class Describe_MarkerFactory(object):

    def it_constructs_the_appropriate_marker_object(self, call_fixture):
        marker_code, stream_, offset_, marker_cls_ = call_fixture
        marker = _MarkerFactory(marker_code, stream_, offset_)
        marker_cls_.from_stream.assert_called_once_with(
            stream_, marker_code, offset_
        )
        assert marker is marker_cls_.from_stream.return_value

    # fixtures -------------------------------------------------------

    @pytest.fixture(params=[
        JPEG_MARKER_CODE.APP0,
        JPEG_MARKER_CODE.SOF0,
        JPEG_MARKER_CODE.SOF7,
        JPEG_MARKER_CODE.SOS,
    ])
    def call_fixture(
            self, request, stream_, offset_, _App0Marker_, _SofMarker_,
            _Marker_):
        marker_code = request.param
        if marker_code == JPEG_MARKER_CODE.APP0:
            marker_cls_ = _App0Marker_
        elif marker_code in JPEG_MARKER_CODE.SOF_MARKER_CODES:
            marker_cls_ = _SofMarker_
        else:
            marker_cls_ = _Marker_
        return marker_code, stream_, offset_, marker_cls_

    @pytest.fixture
    def _App0Marker_(self, request):
        return class_mock(request, 'docx.image.jpeg._App0Marker')

    @pytest.fixture
    def _Marker_(self, request):
        return class_mock(request, 'docx.image.jpeg._Marker')

    @pytest.fixture
    def offset_(self, request):
        return instance_mock(request, int)

    @pytest.fixture
    def _SofMarker_(self, request):
        return class_mock(request, 'docx.image.jpeg._SofMarker')

    @pytest.fixture
    def stream_(self, request):
        return instance_mock(request, BytesIO)


class Describe_MarkerFinder(object):

    def it_can_construct_from_a_stream(self, from_stream_fixture):
        stream_, _MarkerFinder__init_ = from_stream_fixture
        marker_finder = _MarkerFinder.from_stream(stream_)
        _MarkerFinder__init_.assert_called_once_with(stream_)
        assert isinstance(marker_finder, _MarkerFinder)

    def it_can_find_the_next_marker_after_a_given_offset(self, next_fixture):
        marker_finder, start, expected_code_and_offset = next_fixture
        marker_code, segment_offset = marker_finder.next(start)
        assert (marker_code, segment_offset) == expected_code_and_offset

    # fixtures -------------------------------------------------------

    @pytest.fixture
    def from_stream_fixture(self, stream_, _MarkerFinder__init_):
        return stream_, _MarkerFinder__init_

    @pytest.fixture
    def _MarkerFinder__init_(self, request):
        return initializer_mock(request, _MarkerFinder)

    @pytest.fixture(params=[
        (0, JPEG_MARKER_CODE.SOI,   2),
        (1, JPEG_MARKER_CODE.APP0,  4),
        (2, JPEG_MARKER_CODE.APP0,  4),
        (3, JPEG_MARKER_CODE.EOI,  12),
        (4, JPEG_MARKER_CODE.EOI,  12),
        (6, JPEG_MARKER_CODE.EOI,  12),
        (8, JPEG_MARKER_CODE.EOI,  12),
    ])
    def next_fixture(self, request):
        start, marker_code, segment_offset = request.param
        bytes_ = b'\xFF\xD8\xFF\xE0\x00\x01\xFF\x00\xFF\xFF\xFF\xD9'
        stream_reader = StreamReader(BytesIO(bytes_), BIG_ENDIAN)
        marker_finder = _MarkerFinder(stream_reader)
        expected_code_and_offset = (marker_code, segment_offset)
        return marker_finder, start, expected_code_and_offset

    @pytest.fixture
    def stream_(self, request):
        return instance_mock(request, BytesIO)


class Describe_MarkerParser(object):

    def it_can_construct_from_a_jfif_stream(self, from_stream_fixture):
        stream_, StreamReader_, _MarkerParser__init_, stream_reader_ = (
            from_stream_fixture
        )
        marker_parser = _MarkerParser.from_stream(stream_)
        StreamReader_.assert_called_once_with(stream_, BIG_ENDIAN)
        _MarkerParser__init_.assert_called_once_with(stream_reader_)
        assert isinstance(marker_parser, _MarkerParser)

    def it_can_iterate_over_the_jfif_markers_in_its_stream(
            self, iter_markers_fixture):
        (marker_parser, stream_, _MarkerFinder_, marker_finder_,
         _MarkerFactory_, marker_codes, offsets,
         marker_lst) = iter_markers_fixture
        markers = [marker for marker in marker_parser.iter_markers()]
        _MarkerFinder_.from_stream.assert_called_once_with(stream_)
        assert marker_finder_.next.call_args_list == [
            call(0), call(2), call(20)
        ]
        assert _MarkerFactory_.call_args_list == [
            call(marker_codes[0], stream_, offsets[0]),
            call(marker_codes[1], stream_, offsets[1]),
            call(marker_codes[2], stream_, offsets[2]),
        ]
        assert markers == marker_lst

    # fixtures -------------------------------------------------------

    @pytest.fixture
    def app0_(self, request):
        return instance_mock(request, _App0Marker, segment_length=16)

    @pytest.fixture
    def eoi_(self, request):
        return instance_mock(request, _Marker, segment_length=0)

    @pytest.fixture
    def from_stream_fixture(
            self, stream_, StreamReader_, _MarkerParser__init_,
            stream_reader_):
        return stream_, StreamReader_, _MarkerParser__init_, stream_reader_

    @pytest.fixture
    def iter_markers_fixture(
            self, stream_reader_, _MarkerFinder_, marker_finder_,
            _MarkerFactory_, soi_, app0_, eoi_):
        marker_parser = _MarkerParser(stream_reader_)
        offsets = [2, 4, 22]
        marker_lst = [soi_, app0_, eoi_]
        marker_finder_.next.side_effect = [
            (JPEG_MARKER_CODE.SOI,  offsets[0]),
            (JPEG_MARKER_CODE.APP0, offsets[1]),
            (JPEG_MARKER_CODE.EOI,  offsets[2]),
        ]
        marker_codes = [
            JPEG_MARKER_CODE.SOI, JPEG_MARKER_CODE.APP0, JPEG_MARKER_CODE.EOI
        ]
        return (
            marker_parser, stream_reader_, _MarkerFinder_, marker_finder_,
            _MarkerFactory_, marker_codes, offsets, marker_lst
        )

    @pytest.fixture
    def _MarkerFactory_(self, request, soi_, app0_, eoi_):
        return class_mock(
            request, 'docx.image.jpeg._MarkerFactory',
            side_effect=[soi_, app0_, eoi_]
        )

    @pytest.fixture
    def _MarkerFinder_(self, request, marker_finder_):
        _MarkerFinder_ = class_mock(request, 'docx.image.jpeg._MarkerFinder')
        _MarkerFinder_.from_stream.return_value = marker_finder_
        return _MarkerFinder_

    @pytest.fixture
    def marker_finder_(self, request):
        return instance_mock(request, _MarkerFinder)

    @pytest.fixture
    def _MarkerParser__init_(self, request):
        return initializer_mock(request, _MarkerParser)

    @pytest.fixture
    def soi_(self, request):
        return instance_mock(request, _Marker, segment_length=0)

    @pytest.fixture
    def stream_(self, request):
        return instance_mock(request, BytesIO)

    @pytest.fixture
    def StreamReader_(self, request, stream_reader_):
        return class_mock(
            request, 'docx.image.jpeg.StreamReader',
            return_value=stream_reader_
        )

    @pytest.fixture
    def stream_reader_(self, request):
        return instance_mock(request, StreamReader)