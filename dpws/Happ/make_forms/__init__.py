from django import forms

_field_attrs = ['placeholder']
class_field_attrs = {
					'Char_Field': ('CharField', 'TextInput',), 
					'Integer_Field': ('IntegerField', 'NumberInput',),
					'Email_Field': ('EmailField','EmailInput',)
					}

class FormField:
	def __init__(self, field_name, field, label, max_length, widget,**kwargs):
		self.field_name = field_name
		self.field = field
		self.label = label
		self.max_length = max_length
		self.widget = widget
		self.nones = []
		
		for k,v in self:
			if v == None:
				self.nones.append(k)

		if len(kwargs) > 0:
			for attr_key, attr_value in kwargs.items():
				if attr_key in _field_attrs:
					continue
				else:
					kwargs.pop(attr_key, None)
			self.field_attrs = kwargs
		else:
			self.field_attrs = {"placeholder": "%s" %(self.field_name.replace('_', ' ').title())}

		self.delattr()
		#print(self.__dict__)

	def __iter__(self):
		for k,v in self.__dict__.items():
			yield k,v

	def delattr(self):
		for attr in self.nones:
			delattr(self, attr)

	def _label_(self, label):
		_label = None
		if label is None:
			_label = self.field_name.replace('_', ' ').title()
		else:
			_label = label
		return _label

	def _widget_(self, cls, widget):
		_widget = None
		if widget is None:
			_widget = cls._widget
		else:
			_widget = widget
		return _widget


	def _max_length_(self, cls, max_length=None):
		_max_length = None
		if 'max_length' in cls.__init__.__code__.co_varnames:
			if max_length is None:
				_max_length = 100
			else:
				_max_length = max_length

		return _max_length
	
class MetaFieldClass(type):
	def __new__(mcs, name, bases, attrs):
		field = None
		new_class = super(MetaFieldClass, mcs).__new__(mcs, name, bases, attrs)
		for base in new_class.__mro__:
			if base.__name__ in class_field_attrs:
				field = class_field_attrs[base.__name__]

		if field is not None:
			new_class._field = field[0]
			new_class._widget = field[1]
		return new_class

class Field(FormField, metaclass=MetaFieldClass): pass

class Char_Field(Field):

	def __init__(self, field_name, label=None, max_length=None, widget=None, **kwargs):
		self.field = self._field
		self.field_name = field_name
		self.label = self._label_(label)
		self.max_length = self._max_length_(self, max_length)
		self.widget = self._widget_(self, widget)

		super(Char_Field, self).__init__(self.field_name, self.field, self.label, self.max_length, self.widget, **kwargs)

class Integer_Field(Field):

	def __init__(self, field_name, label=None, widget=None, **kwargs):
		self.field = self._field
		self.field_name = field_name
		self.label = self._label_(label)
		self.widget = self._widget_(self, widget)
		self.max_length = self._max_length_(self)

		super(Integer_Field, self).__init__(self.field_name, self.field, self.label, self.max_length, self.widget, **kwargs)

class Email_Field(Field):
	
	def __init__(self, field_name, label=None, max_length=None, widget=None, **kwargs):
		self.field  = self._field
		self.field_name = field_name
		self.label = self._label_(label)
		self.widget = self._widget_(self, widget)
		self.max_length = self._max_length_(self, max_length)

		super(Email_Field, self).__init__(self.field_name, self.field, self.label, self.max_length, self.widget, **kwargs)

class make_form_str:
    def __init__(self, c_name, attrs):
        self.c_name = c_name
        self.attrs = attrs
        self.val = self.form(c_name, attrs)

    def form(self, c_name, attrs):
        vl_attrs = ''
        for attr in attrs:
            if hasattr(attr, 'max_length'):
                vl_attrs += '%s=forms.%s(label="%s", max_length=%d, widget=forms.%s(attrs=%s));' %(attr.field_name, attr.field, attr.label, attr.max_length, attr.widget, attr.field_attrs)
            else:
                vl_attrs += '%s=forms.%s(label="%s", widget=forms.%s(attrs=%s));' %(attr.field_name, attr.field, attr.label, attr.widget, attr.field_attrs)
        _val = "class %s (forms.Form): %s" %(c_name, vl_attrs)

        return _val

class Fill_Form_Field:
    def __init__(self, c_name, attrs):
        self.c_name = c_name
        self.attrs = []
        for attr in attrs:
        	if isinstance(attr, str):
        		self.attrs.append(Char_Field(attr))
        	if isinstance(attr, FormField):
        		self.attrs.append(attr)

    def fill(self):
        mf = make_form_str(self.c_name, self.attrs)
        return mf
    
def exec_obj_as_global(obj):
	e_run = obj.val+' global %s' %(obj.c_name)
	exec(e_run)

Global_Dict_Obj = globals()
