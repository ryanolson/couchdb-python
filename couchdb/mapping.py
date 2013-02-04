import inspect
from schematics.models import Model
from schematics.types import *
from schematics.types.compound import ListType
from schematics.validation import validate_instance

class Document(Model):
    doc_type = StringType()

    def __init__(self, id=None, *args, **kwargs):
        super(Document, self).__init__(*args,**kwargs)
        if id:
           self.id = id
        self.doc_type = self.__class__.__name__

    def __repr__(self):
        return '<%s %r@%r %r>' % (type(self).__name__, self.id, self.rev,
                                  dict([(k, v) for k, v in self._data.items()
                                        if k not in ('_id', '_rev')]))

    def _get_id(self):
        if hasattr(self._data, 'id'): # When data is client.Document
            return self._data.id
        return self._data.get('_id')
    def _set_id(self, value):
        if self.id is not None:
            raise AttributeError('id can only be set on new documents')
        self._data['_id'] = value
    id = property(_get_id, _set_id, doc='The document ID')

    @property
    def rev(self):
        """The document revision.
        :rtype: basestring
        """
        if hasattr(self._data, 'rev'): # When data is client.Document
            return self._data.rev
        return self._data.get('_rev')

    def items(self):
        retval = []
        if self.id is not None:
            retval.append(('_id', self.id))
            if self.rev is not None:
                retval.append(('_rev', self.rev))
        for name, value in self._fields.items():
            if name not in ('_id', '_rev'):
                retval.append((name,self._data[value.field_name]))
        return retval

    @classmethod
    def wrap(cls, data):
        instance = cls()
        instance._data = data
        return instance

    @classmethod
    def load(cls, db, id):
        """Load a specific document from the given database.
        
        :param db: the `Database` object to retrieve the document from
        :param id: the document ID
        :return: the `Document` instance, or `None` if no document with the
                 given ID was found
        """
        doc = db.get(id)
        if doc is None:
            return None
        return cls.wrap(doc)

    def store(self, db, validate=True):
        """Store the document in the given database."""
        results = validate_instance(self)
        if results.tag == 'OK':
           db.save(self._data)
        else:
           raise Exception
        return self

    @classmethod
    def query(cls, db, map_fun, reduce_fun, language='javascript', **options):
        """Execute a CouchDB temporary view and map the result values back to
        objects of this mapping.
        
        Note that by default, any properties of the document that are not
        included in the values of the view will be treated as if they were
        missing from the document. If you want to load the full document for
        every row, set the ``include_docs`` option to ``True``.
        """
        return db.query(map_fun, reduce_fun=reduce_fun, language=language,
                        wrapper=cls._wrap_row, **options)

    @classmethod
    def view(cls, db, viewname, **options):
        """Execute a CouchDB named view and map the result values back to
        objects of this mapping.
        
        Note that by default, any properties of the document that are not
        included in the values of the view will be treated as if they were
        missing from the document. If you want to load the full document for
        every row, set the ``include_docs`` option to ``True``.
        """
        return db.view(viewname, wrapper=cls._wrap_row, **options)

    @classmethod
    def _wrap_row(cls, row):
        doc = row.get('doc')
        if doc is not None:
            return cls.wrap(doc)
        data = row['value']
        data['_id'] = row['id']
        return cls.wrap(data)

class BasicField(object):
    def __init__(self, *args, **kwargs):
        if 'name' in kwargs:
           kwargs['field_name'] = kwargs['name']
           del kwargs['name']
        keys = sorted(kwargs.keys())
        for kw in keys:
           print kw, ":", kwargs[kw]
        super(BasicField, self).__init__()

    def _to_json(self, value):
        return self.for_json(value)

    def _to_python(self, value):
        return self.for_python(value)

class TextField(BasicField,StringType):
    pass

class FloatField(BasicField,FloatType):
    pass

class IntegerField(BasicField,IntType):
    pass

class LongField(BasicField,FloatType):
    pass

class BooleanField(BasicField,BooleanType):
    pass

class DecimalField(BasicField,DecimalType):
    pass 

class DateField(BasicField,DateTimeType):
    pass

class DateTimeField(BasicField,DateTimeType):
    pass

class TimeField(BasicField,DateTimeType):
    pass

class DictField(BasicField,DictType):
    pass

class ListField(ListType):
    def __init__(self, field, **kwargs):
        if 'name' in kwargs:
           kwargs['field_name'] = kwargs['name']
           del kwargs['name']
        keys = sorted(kwargs.keys())
        for kw in keys:
           print kw, ":", kwargs[kw]
        field_instance = field
        if inspect.isclass(field):
           if issubclass(field, BaseType):
              field_instance = field()
        super(ListField, self).__init__(field_instance, **kwargs)
        

