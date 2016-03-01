from openerp.osv import osv, fields

class testapi(osv.osv):
    _name = 'testapi'
    _description = "Test API"
    _order = 'id'

    _columns = {
            'name': fields.char(size=256, string='Name', ),
            'description': fields.text(string='Description'  ),
            'datestart': fields.date('Date'),
            'amount':fields.float('Amount'),
            
    }
    

testapi()
