from openerp import models, fields

class testwidget(models.Model):
    _name = 'testwidget'

    name = fields.Char()
    