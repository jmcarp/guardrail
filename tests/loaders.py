# -*- coding: utf-8 -*-

class LoaderMixin(object):

    def test_default_column(self):
        loader = self.Loader(self.Schema)
        assert loader.column == self.primary

    def test_override_column(self):
        loader = self.Loader(self.Schema, column=self.secondary)
        assert loader.column == self.secondary

    def test_result_found(self):
        loader = self.Loader(self.Schema)
        assert loader(id=self.record.id) == self.record

    def test_result_found_override_kwarg(self):
        loader = self.Loader(self.Schema, kwarg='pk')
        assert loader(pk=self.record.id) == self.record

    def test_no_result_found(self):
        loader = self.Loader(self.Schema)
        assert loader(id=self.record.id + 1) is None
